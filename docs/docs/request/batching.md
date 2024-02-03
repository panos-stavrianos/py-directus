# Batching Requests

If you need to make multiple independent requests to the Directus server, you can use `async.gather(*requests)`,
or set the flag `as_task` of the `read`, `create`, `update`, `delete` methods.

Then call `await directus.gather()` to execute the batch.

> When `as_task` flag is used the request is added to a list of tasks that will be executed
> when `await directus.gather()`
> is called.

```python
import asyncio

from py_directus import Directus


async def with_async_gather(directus: Directus):
    tasks = [
        directus.collection("directus_users").read(),
        directus.collection("directus_files").read(),
    ]
    results = await asyncio.gather(*tasks)
    result_1 = results[0]
    result_2 = results[1]
    print(result_1.items, result_2.items)


async def with_as_task(directus: Directus):
    result_1 = await directus.collection("directus_users").read(as_task=True)
    result_2 = await directus.collection("directus_files").read(as_task=True)

    await directus.gather()
    print(result_1.items, result_2.items)
```

> IMPORTANT: cache and as_task cannot be used together, if both are set to True, the cache will take precedence and the
> request will be awaited.

 
