# bot/telegram_server.py

import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder,
    CallbackQueryHandler,
    CommandHandler,
    ContextTypes,
)

from bot.commands import COMMANDS
from bot.services.telegram_notifier import TelegramNotifier
from telegram import ReplyKeyboardMarkup
from telegram.ext import MessageHandler, filters

from bot.commands.launch_handler import LaunchHandler
from bot.commands.close_handler import CloseHandler

logger = logging.getLogger(__name__)

def build_reply_menu():
    return ReplyKeyboardMarkup([["📋 Меню"]], resize_keyboard=True)

async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.text == "📋 Меню":
        await update.message.reply_text(
            "Выберите команду:",
            reply_markup=build_menu()  # это твой InlineKeyboardMarkup
        )

def build_menu():
    buttons = [
        [InlineKeyboardButton(cmd.label, callback_data=cmd.command)]
        for cmd in COMMANDS.values()
    ]
    return InlineKeyboardMarkup(buttons)


def create_handlers(agent_client):
    async def handle_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
        query = update.callback_query
        await query.answer()
        handler = COMMANDS.get(query.data)
        if handler:
            await handler(query, agent_client)
            # try:
            #     await query.edit_message_reply_markup(reply_markup=build_menu())
            # except Exception as e:
            #     logger.warning("Не удалось обновить меню", exc_info=e)
        else:
            await query.edit_message_text("Неизвестная команда")

    async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
        await update.message.reply_text(
            "Выберите команду:",
            reply_markup=build_reply_menu()
        )


    return start, handle_menu


async def run_telegram(config, chat_id, agent_client):
    token = config.get("telegram_token")
    if not token:
        raise ValueError("❌ Не указан telegram_token в конфиге")

    TelegramNotifier.configure(token, chat_id)

    app = ApplicationBuilder().token(token).build()
    start_handler, menu_handler = create_handlers(agent_client)
    launch_handler = LaunchHandler(agent_client)
    close_handler = CloseHandler(agent_client)

    app.add_handler(CommandHandler("start", start_handler))
    
    app.add_handler(CallbackQueryHandler(launch_handler, pattern="^launch:"))
    app.add_handler(CallbackQueryHandler(close_handler, pattern="^close:"))
    app.add_handler(CallbackQueryHandler(menu_handler))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))

    await app.initialize()
    await app.start()
    print("✅ Telegram polling запущен")

    await app.updater.initialize()
    await app.updater.start_polling()
