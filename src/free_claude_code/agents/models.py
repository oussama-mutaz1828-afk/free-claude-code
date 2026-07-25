"""Data models for agent persona definitions."""

from dataclasses import dataclass, field


@dataclass(frozen=True, slots=True)
class AgentDivision:
    """Metadata for a group of related agents."""

    division_id: str
    label: str
    icon: str
    color: str


@dataclass(frozen=True, slots=True)
class AgentDefinition:
    """A single agent persona parsed from a markdown definition file."""

    agent_id: str
    name: str
    description: str
    division: str
    emoji: str
    vibe: str
    system_prompt: str
    tools: tuple[str, ...] = field(default_factory=tuple)
    model: str = ""
