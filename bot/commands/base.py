# bot/commands/base.py
from abc import ABC, abstractmethod
from telegram import CallbackQuery
from bot.services.ws_client import WebSocketClient
from bot.services.telegram_notifier import TelegramNotifier

class ICommandHandler(ABC):
    async def __call__(self, query: CallbackQuery, client: WebSocketClient):
        await self.handle(query, client)

        # try:
        #     await TelegramNotifier.notify("Done")
        # except Exception as e:
        #     print(f"⚠️ Не удалось обновить сообщение: {e}")

    @abstractmethod
    async def handle(self, query: CallbackQuery, client: WebSocketClient) -> str:
        pass

