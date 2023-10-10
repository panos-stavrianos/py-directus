# py-directus

> Under development

Documentation [here](https://panos-stavrianos.github.io/py-directus/)

## Run examples

```shell
python -m examples.{example_file_name}
```

### Multiple Users in the Same Session

You can use multiple users in the same session by creating a new Directus instance by passing the client object

```python
connection = httpx.Client()
directus1 = Directus(url, token=token, connection=connection)
directus2 = Directus(url, email=email, password=password, connection=connection)
```

## Collections

There are two ways to set a collection, either by passing the collection name as a string
or by passing the collection as a Pydantic model.

Using the `collection` method you can pass the collection name as a string

```python
directus.collection("directus_users")
```

Or you can pass the collection as a `Pydantic` model

```python
from typing import Optional
from pydantic import BaseModel


class User(BaseModel):
    id: Optional[str]
    first_name: Optional[str]
    last_name: Optional[str]
    avatar: Optional[str]
    description: Optional[str]
    email: Optional[str]
    role: Optional[str] | Optional[Role]
    status: Optional[str]
    title: Optional[str]
    token: Optional[str]

    class Config:
        collection = 'directus_users'


directus.collection(User)
```

> Don't forget to set the `collection` attribute in the `Config` class

If you go with the second option, you will get the responses as `Pydantic` models (auto parsing)

> The `collection` method returns a `DirectusRequest` object which is used to perform READ, CREATE,
> UPDATE and DELETE operations
