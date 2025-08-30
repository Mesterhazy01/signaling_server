# signaling_server.py
import asyncio
from aiohttp import web
import json

ROOMS = {}  # szoba_id: [ws1, ws2, ...]

async def websocket_handler(request):
    ws = web.WebSocketResponse()
    await ws.prepare(request)

    room_id = request.query.get("room")
    if room_id not in ROOMS:
        ROOMS[room_id] = []
    ROOMS[room_id].append(ws)

    try:
        async for msg in ws:
            if msg.type == web.WSMsgType.TEXT:
                data = msg.data
                # forward message to all other peers in the same room
                for peer in ROOMS[room_id]:
                    if peer != ws:
                        await peer.send_str(data)
    finally:
        ROOMS[room_id].remove(ws)

    return ws

app = web.Application()
app.add_routes([web.get("/ws", websocket_handler)])

if __name__ == "__main__":
    web.run_app(app, port=8080)
