from bot.services.ws_client import WebSocketClient, AgentCommandHandler
from bot.services.telegram_notifier import TelegramNotifier

__all__ = ["create_agent", "run_agent_client"]


class AgentHandlerRegistry:
    def __init__(self):
        self._handlers = {}

    def handler(self, message_type):
        def decorator(fn):
            self._handlers[message_type] = fn
            return fn
        return decorator

    def apply_to(self, agent_handler: AgentCommandHandler):
        for message_type, fn in self._handlers.items():
            agent_handler.register(message_type, fn)

# Словарь зарегистрированных хендлеров
agent_handlers = {}

def agent_handler(message_type):
    def decorator(fn):
        agent_handlers[message_type] = fn
        return fn
    return decorator

@agent_handler("info_reply")
async def handle_info_reply(payload):
    await TelegramNotifier.on_info(payload)

@agent_handler("games_list")
async def handle_games_list(payload):
    await TelegramNotifier.on_games(payload)

@agent_handler("pong")
async def handle_pong(payload):
    await TelegramNotifier.on_pong(payload)

@agent_handler("launch_ack")
async def handle_launch(payload):
    await TelegramNotifier.on_launch(payload)

def create_handler(client):
    handler = AgentCommandHandler(client)
    for message_type, fn in agent_handlers.items():
        handler.register(message_type, fn)
    return handler


async def run_agent_client(client):
    handler = create_handler(client)
    await handler.run()
