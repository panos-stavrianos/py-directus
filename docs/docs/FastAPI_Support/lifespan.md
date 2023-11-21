# Lifespan

> In development

We provide a predefined lifespan context manager that you can use to initialize and close 
some globaly available Directus clients.

```python
import os

from dotenv import load_dotenv

from fastapi import FastAPI

from py_directus.fast_api import globals as py_dr_glob_vars
from py_directus.fast_api.lifespan import lifespan


load_dotenv()

directus_url = os.environ.get('DIRECTUS_URL')
directus_admin_token = os.environ.get('DIRECTUS_ADMIN_TOKEN')


app = FastAPI(lifespan=lifespan(directus_base_url=directus_url, directus_admin_token=directus_admin_token))


@app.get("/predict")
async def predict(x: float):
    user = await py_dr_glob_vars.directus_admin.user
    return {"user": user}
```

In case you have already defined your own lifespan context manager, then you can wrap our lifespan around yours like in the following example:


```python
import os

from dotenv import load_dotenv

from contextlib import asynccontextmanager

from fastapi import FastAPI

from py_directus import init_directus, globals as py_dr_glob_vars


load_dotenv()

directus_url = os.environ.get('DIRECTUS_URL')
directus_admin_token = os.environ.get('DIRECTUS_ADMIN_TOKEN')


def fake_answer_to_everything_ml_model(x: float):
    return x * 42


ml_models = {}


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Load the ML model
    ml_models["answer_to_everything"] = fake_answer_to_everything_ml_model
    yield
    # Clean up the ML models and release the resources
    ml_models.clear()


app = FastAPI(lifespan=lifespan)

# Here we wrap app's lifespan context manager with our own
init_directus(app, directus_base_url=directus_url, directus_admin_token=directus_admin_token)


@app.get("/predict")
async def predict(x: float):
    result = ml_models["answer_to_everything"](x)
    user = await py_dr_glob_vars.directus_admin.user
    return {"result": result, "user": user}
```


> ALTERNATIVE (used in case we need to wrap a specific context manager within app's lifespan)


```python
import os

from dotenv import load_dotenv

from contextlib import asynccontextmanager

from fastapi import FastAPI

from py_directus.fast_api import globals as py_dr_glob_vars
from py_directus.fast_api.lifespan import lifespan as py_dr_lifespan


load_dotenv()

directus_url = os.environ.get('DIRECTUS_URL')
directus_admin_token = os.environ.get('DIRECTUS_ADMIN_TOKEN')


def fake_answer_to_everything_ml_model(x: float):
    return x * 42


ml_models = {}


@py_dr_lifespan(directus_base_url=directus_url, directus_admin_token=directus_admin_token)
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Load the ML model
    ml_models["answer_to_everything"] = fake_answer_to_everything_ml_model
    yield
    # Clean up the ML models and release the resources
    ml_models.clear()


app = FastAPI(lifespan=lifespan)


@app.get("/predict")
async def predict(x: float):
    result = ml_models["answer_to_everything"](x)
    user = await py_dr_glob_vars.directus_admin.user
    return {"result": result, "user": user}
```
