# FastAPI Support

> In development

## Current use syntax

```python
from fastapi import Request, Depends
from py_directus import Directus
from py_directus.fast_api.auth import directus_auth, Roles, assert_role


@app.get("/")
@assert_role([Roles.ADMINISTRATOR])
async def root(request: Request, directus: Directus = Depends(directus_auth)):
    # This path operation function is accessed when authenticated user 
    # has the role of `administrator` in directus
    return {"message": "Hello World"}
```
