# agent/commands/system.py

import json
from agent.logger import Logger
from agent.system_info import get_system_info
from agent.agent import Agent

logger = Logger().Get("system")

class GetInfoCommand:
    def __init__(self, agent: Agent):
        agent.register("get_info")(self.handle)

    async def handle(self, _, websocket):
        logger.info("Execute get_info")
        await websocket.send(json.dumps({
            "type": "info_reply",
            "data": get_system_info()
        }))


class PingCommand:
    def __init__(self, agent: Agent):
        agent.register("ping")(self.handle)

    async def handle(self, _, websocket):
        logger.info("Execute ping")
        await websocket.send(json.dumps({"type": "pong"}))


class ShutdownCommand:
    def __init__(self, agent: Agent):
        agent.register("shutdown")(self.handle)

    async def handle(self, _, websocket):
        logger.info("Execute shutdown (stub)")
        # os.system("shutdown /s /t 1")
        await websocket.send(json.dumps({"type": "shutdown_ack", "status": "ok"}))


class RebootCommand:
    def __init__(self, agent: Agent):
        agent.register("reboot")(self.handle)

    async def handle(self, _, websocket):
        logger.info("Execute reboot (stub)")
        # os.system("shutdown /r /t 1")
        await websocket.send(json.dumps({"type": "reboot_ack", "status": "ok"}))
