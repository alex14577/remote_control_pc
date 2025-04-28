# bot/commands/info_handler.py

from bot.commands.base import ICommandHandler
from bot.services.telegram_notifier import TelegramNotifier
from bot.services.ws_client import WebSocketClient

import json

class InfoHandler(ICommandHandler):
    command = "info"
    label = "Инфо"

    async def handle(self, query, client: WebSocketClient):
        await TelegramNotifier.notify("🔄 Запрашиваем информацию у агента...")
        result = await client.send_command({"type": "get_info"})

        if "error" in result:
            await TelegramNotifier.notify(f"⚠️ Ошибка: {result['error']}")
