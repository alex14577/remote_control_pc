import asyncio
import json
import time
from typing import Callable, Awaitable, Optional

from websockets.asyncio.client import ClientConnection, connect
from websockets.exceptions import ConnectionClosed


class WebSocketClient:
    def __init__(self, uri: str, reconnect_interval: int = 1):
        self.uri = uri
        self.websocket: Optional[ClientConnection] = None
        self.queue: asyncio.Queue[dict] = asyncio.Queue()
        self.reconnect_interval = reconnect_interval
        self.connected = asyncio.Event()
        self._lock = asyncio.Lock()
        asyncio.create_task(self._auto_connect())

    async def _auto_connect(self):
        while True:
            if not self._is_websocket_open():
                await self._connect()
                if self._is_websocket_open():
                    asyncio.create_task(self._receive_loop())
            await asyncio.sleep(self.reconnect_interval)

    def _is_websocket_open(self) -> bool:
        return self.websocket is not None and self.websocket.close_code is None

    async def _connect(self) -> bool:
        self.connected.clear()
        try:
            print(f"🌐 Подключение к агенту по адресу {self.uri}...")
            self.websocket = await connect(self.uri)
            print("✅ Подключение установлено")
            self.connected.set()
            return True
        except Exception as e:
            print(f"❌ Ошибка подключения: {e}")
            self.websocket = None
            return False

    async def _ensure_connection(self, timeout: int = 5) -> bool:
        try:
            await asyncio.wait_for(self.connected.wait(), timeout)
            return True
        except asyncio.TimeoutError:
            print("⏱ Превышено время ожидания подключения к агенту")
            return False

    async def _receive_loop(self):
        try:
            async for message in self.websocket:
                try:
                    data = json.loads(message)
                    await self.queue.put(data)
                except json.JSONDecodeError:
                    print("⚠️ Невалидный JSON от агента")
        except ConnectionClosed:
            print("⚠️ Подключение к агенту закрыто")
        except Exception as e:
            print(f"❌ Ошибка в приёме сообщений: {e}")
        finally:
            self.connected.clear()

    async def send_command(self, command: dict, timeout: int = 5) -> dict:
        start_time = time.monotonic()
        if not await self._ensure_connection(timeout):
            return {"error": "timeout waiting for connection"}

        remaining = timeout - (time.monotonic() - start_time)
        if remaining <= 0:
            return {"error": "timeout after connection"}

        try:
            async with self._lock:
                await asyncio.wait_for(
                    self.websocket.send(json.dumps(command)), timeout=remaining
                )
                print(f"📤 Команда отправлена агенту: {command}")
                return {"status": "sent"}
        except Exception as e:
            print(f"❌ Ошибка при отправке команды: {e}")
            return {"error": str(e)}

    async def get_message(self, timeout: int = 5) -> dict:
        start_time = time.monotonic()
        if not await self._ensure_connection(timeout):
            return {"error": "timeout waiting for connection"}

        remaining = timeout - (time.monotonic() - start_time)
        if remaining <= 0:
            return {"error": "timeout after connection"}

        try:
            return await asyncio.wait_for(self.queue.get(), timeout=remaining)
        except asyncio.TimeoutError:
            return {"error": "timeout waiting for message"}


class AgentCommandHandler:
    def __init__(self, client: WebSocketClient):
        self.client = client
        self.handlers: dict[str, Callable[[dict], Awaitable[None]]] = {}

    def register(self, message_type: str, handler: Callable[[dict], Awaitable[None]]):
        self.handlers[message_type] = handler

    async def run(self):
        print("📡 Ожидание сообщений от агента...")
        while True:
            message = await self.client.get_message()
            if not message or "error" in message:
                continue

            if isinstance(message, dict):
                message_type = message.get("type")
                handler = self.handlers.get(message_type)
                if handler:
                    try:
                        await handler(message)
                    except Exception as e:
                        print(f"❌ Ошибка при обработке команды '{message_type}': {e}")
                else:
                    print(f"⚠️ Неизвестный тип сообщения: {message_type}")