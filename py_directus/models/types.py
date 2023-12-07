from datetime import datetime

from typing_extensions import Annotated

from pydantic.functional_validators import AfterValidator


def convert_datetime_to(dt: datetime) -> str:
    dt_format = "%d/%m/%Y %H:%M:%S"
    return dt.strftime(dt_format)


MyDatetime = Annotated[datetime, AfterValidator(convert_datetime_to)]
