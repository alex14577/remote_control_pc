# agent/commands/games.py

import json, os, subprocess
import pylnk3, psutil

from agent.logger import Logger
from agent.scanner import scan_installed
from agent.commands.shared import normalize_name, is_process_running, launch_with_task
from agent.agent import Agent

logger = Logger().Get("games")

stored_games: dict[str, dict] = {}
stored_programs: dict[str, dict] = {}

class ListGamesCommand:
    def __init__(self, agent: Agent):
        agent.register("list_games")(self.handle)
        agent.register("rescan_games")(self.handle)

    async def handle(self, _, websocket):
        logger.info("Execute list/rescan")
        data = scan_installed()

        stored_games.clear()
        stored_programs.clear()

        stored_games.update({g["name"]: g for g in data["games"]})
        stored_programs.update({p["name"]: p for p in data["programs"]})

        logger.info(f"Games: {len(stored_games)}, Programs: {len(stored_programs)}")
        await websocket.send(json.dumps({
            "type": "games_list",
            "data": {
                "games": list(stored_games.values()),
                "programs": list(stored_programs.values())
            }
        }))


class LaunchGameCommand:
    def __init__(self, agent: Agent):
        agent.register("launch_game")(self.handle)

    async def handle(self, data, websocket):
        name = data.get("name")
        logger.info(f"Launch request: {name}")
        entry = stored_games.get(name) or stored_programs.get(name)

        if not entry or not entry.get("path"):
            logger.info("Entry not found or no path")
            await websocket.send(json.dumps({"type": "launch_ack", "status": "not_found", "name": name}))
            return

        path = entry["path"]
        if not path.startswith("steam://") and is_process_running(path):
            logger.info("Already running")
            await websocket.send(json.dumps({"type": "launch_ack", "status": "already_running", "name": name}))
            return

        try:
            if path.startswith("steam://"):
                subprocess.Popen(["explorer", f"{path}/bp"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            else:
                launch_with_task(path)
            logger.info(f"Launched: {name}")
            await websocket.send(json.dumps({"type": "launch_ack", "status": "ok", "name": name}))
        except Exception as e:
            logger.error(f"Launch failed: {e}")
            await websocket.send(json.dumps({"type": "launch_ack", "status": "error", "name": name, "message": str(e)}))


class CloseGameCommand:
    def __init__(self, agent: Agent):
        agent.register("close_game")(self.handle)

    async def handle(self, data, websocket):
        name = data.get("name")
        entry = stored_games.get(name) or stored_programs.get(name)
        if not entry or not entry.get("path"):
            await websocket.send(json.dumps({"type": "close_ack", "status": "not_found", "name": name}))
            return

        path = entry["path"]
        if path.startswith("steam://"):
            await websocket.send(json.dumps({"type": "close_ack", "status": "unsupported", "name": name}))
            return

        try:
            if path.lower().endswith(".lnk"):
                with open(path, "rb") as f:
                    target = pylnk3.parse(f).path
                    executable = os.path.basename(target)
            else:
                executable = os.path.basename(path)

            exe = normalize_name(executable)
            closed = False
            for proc in psutil.process_iter(['name']):
                if proc.info['name'] and normalize_name(proc.info['name']) == exe:
                    proc.terminate()
                    closed = True

            status = "ok" if closed else "not_found"
            await websocket.send(json.dumps({"type": "close_ack", "status": status, "name": name}))

        except Exception as e:
            logger.error(f"Close failed: {e}")
            await websocket.send(json.dumps({"type": "close_ack", "status": "error", "name": name, "message": str(e)}))
