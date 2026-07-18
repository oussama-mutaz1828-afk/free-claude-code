"""Agent persona system for injecting specialized AI agent identities."""

from .injection import apply_agent_persona
from .models import AgentDefinition, AgentDivision
from .registry import AgentRegistry, get_agent_registry

__all__ = [
    "AgentDefinition",
    "AgentDivision",
    "AgentRegistry",
    "apply_agent_persona",
    "get_agent_registry",
]
