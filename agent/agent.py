# agent/agent.py

import asyncio
import json
import websockets

from agent.logger import Logger
from agent.commands import handle_command

connected_clients = set()


logger = Logger().Get("handler")

async def handler(websocket):
    logger.info("🤝 Клиент подключился")
    connected_clients.add(websocket)
    try:
        async for message in websocket:
            try:
                command = json.loads(message)
                await handle_command(command, websocket)
            except Exception as e:
                logger.error(f"⚠️ Ошибка при обработке команды: {e}")
    except websockets.ConnectionClosed:
        logger.info("❌ Клиент отключился")
    finally:
        connected_clients.remove(websocket)


async def run_agent(host: str, port: int):
    logger.info(f"🚀 Агент слушает на {host}:{port}")
    async with websockets.serve(handler, host, port):
        await asyncio.Future()  # run forever
