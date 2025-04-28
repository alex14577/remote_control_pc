from bot.commands.base import ICommandHandler
from bot.services.ws_client import WebSocketClient
from bot.services.telegram_notifier import TelegramNotifier
from telegram import Update, CallbackQuery
import urllib.parse

class CloseHandler(ICommandHandler):
    command = "close"
    label = "Закрыть"

    def __init__(self, client: WebSocketClient):
        self._client = client

    async def __call__(self, update: Update, ctx):
        query = update.callback_query
        await self.handle(query)
        
    async def handle(self, query: CallbackQuery):
        query_data = query.data  # должен начинаться с "launch:"
        _, encoded_name = query_data.split(":", 1)
        name = urllib.parse.unquote(encoded_name)

        await TelegramNotifier.notify(f"🚀 Запрашиваем запуск: {name}")
        result = await self._client.send_command({"type": "close_game", "name": name})

        if "error" in result:
            await TelegramNotifier.notify(f"❌ Ошибка завершения: {result['error']}")
        else:
            await TelegramNotifier.notify(f"✅ Приложение завершено: {name}")