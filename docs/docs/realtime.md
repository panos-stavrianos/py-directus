# Realtime

You have the ability to establish a bidirectional connection with a specific collection 
via the `subscribe` method of the `DirectusRequest` class.

## Proxy server

Pass websocket messages through your backend to directus, thus not exposing the directus endpoint.

### Implementation

Pure python.

```python
import json
import asyncio
import websockets

from py_directus import Directus


async def directusToFrontend(ws, websocket):
    async for message in ws:
        data = json.loads(message)

        if data.get("type", "") == "ping":
            pong_data = json.dumps({
                "type": "pong"
            })

            await ws.send(pong_data)
        else:
            await websocket.send_text(message)


async def frontendToDirectus(ws, websocket):
    async for message in websocket.iter_text():
        await ws.send(message)
    await ws.close()


async def ws_proxy(websocket):
    """
    Called whenever a new connection is made to the server
    """

    directus_client = await Directus(DIRECTUS_URL, token=ACCESS_TOKEN)

    try:
        (auth_data, ws) = await directus_client.collection("test_messages").filter(status="published").subscribe(WS_URL)

        taskA = asyncio.create_task(directusToFrontend(ws, websocket))
        taskB = asyncio.create_task(frontendToDirectus(ws, websocket))

        await taskA
        await taskB
    except:
        await websocket.close()


if __name__ == "__main__":
    DIRECTUS_URL = "https://some-where.xyz"
    WS_URL = "ws://some-where.xyz/websocket"
    ACCESS_TOKEN = "vTUMahtspcJ1PGpXccIttSzKkveeXaC7";

    start_server = websockets.serve(ws_proxy, "", 8001)

    asyncio.get_event_loop().run_until_complete(start_server)
    asyncio.get_event_loop().run_forever()
```

FastAPI.

```python
import json
import asyncio
import websockets

from starlette.websockets import WebSocket, WebSocketDisconnect
from fastapi import FastAPI

from py_directus import Directus


app = FastAPI()


async def directusToFrontend(ws, websocket):
    async for message in ws:
        data = json.loads(message)

        if data.get("type", "") == "ping":
            pong_data = json.dumps({
                "type": "pong"
            })

            await ws.send(pong_data)
        else:
            await websocket.send_text(message)


async def frontendToDirectus(ws, websocket):
    async for message in websocket.iter_text():
        await ws.send(message)
    await ws.close()


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()

    directus_url = "https://some-where.xyz"
    ws_uri = "ws://some-where.xyz/websocket"
    access_token = "vTUMahtspcJ1PGpXccIttSzKkveeXaC7";

    directus_client = await Directus(directus_url, token=access_token)

    try:
        (auth_data, ws) = await directus_client.collection("test_messages").filter(status="published").subscribe(ws_uri)

        taskA = asyncio.create_task(directusToFrontend(ws, websocket))
        taskB = asyncio.create_task(frontendToDirectus(ws, websocket))

        await taskA
        await taskB
    except:
        await websocket.close()
```
