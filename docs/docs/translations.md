# Custom Translations

We provide the `get_translations` and `create_translations` methods of the `Directus` class client 
for you to retrieve and create new translation records on the `Directus` backend.

## Retrieve Translations

Retrieving translation records

```python
...
# A list of translation records in dictionary format
translations = await directus.get_translations()

# A dictionary of translation records grouped by the `key` field
# {
#     "<key>": {
#         "<language>": "<value>"
#     }
# }
translations = await directus.get_translations(clean=True)
...
```

> Note: The automatic retrieval of all Directus translation records is supported by the `async_init` function 
> when the `load_translations` argument is set to `True`. 
> You can access the translations from the `pydirectus.translations` global. The global is in `clean` format.

## Create Translations

Creating a new translation record

```python
...
# Register a translation record for the given values (language: 'en-GB')
directus_response = await directus.create_translations("some")

# Register a translation record for the given values with specific language
directus_response = await directus.create_translations(tuple(["some", "el-GR"]))
...
```
