import os

from dotenv import load_dotenv
from httpx import AsyncClient

from py_directus import Directus


load_dotenv()
directus_url = os.environ.get('DIRECTUS_URL')
directus_admin_token = os.environ.get('DIRECTUS_ADMIN_TOKEN')

cached_directus_instances = dict[str, Directus]()

directus_session = AsyncClient()
directus_session.timeout = 0.7
directus_session.headers.update({'Cache-Control': 'no-store'})

# Client with administrator access
directus_admin = Directus(directus_url, token=directus_admin_token, connection=directus_session)
