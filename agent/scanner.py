import os
import configparser
from typing import List, Dict
import pylnk3
import psutil
import unicodedata

def scan_installed() -> Dict[str, List[Dict[str, str]]]:
    """
    Сканиует ярлыки (.lnk) и URL (.url) на рабочем столе,
    определяет запущенные программы и игры.
    Сохраняет путь к ярлыку, если это не Steam-ссылка.
    """

    desktop_path = os.path.join(os.environ.get("USERPROFILE", ""), "Desktop")
    games = []
    programs = []

    if not os.path.exists(desktop_path):
        return {"games": [], "programs": []}

    def classify(name: str, path: str) -> str:
        """Классифицирует элемент как игру или программу."""
        game_keywords = [
            "steam://", "rungameid", "epic", "uplay", "battle.net", "origin", "gog", "play", "game",
            "launcher", "riot", "valorant", "pubg", "counter-strike", "csgo", "dota", "league", "minecraft",
            "roblox", "apex", "elden", "warzone", "overwatch", "halo", "call of duty", "gta", "cyberpunk", "Remnant2"
        ]
        prog_keywords = [
            "discord", "telegram", "obs", "chrome", "firefox", "browser", "manager", "vpn", "notepad",
            "editor", "visual studio", "vscode", "steam.exe", "client", "microsoft", "office", "excel",
            "word", "teams", "zoom", "spotify", "youtube", "music", "studio", "windows tools"
        ]
        lower = (name + " " + path).lower()

        if any(word in lower for word in game_keywords):
            return "game"
        if any(word in lower for word in prog_keywords):
            return "program"
        return "game" if "\\games\\" in path.lower() else "program"

    def normalize_name(name: str) -> str:
        """Нормализует имя для сравнения процессов."""
        if not name:
            return ""
        name = name.lower()
        name = name.replace('µ', 'u')
        name = unicodedata.normalize('NFKD', name).encode('ascii', 'ignore').decode('ascii')
        name = name.replace('.exe', '')
        return name.strip()

    def is_running(executable_name: str) -> bool:
        """Проверяет, запущен ли процесс с данным именем."""
        expected = normalize_name(executable_name)

        for proc in psutil.process_iter(['name']):
            try:
                proc_name = proc.info['name']
                if proc_name and normalize_name(proc_name) == expected:
                    return True
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue
        return False

    def get_shortcut_name(lnk, file: str) -> str:
        """Определяет красивое имя ярлыка."""
        if hasattr(lnk, "description") and lnk.description:
            return lnk.description.strip()
        if lnk.path:
            base = os.path.basename(lnk.path)
            name, _ = os.path.splitext(base)
            return name.strip()
        return os.path.splitext(file)[0].strip()

    for file in os.listdir(desktop_path):
        full_path = os.path.join(desktop_path, file)

        if file.lower().endswith(".lnk"):
            try:
                with open(full_path, "rb") as f:
                    lnk = pylnk3.parse(f)
                    target = lnk.path

                if target:
                    name = get_shortcut_name(lnk, file)

                    if target.startswith("steam://"):
                        entry = {"name": name, "path": target, "running": False}
                    else:
                        executable = os.path.basename(target)
                        running = is_running(executable)
                        entry = {"name": name, "path": full_path, "running": running}

                    (games if classify(name, target) == "game" else programs).append(entry)

            except Exception as e:
                print(f"⚠️ Не удалось обработать {file} как .lnk: {e}")

        elif file.lower().endswith(".url"):
            try:
                config = configparser.ConfigParser()
                config.read(full_path, encoding="utf-8")
                url = config.get("InternetShortcut", "URL", fallback=None)

                if url:
                    name = os.path.splitext(file)[0].strip()
                    entry = {"name": name, "path": url, "running": False}
                    (games if classify(name, url) == "game" else programs).append(entry)

            except Exception as e:
                print(f"⚠️ Не удалось обработать {file} как .url: {e}")

    return {
        "games": sorted(games, key=lambda x: x['name'].lower()),
        "programs": sorted(programs, key=lambda x: x['name'].lower())
    }
