# agent/commands/__init__.py

from agent.agent import Agent

from agent.commands.system import (
    GetInfoCommand,
    PingCommand,
    ShutdownCommand,
    RebootCommand,
)

from agent.commands.games import (
    ListGamesCommand,
    LaunchGameCommand,
    CloseGameCommand,
)


def create_agent() -> Agent:
    agent = Agent()

    # Системные команды
    GetInfoCommand(agent)
    PingCommand(agent)
    ShutdownCommand(agent)
    RebootCommand(agent)

    # Игровые команды
    ListGamesCommand(agent)
    LaunchGameCommand(agent)
    CloseGameCommand(agent)

    return agent
