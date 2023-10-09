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
