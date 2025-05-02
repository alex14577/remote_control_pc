# agent/__main__.py

import argparse
import asyncio
import os
import sys
import json

from agent.agent import run_agent

import logging
import io

# Заменить stdout и stderr на UTF-8
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

logging.basicConfig(
    filename="agent.log",
    filemode="a",
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s"
)

print = logging.info


def main():
    parser = argparse.ArgumentParser(description="PC Agent")
    parser.add_argument("-f", "--file", required=True, help="Путь до config.json")
    args = parser.parse_args()

    config_path = args.file
    if not os.path.isfile(config_path):
        print(f"❌ Конфиг не найден: {config_path}")
        sys.exit(1)

    with open(config_path, "r", encoding="utf-8") as f:
        config = json.load(f)

    host = config.get("host", "0.0.0.0")
    port = config.get("port", 33444)

    asyncio.run(run_agent(host, port))


if __name__ == "__main__":
    main()
