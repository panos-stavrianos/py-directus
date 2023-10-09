from dotenv import dotenv_values

from py_directus import Directus


config = dotenv_values(".env")


if __name__ == "__main__":
    directus = Directus(config["CONN_URI"], email=config["CONN_EMAIL"], password=config["CONN_PASSWORD"])

    # Filtering
    jn_doe_res = directus.items("directus_users").filter(first_name="John").filter(last_name="Doe").read()

    print(jn_doe_res.items)
    # print(jn_doe_res.item["first_name"])

    directus.logout()
