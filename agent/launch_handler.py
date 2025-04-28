from bot.commands.base import ICommandHandler
from bot.services.ws_client import WebSocketClient
from bot.services.telegram_notifier import TelegramNotifier
from telegram import CallbackQuery
import urllib.parse

class LaunchHandler(ICommandHandler):
    command = "launch"
    label = "Запустить"

    async def handle(self, query: CallbackQuery, client: WebSocketClient):
        query_data = query.data
        _, encoded_name = query_data.split(":", 1)
        name = urllib.parse.unquote(encoded_name)

        await TelegramNotifier.notify(f"🚀 Запрашиваем запуск: {name}")
        result = await client.send_command({"type": "launch_game", "name": name})

        if "error" in result:
            await TelegramNotifier.notify(f"❌ Ошибка запуска: {result['error']}")
        else:
            await TelegramNotifier.notify(f"✅ Запуск выполнен для: {name}")
