# Cache

We provide a basic caching mechanism for request results.

## Usage

```python
...

dr_request = directus_client.collection("directus_users").filter(first_name="John").filter(last_name="Doe")

# Makes a request to the Directus server
rqst_result = await dr_request.read(cache=True)

# Subsequent requests with the same query will return the cached result
dr_request = directus_client.collection(User).filter(first_name="John", last_name="Doe")

rqst_result = await dr_request.read(cache=True)

# If you call the `read` method again, but without the `cache` argument, and there is a not expired cache record, the record will be updated
rqst_result = await dr_request.read()

...
```

## Clear cache

The cache records expire after an hour. 
When you try to get the cached result via the query key, it is completely deleted.

### Client

```python
...

# Clear records in client namespace
await directus_client.clear_cache()

# Clear ALL cached results
await directus_client.clear_cache(True)

...
```

### Request

```python
...

dr_request = directus_client.collection("directus_users").filter(first_name="John").filter(last_name="Doe")

# Caches the result
rqst_result = await dr_request.read(cache=True)

...

# Deletes the cached result
await dr_request.clear_cache()

...
```
