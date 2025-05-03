import json
import subprocess, os, unicodedata, psutil

from agent.system_info import get_system_info
from agent.scanner import scan_installed
from agent.logger import Logger


logger = Logger().Get("commands")

# Словарь с зарегистрированными командами
handlers = {}

# Хранилище игр
stored_games: dict[str, str] = {}
stored_programs: dict[str, str] = {}

# Декоратор для регистрации команды

def register_command(name):
    def decorator(fn):
        handlers[name] = fn
        return fn
    logger.info(f"Command '{name}' was registered")
    return decorator

# Команды агента

@register_command("get_info")
async def handle_get_info(_, websocket):
    info = get_system_info()
    logger.info("Execute get_info")
    await websocket.send(json.dumps({"type": "info_reply", "data": info}))

@register_command("list_games")
async def handle_list_games(_, websocket):
    logger.info("Execute list_games")

    data = scan_installed()
    logger.info(f"scanning complete: {data}")

    stored_games.clear()
    stored_games.update({g["name"]: g for g in data["games"]})
    stored_programs.clear()
    stored_programs.update({p["name"]: p for p in data["programs"]})

    logger.info(f"Games: {stored_games}")
    logger.info(f"Programs: {stored_programs}")

    await websocket.send(json.dumps({
        "type": "games_list",
        "data": {
            "games": list(stored_games.values()),
            "programs": list(stored_programs.values())
        }
    }))

@register_command("rescan_games")
async def handle_rescan_games(_, websocket):
    logger.info("Execute rescan_games")
    
    data = scan_installed()
    stored_games.clear()
    stored_games.update({g["name"]: g for g in data["games"]})
    stored_programs.clear()
    stored_programs.update({p["name"]: p for p in data["programs"]})

    logger.info(f"Games: {stored_games}")
    logger.info(f"Programs: {stored_programs}")

    await websocket.send(json.dumps({
        "type": "games_list",
        "data": {
            "games": list(stored_games.values()),
            "programs": list(stored_programs.values())
        }
    }))

@register_command("ping")
async def handle_ping(_, websocket):
    logger.info("Execute ping")
    await websocket.send(json.dumps({"type": "pong"}))

@register_command("shutdown")
async def handle_shutdown(_, websocket):
    logger.info("Execute shutdown")
    logger.info("⏹️ Выключение (заглушка)")
    # os.system("shutdown /s /t 1")

@register_command("reboot")
async def handle_reboot(_, websocket):
    logger.info("Execute reboot")
    logger.info("🔄 Перезагрузка (заглушка)")
    # os.system("shutdown /r /t 1")


@register_command("launch_game")
async def handle_launch_game(data, websocket):
    logger.info("Command received: launch_game")

    name = data.get("name")
    logger.info(f"Requested name: '{name}'")

    entry = stored_games.get(name) or stored_programs.get(name)
    logger.info(f"Entry resolved: {entry}")

    if not entry:
        logger.info("No matching entry found, sending not_found")
        await websocket.send(json.dumps({
            "type": "launch_ack",
            "status": "not_found",
            "name": name
        }))
        return

    path = entry.get("path")
    logger.info(f"Resolved path: {path}")

    if not path:
        logger.info("Entry has no path, sending not_found")
        await websocket.send(json.dumps({
            "type": "launch_ack",
            "status": "not_found",
            "name": name
        }))
        return

    try:
        if path.startswith("steam://"):
            logger.info("Launching via Steam URL")
            subprocess.Popen(["explorer", f"{path}/bp"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

        elif path.lower().endswith(".lnk"):
            logger.info("Launching .lnk shortcut")
            subprocess.Popen(["explorer", path], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

        else:
            folder = os.path.dirname(path)
            logger.info(f"Launching direct executable in: {folder}")
            subprocess.Popen([path], cwd=folder, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

        logger.info(f"✅ Launch successful: {name}")
        await websocket.send(json.dumps({
            "type": "launch_ack",
            "status": "ok",
            "name": name
        }))

    except Exception as e:
        logger.error(f"❌ Launch error: {e}")
        await websocket.send(json.dumps({
            "type": "launch_ack",
            "status": "error",
            "name": name,
            "message": str(e)
        }))
        
def normalize_name(name: str) -> str:
    if not name:
        return ""
    name = name.lower()
    name = name.replace('µ', 'u')
    name = unicodedata.normalize('NFKD', name).encode('ascii', 'ignore').decode('ascii')
    name = name.replace('.exe', '')
    return name.strip()

@register_command("close_game")
async def handle_close_game(data, websocket):
    name = data.get("name")
    entry = stored_games.get(name) or stored_programs.get(name)

    if not entry:
        await websocket.send(json.dumps({"type": "close_ack", "status": "not_found", "name": name}))
        return

    path = entry.get("path")
    if not path:
        await websocket.send(json.dumps({"type": "close_ack", "status": "not_found", "name": name}))
        return

    # Определяем исполняемый файл
    if path.startswith("steam://"):
        # Steam-игры закрывать напрямую нельзя через taskkill
        await websocket.send(json.dumps({"type": "close_ack", "status": "unsupported", "name": name}))
        return

    try:
        # Если ярлык .lnk — вытаскиваем реальный exe
        if path.lower().endswith(".lnk"):
            import pylnk3
            with open(path, "rb") as f:
                lnk = pylnk3.parse(f)
                target = lnk.path
                executable = os.path.basename(target)
        else:
            executable = os.path.basename(path)

        executable = normalize_name(executable)

        # Ищем и убиваем процесс
        closed = False
        for proc in psutil.process_iter(['name']):
            try:
                proc_name = proc.info['name']
                if proc_name and normalize_name(proc_name) == executable:
                    proc.terminate()
                    closed = True
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue

        if closed:
            await websocket.send(json.dumps({"type": "close_ack", "status": "ok", "name": name}))
        else:
            await websocket.send(json.dumps({"type": "close_ack", "status": "not_found", "name": name}))

    except Exception as e:
        logger.error(f"❌ Ошибка закрытия процесса: {e}")
        await websocket.send(json.dumps({"type": "close_ack", "status": "error", "name": name, "message": str(e)}))



# Главная точка входа: вызывается из agent.py
async def handle_command(message, websocket):
    logger.info(f"📥 Сообщение от сервера: {message}")
    command = message.get("type")
    handler = handlers.get(command)
    if handler:
        await handler(message, websocket)
    else:
        logger.error(f"⚠️ Неизвестная команда: {command}")
