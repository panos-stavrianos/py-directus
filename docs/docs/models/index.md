# Declaration

Subclass the `DirectusModel` to define your custom `pydantic` models.

```python
from typing import List, Union

from pydantic import ConfigDict
from py_directus.models import DirectusModel

class Item(DirectusModel):
    name: str
    description: Union[str, None] = None
    price: float
    tax: Union[float, None] = None
    tags: List[str] = []

    model_config = ConfigDict(collection="items")

```

> Old implementation. It is still supported, but **deprecated**.

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

!!! info "Note"
    In case you don't define the `collection` attribute in the `model_config` attribute (or `Config` class), 
    py-directus will use a munged version of the class name: `CamelCase` becomes `camel_case`.
