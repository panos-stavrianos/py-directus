import asyncio

from dotenv import dotenv_values

from py_directus import Directus


config = dotenv_values(".env")


async def upload_file(directus_client, file_path):
    # Uploading local file
    r = await directus_client.upload_file(file_path)
    print(r.text)


async def get_files_list(directus_client):
    # Get files list
    response = await directus_client.collection('directus_files').filter(type='image/jpeg').read()
    print(response.items)


async def main(file_path):
    directus = await Directus(config["DIRECTUS_URL"], email=config["DIRECTUS_EMAIL"], password=config["DIRECTUS_PASSWORD"])

    # Execute
    await get_files_list(directus)

    await upload_file(directus, file_path)

    # Logout
    await directus.logout()

    # Manually close connection
    await directus.close_connection()


if __name__ == "__main__":
    # Retrieving file path
    file_path = str(input("\nGive the file path:"))

    asyncio.run(main(file_path))
