import asyncio

from dotenv import dotenv_values

from py_directus import DirectusUser, Directus


config = dotenv_values(".env")


async def get_str(directus_client: Directus):
    jn_doe_res = await directus_client.collection("directus_users").filter(first_name="John").filter(last_name="Doe").read(cache=True)

    print(f"When a string is used: {jn_doe_res.items}")
    # print(jn_doe_res.item["first_name"])


async def get_model(directus_client: Directus):
    jn_doe_res = await directus_client.collection(DirectusUser).filter(first_name="John", last_name="Doe").read(cache=True)

    print(f"When a pydantic model is used: {jn_doe_res.items}")


async def main():
    # directus = await Directus.create(config["DIRECTUS_URL"], email=config["DIRECTUS_EMAIL"], password=config["DIRECTUS_PASSWORD"])
    directus = await Directus(config["DIRECTUS_URL"], email=config["DIRECTUS_EMAIL"], password=config["DIRECTUS_PASSWORD"])

    # Filtering
    await asyncio.gather(get_str(directus), get_model(directus))

    # print(directus.cache._cache)

    # await asyncio.gather(*[get_str(directus) for _ in range(10)])

    # Logout
    await directus.logout()

    # Manually close connection
    await directus.close_connection()


if __name__ == "__main__":
    asyncio.run(main())
