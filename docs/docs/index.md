# Welcome to py-directus

> Under development

py-directus is a Python wrapper for asynchronous interaction with the Directus headless CMS API. It provides a convenient and
easy-to-use interface for performing CRUD operations, querying data, and managing resources in Directus.

## Features

- Asynchronous
- Login and authentication handling
- Reading and writing data from Directus collections
- Filtering, sorting, and searching data
- Aggregating data using aggregation operators
- Creating, updating, and deleting items in Directus collections
- Handling multiple users in the same session

Dependencies:

- [Pydantic](https://pydantic-docs.helpmanual.io/): This library leverages Pydantic for data validation and parsing. Pydantic is a powerful tool in Python for ensuring data integrity and handling data validation with ease.

- [HTTPX](https://www.python-httpx.org/): The library utilizes HTTPX, a fully featured HTTP client for Python 3, which provides sync and async APIs, and support for both HTTP/1.1 and HTTP/2.

## Installation

You can install the library directly from pypi using pip:

```shell
$ pip install py-directus
```

> FastAPI support requires the installation of additional dependencies. 
> You can install them along others like so:

```shell
$ pip install py-directus[FastAPI]
```

## Quickstart

Let's assume that after installing the library you would like to use it in your project. For example: you want to retrieve a user record from your Directus backend.

### Import

First, you would need to import the `Directus` client class like so:

```python
from py_directus import Directus
```

### Login

Login to the backend using the appropriate credentials:

```python
directus = await Directus("https://example.com", email="user@example.com", password="secret")

# OR

directus = await Directus("https://example.com", token="static_token")
```

### Request

In case you were successfully identified by the system, then you can compose your request and retrieve the needed user record:

```python
response = await directus.collection("directus_users").filter(first_name="John").read()

user_item = response.item

# OR

user_item = (await directus.collection("directus_users").filter(first_name="John").read()).item
```

Notice that we gave the collection name as a string. This means that the end result will be formated as a regular dictionary.
This library supports `Pydantic` models and provides you with basic models for each `Directus` collection.

```python
from py_directus import DirectusUser

...

user_item = (await directus.collection(DirectusUser).filter(first_name="John").read()).item
```

In this case you will get your data as `Pydantic` model instances.

Now you have a dictionary containing all the information of the found record.

### Logout/Close Connection

After you have done everything you would like with the retrieved data you will have to log out of the Directus system and close the connection to free up resources:

```python
# Logout
await directus.logout()

# Manually close connection
await directus.close_connection()
```

### Full script

```python title="main.py"
import asyncio

from py_directus import DirectusUser, Directus


async def main():
    directus = await Directus("https://example.com", token="static_token")

    user_item = (await directus.collection(DirectusUser).filter(first_name="John").read()).item

    print(f"Full Name: {user_item.last_name} {user_item.first_name}")

    # Logout
    await directus.logout()

    # Manually close connection
    await directus.close_connection()


if __name__ == "__main__":
    asyncio.run(main())

```
