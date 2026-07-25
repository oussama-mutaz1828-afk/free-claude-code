"""Command registry: loads and indexes all bundled command definitions."""

from functools import lru_cache
from pathlib import Path

from .loader import load_commands_from_directory
from .models import CommandDefinition

DEFINITIONS_DIR = Path(__file__).parent / "definitions"


class CommandRegistry:
    """Thread-safe, immutable registry of all available commands."""

    def __init__(self, commands: list[CommandDefinition]) -> None:
        self._commands = {cmd.command_id: cmd for cmd in commands}

    @property
    def command_ids(self) -> list[str]:
        return sorted(self._commands)

    @property
    def commands(self) -> list[CommandDefinition]:
        return [self._commands[cid] for cid in self.command_ids]

    def get(self, command_id: str) -> CommandDefinition | None:
        return self._commands.get(command_id)

    def search(self, query: str) -> list[CommandDefinition]:
        """Search commands by id or description substring (case-insensitive)."""
        q = query.lower()
        return [
            c
            for c in self.commands
            if q in c.command_id.lower() or q in c.description.lower()
        ]

    def __len__(self) -> int:
        return len(self._commands)

    def __contains__(self, command_id: str) -> bool:
        return command_id in self._commands


@lru_cache
def get_command_registry() -> CommandRegistry:
    """Return the singleton command registry loaded from bundled definitions."""
    commands = load_commands_from_directory(DEFINITIONS_DIR)
    return CommandRegistry(commands)
