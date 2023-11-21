import asyncio
import functools
from contextlib import asynccontextmanager


@asynccontextmanager
async def _lifespan(app: str = "FastAPI", *args, **kwargs):
    # Load the ML model
    print(app)
    print("ONE")
    try:
        yield
    finally:
        # Clean up the ML models and release the resources
        print("ONE END")


def lifespan(*og_args, **og_kwargs):
    def wrapper(cm=None, *ag_args, **ag_kwargs):
        if callable(cm):
            @asynccontextmanager
            @functools.wraps(cm)
            async def wrapped(*args, **kwargs):
                async with _lifespan(*og_args, **og_kwargs) as og_res:
                    async with cm(*args, **kwargs) as cm_res:
                        # Load the ML model
                        # print("three")
                        try:
                            yield cm_res
                        finally:
                            # Clean up the ML models and release the resources
                            # print("three END")
                            pass
            return wrapped
        else:
            return _lifespan(*og_args, *ag_args, **og_kwargs, **ag_kwargs)
    return wrapper


@lifespan(app="ULTRA")
@asynccontextmanager
async def secondlifespan(app="FastAPI"):
    # async with _lifespan() as og:
    # Load the ML model
    print(app)
    print("TWO")
    try:
        yield
    finally:
        # Clean up the ML models and release the resources
        print("TWO END")


async def main():
    async with secondlifespan(app="SOME") as sc:
        print("IN MIDDLE")
    
    print("______________________")
    
    our_cm = lifespan()

    async with our_cm(app="OTHER SOME") as orig:
        print("OTHER MIDDLE")

    print("______________________")

    print("Wrapped twice")

    twice_cm = lifespan(app="TWICE SOME")(secondlifespan)

    async with twice_cm(app="TWICE OTHER SOME") as twice:
        print("TWICE OTHER MIDDLE")


if __name__ == "__main__":
    asyncio.run(main())
