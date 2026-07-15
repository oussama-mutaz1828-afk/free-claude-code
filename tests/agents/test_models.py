"""Tests for agent data models."""

from free_claude_code.agents.models import AgentDefinition, AgentDivision


class TestAgentDivision:
    def test_create_division(self):
        div = AgentDivision(
            division_id="engineering",
            label="Engineering",
            icon="Code",
            color="#3B82F6",
        )
        assert div.division_id == "engineering"
        assert div.label == "Engineering"
        assert div.icon == "Code"
        assert div.color == "#3B82F6"

    def test_division_is_frozen(self):
        div = AgentDivision("eng", "Eng", "Code", "#000")
        try:
            div.division_id = "other"  # type: ignore[misc]
            raise AssertionError("Should have raised")
        except AttributeError:
            pass


class TestAgentDefinition:
    def test_create_agent(self):
        agent = AgentDefinition(
            agent_id="software-architect",
            name="Software Architect",
            description="Expert architect",
            division="engineering",
            emoji="🏛️",
            vibe="Designs systems",
            system_prompt="You are a software architect.",
        )
        assert agent.agent_id == "software-architect"
        assert agent.name == "Software Architect"
        assert agent.description == "Expert architect"
        assert agent.division == "engineering"
        assert agent.emoji == "🏛️"
        assert agent.vibe == "Designs systems"
        assert agent.system_prompt == "You are a software architect."

    def test_agent_is_frozen(self):
        agent = AgentDefinition("id", "n", "d", "div", "", "", "prompt")
        try:
            agent.name = "other"  # type: ignore[misc]
            raise AssertionError("Should have raised")
        except AttributeError:
            pass
