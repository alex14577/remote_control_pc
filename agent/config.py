# agent/config.py
import json
import sys


class ConfigProvider:
    def __init__(self, path: str):
        self.config = self._load_config(path)

    def _load_config(self, path: str) -> dict:
        try:
            with open(path, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            print(f"❌ Ошибка загрузки конфигурации агента: {e}")
            sys.exit(1)

    def get(self, key: str, default=None):
        return self.config.get(key, default)
