# agent/agent.py

import asyncio
import json
import websockets
from typing import Callable, Awaitable

from agent.logger import Logger


class Agent:
    def __init__(self):
        self.handlers: dict[str, Callable[[dict, websockets.WebSocketServerProtocol], Awaitable[None]]] = {}
        self.connected_clients = set()
        self._logger = Logger().Get("agent")

    def register(self, command_name: str):
        def decorator(fn: Callable[[dict, websockets.WebSocketServerProtocol], Awaitable[None]]):
            if command_name in self.handlers:
                self._logger.warning(f"Command '{command_name}' is already registered. Overwriting.")
            else:
                self._logger.info(f"Registered command: {command_name}")
            self.handlers[command_name] = fn
            return fn
        return decorator

    async def handle(self, message: dict, websocket: websockets.WebSocketServerProtocol):
        command = message.get("type")
        handler = self.handlers.get(command)
        if handler:
            await handler(message, websocket)
        else:
            self._logger.error(f"\u26a0\ufe0f Unknown command: {command}")

    async def handler(self, websocket: websockets.WebSocketServerProtocol):
        self._logger.info("\U0001f91d Client connected")
        self.connected_clients.add(websocket)
        try:
            async for message in websocket:
                try:
                    command = json.loads(message)
                    await self.handle(command, websocket)
                except Exception as e:
                    self._logger.error(f"\u26a0\ufe0f Error handling command: {e}")
        except websockets.ConnectionClosed:
            self._logger.info("❌ Client disconnected")
        finally:
            self.connected_clients.remove(websocket)

    async def run(self, host: str, port: int):
        self._logger.info(f"\U0001f680 Agent listening on {host}:{port}")
        async with websockets.serve(self.handler, host, port):
            await asyncio.Future()  # run forever

