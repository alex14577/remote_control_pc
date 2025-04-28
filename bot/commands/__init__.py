# bot/commands/__init__.py

from bot.commands.info_handler import InfoHandler
from bot.commands.list_handler import ListHandler
from bot.commands.simple_handler import SimpleCommandHandler
from bot.commands.launch_handler import LaunchHandler

COMMANDS = {
    "info": InfoHandler(),
    "list": ListHandler(),
    "ping": SimpleCommandHandler("ping", "Пинг"),
    "reboot": SimpleCommandHandler("reboot", "Перезапуск"),
    "shutdown": SimpleCommandHandler("shutdown", "Выключение"),
    "rescan_games": SimpleCommandHandler("rescan_games", "Пересканировать игры")
}
