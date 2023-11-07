import asyncio

from dotenv import dotenv_values

from py_directus import Directus
from py_directus.fast_api.utils import role_to_id, directus_admin
from py_directus.fast_api.auth import directus_auth, assert_role


config = dotenv_values(".env")


class TestRequest:
    """
    Test request class.
    """

    def __init__(self, acc_token: str, ref_token: str):
        self.headers = {
            # "Authorization": ""
        }
        self.cookies = {
            "access_token": acc_token,
            "refresh_token": ref_token
        }


@assert_role(["Administrator"])
async def some_func(directus):
    print("Accessed endpoint")


async def main():
    directus = await Directus(config["DIRECTUS_URL"], email=config["DIRECTUS_EMAIL"], password=config["DIRECTUS_PASSWORD"])

    # await directus_admin
    # await role_to_id
    # role_to_id("Administrator")

    directus = await directus_auth(
        request=TestRequest(acc_token=directus.token, ref_token=directus.refresh_token), 
        response=None
    )

    # Access the endpoint
    await some_func(directus)

    # Manual logout
    await directus.logout()

    # Manual connection termination
    await directus.close_connection()


if __name__ == "__main__":
    asyncio.run(main())
