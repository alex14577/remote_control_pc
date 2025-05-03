import logging
import os
from enum import Enum
from pathlib import Path
from typing import List, Optional


class Logger:
    _instance: Optional["Logger"] = None
    loggers: List[logging.Logger] = []

    class Level(Enum):
        INFO = logging.INFO
        ERROR = logging.ERROR

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self, level: "Logger.Level" = Level.INFO, file: Optional[Path] = None):
        if hasattr(self, "_initialized") and self._initialized:
            return  # предотвратить повторную инициализацию singleton

        self.level = level.value
        self.file = file
        self._initialized = True

    def Get(self, name: str = "root") -> logging.Logger:
        logger = logging.getLogger(name)
        logger.setLevel(self.level)

        formatter = logging.Formatter(
            fmt='%(name)-18s | %(filename)s:%(lineno)-5d | %(asctime)s | %(levelname)-5s | %(message)s',
            datefmt='%Y-%m-%d | %H:%M:%S'
        )

        if logger.hasHandlers():
            logger.handlers.clear()

        # Консольный вывод
        stream_handler = logging.StreamHandler()
        stream_handler.setFormatter(formatter)
        logger.addHandler(stream_handler)

        # Файл, если указан
        if self.file:
            self.file.parent.mkdir(parents=True, exist_ok=True)
            file_handler = logging.FileHandler(self.file, encoding="utf-8")
            file_handler.setFormatter(formatter)
            logger.addHandler(file_handler)

        if logger not in self.loggers:
            self.loggers.append(logger)

        return logger
