from dotenv import dotenv_values

from py_directus import Directus
from py_directus.models import User


config = dotenv_values(".env")


if __name__ == "__main__":
    directus = Directus(config["CONN_URI"], email=config["CONN_EMAIL"], password=config["CONN_PASSWORD"])

    # Filtering
    jn_doe_res = directus.collection("directus_users").filter(first_name="John").filter(last_name="Doe").read()

    print(f"When a string is used: {jn_doe_res.items}")
    # print(jn_doe_res.item["first_name"])

    # OR
    jn_doe_res = directus.collection(User).filter(first_name="John", last_name="Doe").read()

    print(f"When a pydantic model is used: {jn_doe_res.items}")

    directus.logout()

    # Mannually close connection
    directus.close_connection()
