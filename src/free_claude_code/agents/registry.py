"""Agent registry: loads and indexes all bundled agent definitions."""

from functools import lru_cache
from pathlib import Path

from .loader import load_agents_from_directory
from .models import AgentDefinition, AgentDivision

DEFINITIONS_DIR = Path(__file__).parent / "definitions"

DIVISIONS: tuple[AgentDivision, ...] = (
    AgentDivision("engineering", "Engineering", "Code", "#3B82F6"),
    AgentDivision("security", "Security", "ShieldCheck", "#EF4444"),
    AgentDivision("testing", "Testing", "FlaskConical", "#F59E0B"),
    AgentDivision("design", "Design", "PenTool", "#EC4899"),
    AgentDivision("sales", "Sales", "Handshake", "#10B981"),
    AgentDivision("marketing", "Marketing", "Megaphone", "#F97316"),
    AgentDivision("review", "Code Review", "Eye", "#8B5CF6"),
    AgentDivision("build", "Build Resolution", "Hammer", "#6366F1"),
    AgentDivision("architecture", "Architecture", "Building", "#0EA5E9"),
    AgentDivision("devops", "DevOps & Infra", "Server", "#14B8A6"),
    AgentDivision("research", "Research & Analysis", "Search", "#A855F7"),
    AgentDivision("ml", "Machine Learning", "Brain", "#F43F5E"),
    AgentDivision("ops", "Operations", "Settings", "#64748B"),
    AgentDivision("opensource", "Open Source", "GitBranch", "#22C55E"),
)


class AgentRegistry:
    """Thread-safe, immutable registry of all available agent personas."""

    def __init__(self, agents: list[AgentDefinition]) -> None:
        self._agents = {agent.agent_id: agent for agent in agents}

    @property
    def agent_ids(self) -> list[str]:
        return sorted(self._agents)

    @property
    def agents(self) -> list[AgentDefinition]:
        return [self._agents[aid] for aid in self.agent_ids]

    def get(self, agent_id: str) -> AgentDefinition | None:
        return self._agents.get(agent_id)

    def list_by_division(self, division: str) -> list[AgentDefinition]:
        return [a for a in self.agents if a.division == division]

    @property
    def divisions(self) -> tuple[AgentDivision, ...]:
        return DIVISIONS

    def __len__(self) -> int:
        return len(self._agents)

    def __contains__(self, agent_id: str) -> bool:
        return agent_id in self._agents


@lru_cache
def get_agent_registry() -> AgentRegistry:
    """Return the singleton agent registry loaded from bundled definitions."""
    agents = load_agents_from_directory(DEFINITIONS_DIR)
    return AgentRegistry(agents)
