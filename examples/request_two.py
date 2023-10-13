import asyncio

from dotenv import dotenv_values

from py_directus import Directus
from py_directus.models import User


config = dotenv_values(".env")


async def get_str(directus_client):
    jn_doe_res = await directus_client.collection("directus_users").filter(first_name="John").filter(last_name="Doe").read()

    print(f"When a string is used: {jn_doe_res.items}")
    # print(jn_doe_res.item["first_name"])


async def get_model(directus_client):
    jn_doe_res = await directus_client.collection(User).filter(first_name="John", last_name="Doe").read()

    print(f"When a pydantic model is used: {jn_doe_res.items}")


async def main():
    async with Directus(config["DIRECTUS_URL"], email=config["DIRECTUS_EMAIL"], password=config["DIRECTUS_PASSWORD"]) as directus:
        # Manually run login
        await directus.login()

        # Filtering
        await asyncio.gather(get_str(directus), get_model(directus))


if __name__ == "__main__":
    asyncio.run(main())
