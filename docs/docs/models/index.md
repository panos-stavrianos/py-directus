# Usage

Subclass the `DirectusModel` to define your custom `pydantic` models.

```python
from typing import List, Union

from py_directus.models import DirectusModel

class Item(DirectusModel):
    name: str
    description: Union[str, None] = None
    price: float
    tax: Union[float, None] = None
    tags: List[str] = []

    class Config:
        collection = "item"

```

> In case you don't define the `collection` attribute in the `Config` class, 
> py-directus will use a munged version of the class name: `CamelCase` becomes `camel_case`.
