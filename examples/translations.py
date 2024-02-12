import asyncio

from dotenv import dotenv_values

from py_directus import DirectusUser, Directus


config = dotenv_values(".env")


async def main():
    # directus = await Directus.create(config["DIRECTUS_URL"], email=config["DIRECTUS_EMAIL"], password=config["DIRECTUS_PASSWORD"])
    directus = await Directus(config["DIRECTUS_URL"], email=config["DIRECTUS_EMAIL"], password=config["DIRECTUS_PASSWORD"])

    # Retrieving translation records
    translations = await directus.get_translations()
    print(f"TRANSLATIONS: {translations}")

    # Creating a new translation record
    directus_response = await directus.create_translations(tuple(["some", "el-GR"]))
    print(f"DIRECTUS RESPONSE: {directus_response}")

    # Retrieving translation records again
    translations = await directus.get_translations()
    print(f"TRANSLATIONS (AGAIN): {translations}")

    # Logout
    await directus.logout()

    # Manually close connection
    await directus.close_connection()


if __name__ == "__main__":
    asyncio.run(main())
