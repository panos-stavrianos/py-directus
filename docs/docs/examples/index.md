# Usage

!!! warning "Note"
    Examples are not included with the `pypi` package, so you will have to download them separately and execute in a virtual environment.

## Execution

Run individual examples as such:

```shell
python -m examples.<example_file_name>
```

## Currently available

- request

Retrieves a user record from `Directus` whith the collection being defined as a string and as a `Pydantic` model class.

- request_two

Same as the `request` example, but uses the `Directus` client as context manager.

- filters

A demonstration of the capabilities that the `F` provides.

- files

Upload a file from local storage to `Directus` and retireve a list of currently saved files.

- file_download

Download a file from `Directus` by its id.
