# py-directus

## Disclaimer: Under development

Documentation [here](https://panos-stavrianos.github.io/py-directus/)

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

> Directus API:
> This library interacts with the [Directus API](https://docs.directus.io/reference/introduction.html).
> 
> To make the most of this library, it is highly recommended to familiarize yourself with the Directus API documentation. Understanding the API's capabilities and endpoints will help you effectively utilize this library for seamless integration with Directus.

## Installation

You can install the library directly from [pypi](https://pypi.org/project/py-directus/) using pip:

```shell
$ pip install py-directus
```

> FastAPI support requires additional dependencies installation. 
> You can install them along others like this:

```shell
$ pip install py-directus[FastAPI]
```

## Authentication and Session Handling

### Login

Create a Directus instance using email and password

```python
from py_directus import Directus

directus = await Directus("https://example.com", email="user@example.com", password="secret")
```

Alternatively create a Directus instance using the static token

```python
from py_directus import Directus

directus = await Directus("https://example.com", token="static token")
```

Another way is to use the `with` statement to automatically logout when the session ends

```python
async with Directus(url, email, password) as directus:
    # Manually login
    await directus.login()
    # do stuff

# OR

async with await Directus(url, email, password) as directus:
    # do stuff
```

### Refresh Token

If you want to refresh the token you can use the `refresh` method

```python
await directus.refresh()
```

### Logout

Logout from Directus

```python
await directus.logout()
```

### Multiple Users in the Same Session

You can use multiple users in the same session by creating a new Directus instance by passing the client object

```python
connection = httpx.AsyncClient()
directus1 = await Directus(url, token=token, connection=connection)
directus2 = await Directus(url, email=email, password=password, connection=connection)
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

from pydantic import ConfigDict

from py_directus.models import DirectusModel


class User(DirectusModel):
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

    model_config = ConfigDict(collection="directus_users")


directus.collection(User)
```

> Don't forget to set the `collection` attribute in the `model_config` attribute

If you go with the second option, you will get the responses as `Pydantic` models (auto parsing)

> The `collection` method returns a `DirectusRequest` object which is used to perform READ, CREATE,
> UPDATE and DELETE operations

## Reading Data

When you have the DirectusRequest object you can use the `read` method to get the data.
This will return a DirectusResponse object which contains the data.

> Imporatnt note: The `read` method must be awaited

```python
await directus.collection("directus_users").read()
```

### Filtering

For an easy equality filter you can pass the field name and the value

```python
await directus.collection("directus_users").filter(first_name="John").read()
```

To add multiple equality filters you can chain the `filter` method

```python
await directus.collection("directus_users")
.filter(first_name="John")
.filter(last_name="Doe").read()
```

Using it like this you chain the filters with `AND` operator

#### F objects

To define complex logic in filters, use the `F` object

```python
from py_directus import F

await directus.collection("directus_users")
.filter(
    (F(first_name="John") | F(first_name="Jane")) 
    & F(last_name="Doe")
).read()
```

> Important note: The `F` object does not support negation

### Sorting

You can sort the data by passing the field name to the `sort` method

```python
await directus.collection("directus_users").sort("first_name", asc=True).read()
```

To add multiple sorting fields you can chain the `sort` method

```python
await directus.collection("directus_users")
.sort("first_name", asc=True)
.sort("last_name", asc=False).read()
```

### Limiting

You can limit the data by passing the limit to the `limit` method

```python
await directus.collection("directus_users").limit(10).read()
```

### Aggregation

Aggregate the number of records in the query

```python
await directus.collection("directus_users").aggregate().read()

# OR

await directus.collection("directus_users").aggregate(count="*").read()
```

To add multiple aggregates you can chain the `aggregate` method

```python
await directus.collection("products")
.aggregate(countDistinct="id")
.aggregate(sum="price").read()
```

#### Agg objects

You can aggregate the data by defining the needed aggregation with the `Agg` class and passing it to the `aggregate` method

```python
from py_directus.aggregator import Agg

agg_obj = Agg(operator=AggregationOperators.Count)

await directus.collection("directus_users").aggregate(agg_obj).read()
```

In case you need only certain fields

```python
from py_directus.aggregator import Agg

amount_agg = Agg(operator=AggregationOperators.Sum, fields="amount")

await directus.collection("transactions").aggregate(amount_agg).read()
```

The available aggregation operators are:

- Count
- CountDistinct
- CountAll (Only in GraphQL)
- Sum
- SumDistinct
- Average
- AverageDistinct
- Minimum
- Maximum

### Grouping

You can group the data by passing the field names to the `group_by` method

```python
await directus.collection("directus_users").group_by("first_name", "last_name").read()
```

### Searching

You can search the data by passing the search term to the `search` method

```python
await directus.collection("directus_users").search("John").read()
```

### Selecting Fields

You can select the fields you want to get by passing the field names to the `fields` method

```python
await directus.collection("directus_users").fields("first_name", "last_name").read()
```

### Getting the Count Metadata

You can get the count of the data (total count and filtered count) calling `include_count`

```python
await directus.collection("directus_users").include_count().read()
```

## CRUD

### Retrieving items

After you call `read()` you get a `DirectusResponse` object which contains the data.

- `item` for single item
- `items` for multiple items

Getting the data as a dictionary or a list of dictionaries

```python
response = await directus.collection("directus_users").read()
print(response.item["first_name"])
print(response.items)
```

If you provide the `collection` method a `Pydantic` model you will get the data as a `Pydantic` object or a list of `Pydantic` objects

```python
response = await directus.collection(User).read()
print(response.item.first_name)
print(response.items)
```

### Converting to Models (pydantic) or to Dictionary

Apart from the auto parsing, you can manually convert the data to a `Pydantic` model instance or to a dictionary using:

- `item_as(User)` or `items_as(User)`
- `item_as_dict()` or `items_as_dict()`

```python
response = await directus.collection("directus_users").read()
print(response.item_as(User))

response = await directus.collection(User).read()
print(response.item_as_dict())
```

### Creating Items

The library does not support `Pydantic` models for creation, you have to pass a dictionary

- create(items: dict|List[dict])

```python
await directus.collection("directus_users").create({
    "first_name": "John", "last_name": "Doe"
})

# OR

await directus.collection("directus_users").create(
    [
        {"first_name": "John", "last_name": "Doe"},
        {"first_name": "Jane", "last_name": "Doe"}
    ]
)
```

### Updating Items

The library do not support `Pydantic` models for updating, you have to pass a dictionary

- `update(ids: str|int, items: dict)`
- `update(ids: List[str|int], items: List[dict])`

```python
await directus.collection("directus_users").update(1, {
    "first_name": "Red",
    "last_name": "John"
})

# OR

await directus.collection("directus_users").update(
    [1, 2],
    [
        {"first_name": "Jean-Luc"},
        {"first_name": "Jane", "last_name": "Doe"}
    ]
)
```

### Deleting Items

- `delete(ids: str|int|List[str|int])`

```python
await directus.collection("directus_users").delete(1)

# OR

await directus.collection("directus_users").delete([1, 2])
```

> Supporting `Pydantic` models for `create`/`update`/`delete` item operations is shortly coming.

## Examples

> Examples are not included with the `pypi` package, so you will have to download them separately and execute in a virtual environment.

Run individual examples as such:

```shell
python -m examples.<example_file_name>
```

## Tests

Run tests as such:

```shell
# All unit tests

python -m unittest discover -s tests/unit

# All integration tests

python -m unittest discover -s tests/integration
```
