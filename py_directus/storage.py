import os
import pathlib
import errno
import platformdirs
import aiofiles

from py_directus.utils import get_random_string


class SuspiciousFileOperation(Exception):
    """
    A Suspicious filesystem operation was attempted.
    
    Origin: https://github.com/django/django/blob/3.2.23/django/core/files/storage.py
    """
    pass


def _validate_file_name(name, allow_relative_path=False):
    """
    Origin: https://github.com/django/django/blob/3.2.23/django/core/files/utils.py
    """

    # Remove potentially dangerous names
    if os.path.basename(name) in {'', '.', '..'}:
        raise SuspiciousFileOperation(f"Could not derive file name from '{name}'")

    if allow_relative_path:
        # Use PurePosixPath() because this branch is checked only in
        # FileField.generate_filename() where all file paths are expected to be
        # Unix style (with forward slashes).
        path = pathlib.PurePosixPath(name)
        if path.is_absolute() or ".." in path.parts:
            raise SuspiciousFileOperation(
                f"Detected path traversal attempt in '{name}'"
            )
    elif name != os.path.basename(name):
        raise SuspiciousFileOperation(f"File name '{name}' includes path elements")

    return name


def _get_alternative_name(file_root, file_ext):
    """
    Return an alternative filename, by adding an underscore and a random 7
    character alphanumeric string (before the file extension, if one
    exists) to the filename.

    Origin: https://github.com/django/django/blob/3.2.23/django/core/files/storage.py
    """
    return f"{file_root}_{get_random_string(7)}{file_ext}"


def _get_available_name(name, max_length=None):
    """
    Return a filename that's free on the target storage system and
    available for new content to be written to.

    Origin: https://github.com/django/django/blob/3.2.23/django/core/files/storage.py
    """

    name = str(name).replace('\\', '/')
    dir_name, file_name = os.path.split(name)

    if ".." in pathlib.PurePath(dir_name).parts:
        raise SuspiciousFileOperation(f"Detected path traversal attempt in '{dir_name}'")

    _validate_file_name(file_name)
    file_root, file_ext = os.path.splitext(file_name)

    # If the filename already exists, generate an alternative filename
    # until it doesn't exist.
    # Truncate original name if required, so the new filename does not
    # exceed the max_length.
    while os.path.exists(_get_default_downloads_path(name)) or (max_length and len(name) > max_length):
        # file_ext includes the dot.
        name = os.path.join(dir_name, _get_alternative_name(file_root, file_ext))

        if max_length is None:
            continue

        # Truncate file_root if max_length exceeded.
        truncation = len(name) - max_length

        if truncation > 0:
            file_root = file_root[:-truncation]

            # Entire file_root was truncated in attempt to find an available filename.
            if not file_root:
                raise SuspiciousFileOperation(
                    f"Storage can not find an available filename for '{name}'. "
                    f"Please make sure that you allows sufficient 'max_length'."
                )
            name = os.path.join(dir_name, _get_alternative_name(file_root, file_ext))

    return name


def _get_default_downloads_path(filename: str):
    """
    """

    path = os.path.join(platformdirs.user_downloads_dir(), "py_directus")

    # Make directories
    try:
        os.makedirs(path)
    except OSError as exc:
        if exc.errno == errno.EEXIST and os.path.isdir(path):
            pass
        else:
            raise

    # Append the file name
    return os.path.join(path, filename)


async def save_file(filename: str, content: bytes) -> str:
    """
    """

    name = _get_available_name(filename)
    full_path = _get_default_downloads_path(name)

    # Create file from received data

    while True:
        try:
            # Open for exclusive creation (as bytes)
            async with aiofiles.open(full_path, 'xb') as f:
                await f.write(content)
        except FileExistsError:
            # A new name is needed if the file exists.
            name = _get_available_name(name)
            full_path = _get_default_downloads_path(name)
        else:
            # Everything went OK, so get out of the infinite loop
            break

    # Ensure that the name returned from the storage system is still valid.
    _validate_file_name(name, allow_relative_path=True)

    return name
