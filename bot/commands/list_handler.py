# bot/commands/info_handler.py

from bot.commands.base import ICommandHandler

class ListHandler(ICommandHandler):
    command = "list"
    label = "Игры"

    async def handle(self, query, server):
        await server.send_command({"type": "list_games"})
        await query.edit_message_text("🎮 Получен список игр")
