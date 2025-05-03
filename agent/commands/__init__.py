from agent.logger import Logger
import importlib
import pkgutil

logger = Logger().Get("commands")

# Хранилище зарегистрированных обработчиков
handlers = {}

def register_command(name):
    def decorator(fn):
        handlers[name] = fn
        logger.info(f"Registered command: {name}")
        return fn
    return decorator

# 💡 Импортируем все подмодули commands после объявления register_command
for loader, name, _ in pkgutil.iter_modules(__path__):
    importlib.import_module(f"{__name__}.{name}")

# Обработчик всех входящих команд
async def handle_command(message, websocket):
    logger.info(f"📥 Incoming message: {message}")
    command = message.get("type")
    handler = handlers.get(command)
    if handler:
        await handler(message, websocket)
    else:
        logger.error(f"⚠️ Unknown command: {command}")
