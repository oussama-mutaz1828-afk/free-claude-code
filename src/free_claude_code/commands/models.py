"""Data models for command definitions."""

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class CommandDefinition:
    """A single command parsed from a markdown definition file."""

    command_id: str
    description: str
    argument_hint: str
    instructions: str
