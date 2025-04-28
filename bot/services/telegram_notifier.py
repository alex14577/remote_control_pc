from telegram import Bot
from telegram.error import TelegramError
from typing import Optional
import logging

from telegram import InlineKeyboardMarkup, InlineKeyboardButton, Update
import urllib.parse

logger = logging.getLogger(__name__)

class TelegramNotifier:
    bot: Optional[Bot] = None
    chat_id: Optional[int] = None

    @classmethod
    def configure(cls, token: str, chat_id: int):
        cls.bot = Bot(token)
        cls.chat_id = chat_id

    @classmethod
    async def notify_all(cls, text: str):
        if cls.bot and cls.chat_id:
            try:
                await cls.bot.send_message(chat_id=cls.chat_id, text=text)
            except TelegramError as e:
                logger.error(f"Ошибка при отправке сообщения: {e}")

    @classmethod
    async def notify(cls, text: str):
        await cls.notify_all(text)

    @classmethod
    async def on_info(cls, payload: dict):
        text = payload["data"]
        await cls.notify(f"💍 Информация о системе:\n{text}")

    @classmethod
    async def on_games(cls, payload: dict):
        if not payload or "data" not in payload:
            await cls.notify("🎮 Игры не найдены")
            return

        data = payload["data"]

        # Старый формат списка строк
        if isinstance(data, list) and all(isinstance(item, str) for item in data):
            games = [{"name": name, "path": name, "running": False} for name in data]
            programs = []
        else:
            games = data.get("games", [])
            programs = data.get("programs", [])

        def safe_callback_data(action: str, name: str) -> str:
            encoded = urllib.parse.quote(str(name), safe="")
            return f"{action}:{encoded[:50]}"

        if not games and not programs:
            await cls.notify("🎮 Игры и программы не найдены")
            return

        buttons = []

        def create_button(item: dict, icon: str) -> InlineKeyboardButton:
            name = item.get("name", "Неизвестно")
            running = item.get("running", False)

            if running:
                action = "close"
                label = f"❌ Закрыть {name}"
            else:
                action = "launch"
                label = f"▶️ Открыть {name}"

            return InlineKeyboardButton(label, callback_data=safe_callback_data(action, name))

        # Игры
        for game in games:
            buttons.append([create_button(game, "🎮")])

        # Программы
        for program in programs:
            buttons.append([create_button(program, "📦")])

        markup = InlineKeyboardMarkup(buttons)

        if cls.bot and cls.chat_id:
            try:
                await cls.bot.send_message(
                    chat_id=cls.chat_id,
                    text="Выберите действие для приложения:",
                    reply_markup=markup
                )
            except TelegramError as e:
                logger.error(f"Ошибка при отправке inline-кнопок: {e}")


    @classmethod
    async def on_pong(cls, _):
        await cls.notify("🌿 Агент на связи")

    @classmethod
    async def on_launch(cls, payload: dict) -> None:
        status = payload.get('status', '')
        name = payload.get('name', 'Неизвестный файл')
        message = payload.get('message', 'Неизвестная ошибка')

        if status == 'error':
            await cls.notify(f"Ошибка при запуске: {message}")
        elif status == 'not_found':
            await cls.notify(f"Файл не найден: {name}")
        else:
            await cls.notify(f"Успешный запуск: {name}")
