"""Tests for the agent registry."""

from free_claude_code.agents.models import AgentDefinition
from free_claude_code.agents.registry import (
    DIVISIONS,
    AgentRegistry,
    get_agent_registry,
)


def _make_agent(agent_id: str, division: str = "engineering") -> AgentDefinition:
    return AgentDefinition(
        agent_id=agent_id,
        name=agent_id.replace("-", " ").title(),
        description=f"Test {agent_id}",
        division=division,
        emoji="🧪",
        vibe="Testing",
        system_prompt=f"You are {agent_id}.",
    )


class TestAgentRegistry:
    def test_empty_registry(self):
        reg = AgentRegistry([])
        assert len(reg) == 0
        assert reg.agents == []
        assert reg.agent_ids == []

    def test_register_and_get(self):
        agent = _make_agent("test-agent")
        reg = AgentRegistry([agent])
        assert len(reg) == 1
        assert "test-agent" in reg
        assert reg.get("test-agent") is agent

    def test_get_missing_returns_none(self):
        reg = AgentRegistry([])
        assert reg.get("nonexistent") is None

    def test_agent_ids_sorted(self):
        agents = [
            _make_agent("c-agent"),
            _make_agent("a-agent"),
            _make_agent("b-agent"),
        ]
        reg = AgentRegistry(agents)
        assert reg.agent_ids == ["a-agent", "b-agent", "c-agent"]

    def test_agents_sorted_by_id(self):
        agents = [_make_agent("z"), _make_agent("a"), _make_agent("m")]
        reg = AgentRegistry(agents)
        names = [a.agent_id for a in reg.agents]
        assert names == ["a", "m", "z"]

    def test_list_by_division(self):
        agents = [
            _make_agent("eng1", "engineering"),
            _make_agent("sec1", "security"),
            _make_agent("eng2", "engineering"),
        ]
        reg = AgentRegistry(agents)
        eng = reg.list_by_division("engineering")
        assert len(eng) == 2
        assert all(a.division == "engineering" for a in eng)

    def test_list_by_division_empty(self):
        reg = AgentRegistry([_make_agent("a")])
        assert reg.list_by_division("nonexistent") == []

    def test_contains(self):
        reg = AgentRegistry([_make_agent("present")])
        assert "present" in reg
        assert "absent" not in reg

    def test_divisions(self):
        reg = AgentRegistry([])
        assert reg.divisions is DIVISIONS
        assert len(reg.divisions) >= 4


class TestGetAgentRegistry:
    def test_returns_populated_registry(self):
        reg = get_agent_registry()
        assert len(reg) >= 10

    def test_singleton(self):
        a = get_agent_registry()
        b = get_agent_registry()
        assert a is b

    def test_known_agents_present(self):
        reg = get_agent_registry()
        assert "software-architect" in reg
        assert "code-reviewer" in reg
        assert "security-architect" in reg
        assert "test-engineer" in reg

    def test_agents_have_system_prompts(self):
        reg = get_agent_registry()
        for agent in reg.agents:
            assert agent.system_prompt, f"{agent.agent_id} has empty system_prompt"
