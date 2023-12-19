from datetime import datetime
from typing import Union, Tuple

try:
    import human_readable
except ImportError:
    human_readable = None

from typing_extensions import Annotated

from pydantic.functional_validators import AfterValidator


class ModelDateTime(datetime):
    """
    """

    DATE_FORMAT: str = "%d/%m/%Y"
    TIME_FORMAT: Tuple[str, str] = ("%H:%M:%S", "%H:%M")
    DATETIME_FORMAT: Tuple[str, str] = ("%d/%m/%Y %H:%M:%S", "%d/%m/%Y %H:%M")

    # Pydantic field data type
    field = Annotated[
        datetime,
        AfterValidator(lambda v: ModelDateTime.fromisoformat(v.isoformat())),
    ]

    def str_only_date(self):
        return self.strftime(self.DATE_FORMAT)

    def str_only_time(self, with_seconds: bool=False):
        if with_seconds:
            return self.strftime(self.TIME_FORMAT[0])
        return self.strftime(self.TIME_FORMAT[1])

    def str_date_time(self, with_seconds: bool=False):
        if with_seconds:
            return self.strftime(self.DATETIME_FORMAT[0])
        return self.strftime(self.DATETIME_FORMAT[1])

    if human_readable:
        def str_human_readable(self):
            return human_readable.date_time(ModelDateTime.now() - self)
