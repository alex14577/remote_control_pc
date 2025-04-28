# PC Control Bot

**PC Control Bot** — это Telegram-бот и агент для удалённого управления вашим ПК.

## 📦 Возможности

- 📋 Просмотр списка установленных игр и программ
- 🔄 Перезагрузка и выключение ПК
- 🔃 Перескан программ
- ℹ️ Получение системной информации
- 🌐 WebSocket-соединение с агентом
- 🚀 Wake-on-LAN для удалённого включения

## 🧰 Установка

### Установка из GitHub:
```bash
pip install git+https://github.com/yourusername/pc-control-bot.git
```

### Локальная установка:
```bash
git clone https://github.com/yourusername/pc-control-bot.git
cd pc-control-bot
pip install .
```

## 🚀 Запуск

### Бот:
```bash
pc-bot -f bot/config.json
```

### Агент:
```bash
pc-agent -f agent/config.json
```

## 🗂 Структура
- `bot/` — Telegram бот
- `agent/` — агент на ПК
- `main.py` — точка входа
- `pyproject.toml` — конфигурация сборки
- `setup.cfg`, `LICENSE`, `README.md` — мета-информация

## 📜 Лицензия
MIT License © 2025 Morgan