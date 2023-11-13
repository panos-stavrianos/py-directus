import asyncio

from dotenv import dotenv_values

from py_directus import Directus


config = dotenv_values(".env")


async def main(file_id):
    directus = await Directus(config["DIRECTUS_URL"], email=config["DIRECTUS_EMAIL"], password=config["DIRECTUS_PASSWORD"])

    # Uploading local file
    r = await directus.download_file(file_id, quality=20)
    print(r.status_code)

    # Logout
    await directus.logout()

    # Manually close connection
    await directus.close_connection()


if __name__ == "__main__":
    # Retrieving file id
    file_id = str(input("\nGive the file id:"))

    asyncio.run(main(file_id))
