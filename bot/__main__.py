import asyncio
import argparse
import os
import sys

from bot.config import ConfigProvider
from bot.telegram_server import run_telegram
from bot.services.agent_client import AgentCommandHandler
from bot.services.ws_client import WebSocketClient
from bot.services.agent_client import run_agent_client

def main():
    parser = argparse.ArgumentParser(description="PC Control Bot")
    parser.add_argument("-f", "--file", required=True, help="Path to config.json")
    args = parser.parse_args()

    config_path = args.file
    if not os.path.isfile(config_path):
        print(f"❌ Конфиг не найден: {config_path}")
        sys.exit(1)

    config = ConfigProvider(config_path)
    chat_id = config.get("telegram_chat_id")
    if not chat_id:
        print("❌ В config.json отсутствует telegram_chat_id")
        sys.exit(1)

    try:
        loop = asyncio.get_running_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

    loop.create_task(start(config, chat_id))
    loop.run_forever()


async def start(config, chat_id):
    
    ws_client = WebSocketClient(config.get("server_url"))
    await asyncio.gather(
        run_telegram(config, chat_id, ws_client),
        run_agent_client(ws_client)
    )


if __name__ == "__main__":
    main()
