# bot/commands/simple_handler.py

from bot.commands.base import ICommandHandler
from bot.services.telegram_notifier import TelegramNotifier

class SimpleCommandHandler(ICommandHandler):
    def __init__(self, command: str, label: str):
        self.command = command
        self.label = label

    async def handle(self, query, server):
        # await TelegramNotifier.notify(f"🔄 Отправляем команду: {self.label}")
        result = await server.send_command({"type": self.command})

        if "error" in result:
            await TelegramNotifier.notify(f"⚠️ Ошибка: {result['error']}")
        else:
            await TelegramNotifier.notify(f"✅ Команда {self.label} выполнена")
