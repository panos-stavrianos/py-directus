# py-directus

## Requirements:

- Support for Directus >=v10
- Full utilization of pydantic models (pydantic >=v2), but primitive dict support is also required
- FastApi Support
- Fully asynchronous (perhaps using aiohttp)
- Sync support (using requests) maybe? If we find a way to do it without code duplication
- Support for all (at least most) Directus API endpoints, including file upload and download
- Support for all Directus API filters
- Support for login using email and password, token, and api key(static token)
- Refresh token support
- Exception handling
- Support for GraphQL
- Realtime support (websockets), for start, just receiving events not creating and updating
- Websocket Relay (proxy). A small websocket server that will act as a proxy between the client and the Directus server.
  This will allow us to use the realtime functionality without having to expose the Directus server to the internet.
- Pypi package
- Documentation
- Tests

## Usage examples

Most of the functionality is from an older project of
mine, [DirectusPyWrapper](https://github.com/panos-stavrianos/DirectusPyWrapper).
This project will be rewrite of that project, but with a lot more functionality and better code.

### Installation

```bash
pip install py-directus
```

### Pydantic models

Regular pydantic models can be used to represent the data returned from the Directus API. The only requirement is that
the model has a `collection` attribute that matches the collection name in Directus.

```python
from pydantic import BaseModel
from typing import Optional


class Language(BaseModel):
    code: Optional[str] = None
    name: Optional[str] = None
    icon: Optional[str] = None

    class Config:
        collection = 'languages'
        ignore_extra = True
```

### Initialization

```python
from py_directus import Directus

url = 'https://directus.example.com'
token = 'my_token'
directus = Directus(url=url, token=token)

# or
directus = Directus(url=url, email='my_email', password='my_password')

# or
directus = Directus(url=url)

# and maybe later login
directus.login(email='my_email', password='my_password')
# or 
directus.login(token=token)
```

### Select collection

Either use the `items` or the `collection` method.

Both methods return a `DirectusRequest` object that contains the
`filters`, `sort`, `limit`, `offset` and the `read`, `create`, `update`, `delete` etc.

Items method:

```python
directus.items('languages')
```

Collection method:

```python
import Language
from models

directus.collection(Language)
```

> Implementation Changes

```python
directus.collection('languages')

# OR

import Language
from models

directus.collection(Language)
```

### Retrieve items

If you have used the `items` method, you get a dict or a list of dicts. If you have used the `collection` method, you
get a pydantic model or a list of pydantic models.

Also, you can use the `read` method to retrieve items. The `read` method returns a `DirectusResponse` object that
contains the `items` and `item` properties. The `items` property is a list of items and the `item` property is the first
item of the list.

```python
# dict
languages: list[dict] = directus.items('languages').read().items
first_language: dict = directus.items('languages').read().item

# pydantic model
languages: list[Language] = directus.collection(Language).read().items
first_language: Language = directus.collection(Language).read().item
```

> Implementation Changes

```python
# dict
languages: list[dict] = directus.collection('languages').read().items
first_language: dict = directus.collection('languages').read().item

# pydantic model
languages: list[Language] = directus.collection(Language).read().items
first_language: Language = directus.collection(Language).read().item
```

#### Extra methods for retrieving items

You can use:

- `items` to retrieve a list of items (list of dicts or list of pydantic models)
- `item` to retrieve the first item (dict or pydantic model)
- `items_as_dict` to retrieve a list of items as a dict
- `item_as_dict` to retrieve the first item as a dict
- `items_as_model` to retrieve a list of items as a pydantic model (Requires a pydantic model to be passed as an
  argument)
- `item_as_model` to retrieve the first item as a pydantic model (Requires a pydantic model to be passed as an argument)

### Get ME!

```python
from models import User

from py_directus import DirectusUser

user: DirectusUser = directus.me()
user: dict = directus.me_as_dict()

# or if you have overridden the User model
user: User = directus.me(User)

# you can also declare the User model in the Directus initialization
directus = Directus(url=url, user_model=User)
```

> Implementation Changes

```python
from models import User

from py_directus import DirectusUser

user: DirectusUser = directus.me().item
user: dict = directus.me().item_as_dict

# or if you have overridden the User model
user: User = directus.me(User).item

# you can also declare the User model in the Directus initialization
directus = Directus(url=url, user_model=User)
```

### Roles

Get all roles

```python
from py_directus import DirectusRole

roles: list[DirectusRole] = directus.roles()
```

> Implementation Changes

```python
from py_directus.models import DirectusRole

roles: list[DirectusRole] = directus.roles().items
```

### FastApi

Provide a `Depends` function to get a directus instance based on the request. Support for both Header and Cookie.

On not found, it will return a `HTTPException` with status code 401.

Additionally, we must provide a decorator `@assert_role([roles accepted])` to assert that the user has the required
role.

### Filters

Most of the filters functionality is already implemented. See docs for more info.

### Extra functionality

See at the directus [docs](https://docs.directus.io/reference/query.html) for more info.

- `fields`
- `count`
- `sort`
- `limit`
- `offset`
- `Aggregation & Grouping`
- `deep`
- `metadata (DEPRECATED)`
