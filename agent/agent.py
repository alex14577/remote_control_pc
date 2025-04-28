# agent/agent.py

import asyncio
import json
import websockets
from agent.commands import handle_command

connected_clients = set()

async def handler(websocket):
    print("🤝 Клиент подключился")
    connected_clients.add(websocket)
    try:
        async for message in websocket:
            try:
                command = json.loads(message)
                await handle_command(command, websocket)
            except Exception as e:
                print(f"⚠️ Ошибка при обработке команды: {e}")
    except websockets.ConnectionClosed:
        print("❌ Клиент отключился")
    finally:
        connected_clients.remove(websocket)


async def run_agent(host: str, port: int):
    print(f"🚀 Агент слушает на {host}:{port}")
    async with websockets.serve(handler, host, port):
        await asyncio.Future()  # run forever
