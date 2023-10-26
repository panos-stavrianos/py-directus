# FastAPI Support

> In development

## Syntax

Current use syntax

```python
from fastapi import Request, Depends
from py_directus import Directus
from py_directus.fast_api.auth import directus_auth, assert_role
from py_directus.fast_api.utils import Roles


@app.get("/")
@assert_role([Roles.ADMINISTRATOR])
async def root(request: Request, directus: Directus = Depends(directus_auth)):
    # This path operation function is accessed when authenticated user 
    # has the role of `administrator` in directus
    return {"message": "Hello World"}
```

## Changes

> Some functionality of the `RoleToID` and `Directus` classes has been moved to their `__await__` method, 
> so the globals (`directus_admin` and `role_to_id`) of the `fast_api` module must be awaited before usage.

Previous syntax

```python
...

roles = directus_admin.collection(Role).read().items
self.roles = {role.name: role.id for role in roles}

...

role_id = role_to_id(role)

...
```

Current syntax
```python
...

# The global does not perform the login automatically, 
# so we must do it manually by awaiting
await directus_admin
roles = await directus_admin.collection(Role).read()
self.roles = {role.name: role.id for role in roles.items}

...

# The global does not fetch roles from Directus automatically, 
# so we must do it manually by awaiting
await role_to_id
role_id = role_to_id(role)

...
```
