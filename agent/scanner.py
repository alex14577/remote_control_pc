import os
import configparser
from typing import List, Dict
import pylnk3
import psutil
import unicodedata
from pathlib import Path
from logger import Logger

logger = Logger().Get("scanner")

def get_all_desktop_paths() -> List[str]:
    paths = set()

    userprofile = os.environ.get("USERPROFILE")
    if userprofile:
        paths.add(os.path.join(userprofile, "Desktop"))

    paths.add("C:\\Users\\Public\\Desktop")

    base = Path("C:/Users")
    if base.exists():
        for user_dir in base.iterdir():
            desktop = user_dir / "Desktop"
            if desktop.exists():
                paths.add(str(desktop))

    return sorted(paths)


def scan_installed() -> Dict[str, List[Dict[str, str]]]:
    logger.info("Starting scan for installed games and programs...")

    games = []
    programs = []

    def classify(name: str, path: str) -> str:
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
        if not name:
            return ""
        name = name.lower().replace('µ', 'u')
        name = unicodedata.normalize('NFKD', name).encode('ascii', 'ignore').decode('ascii')
        return name.replace('.exe', '').strip()

    def is_running(executable_name: str) -> bool:
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
        if hasattr(lnk, "description") and lnk.description:
            return lnk.description.strip()
        if lnk.path:
            base = os.path.basename(lnk.path)
            name, _ = os.path.splitext(base)
            return name.strip()
        return os.path.splitext(file)[0].strip()

    for desktop_path in get_all_desktop_paths():
        logger.info(f"Scanning desktop: {desktop_path}")
        if not os.path.exists(desktop_path):
            logger.warning(f"Desktop path does not exist: {desktop_path}")
            continue

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
                    logger.error(f"Failed to parse .lnk: {file}: {e}")

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
                    logger.error(f"Failed to parse .url: {file}: {e}")

    result = {
        "games": sorted(games, key=lambda x: x['name'].lower()),
        "programs": sorted(programs, key=lambda x: x['name'].lower())
    }

    logger.info(f"Scan complete: {len(result['games'])} games, {len(result['programs'])} programs.")
    return result
