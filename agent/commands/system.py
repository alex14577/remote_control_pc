import json
from agent.commands import register_command
from agent.system_info import get_system_info
from agent.logger import Logger

logger = Logger().Get("system")

@register_command("get_info")
async def handle_get_info(_, websocket):
    logger.info("Execute get_info")
    await websocket.send(json.dumps({"type": "info_reply", "data": get_system_info()}))

@register_command("ping")
async def handle_ping(_, websocket):
    logger.info("Execute ping")
    await websocket.send(json.dumps({"type": "pong"}))

@register_command("shutdown")
async def handle_shutdown(_, websocket):
    logger.info("Execute shutdown (stub)")
    # os.system("shutdown /s /t 1")

@register_command("reboot")
async def handle_reboot(_, websocket):
    logger.info("Execute reboot (stub)")
    # os.system("shutdown /r /t 1")
