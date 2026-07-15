"""Tests for agent persona system prompt injection."""

from free_claude_code.agents.injection import apply_agent_persona
from free_claude_code.agents.models import AgentDefinition
from free_claude_code.agents.registry import AgentRegistry
from free_claude_code.core.anthropic.models import Message, MessagesRequest


def _make_registry(*agents: AgentDefinition) -> AgentRegistry:
    return AgentRegistry(list(agents))


def _make_agent(
    agent_id: str = "test-agent", prompt: str = "You are a test agent."
) -> AgentDefinition:
    return AgentDefinition(
        agent_id=agent_id,
        name="Test Agent",
        description="Testing",
        division="engineering",
        emoji="🧪",
        vibe="Testing",
        system_prompt=prompt,
    )


def _make_request(
    system: str | list[object] | None = None,
) -> MessagesRequest:
    return MessagesRequest(
        model="claude-sonnet-4-20250514",
        messages=[Message(role="user", content="Hello")],
        system=system,
    )


class TestApplyAgentPersona:
    def test_empty_persona_returns_unchanged(self):
        req = _make_request(system="Original")
        result = apply_agent_persona(req, "")
        assert result is req

    def test_unknown_persona_returns_unchanged(self):
        registry = _make_registry()
        req = _make_request(system="Original")
        result = apply_agent_persona(req, "nonexistent", registry=registry)
        assert result is req

    def test_inject_into_none_system(self):
        agent = _make_agent()
        registry = _make_registry(agent)
        req = _make_request(system=None)
        result = apply_agent_persona(req, "test-agent", registry=registry)
        assert result.system == "You are a test agent."

    def test_inject_prepends_to_string_system(self):
        agent = _make_agent()
        registry = _make_registry(agent)
        req = _make_request(system="Original system prompt")
        result = apply_agent_persona(req, "test-agent", registry=registry)
        assert isinstance(result.system, str)
        assert result.system.startswith("You are a test agent.")
        assert "Original system prompt" in result.system

    def test_inject_prepends_to_list_system(self):
        agent = _make_agent()
        registry = _make_registry(agent)
        existing_blocks = [{"type": "text", "text": "Existing block"}]
        req = _make_request(system=existing_blocks)
        result = apply_agent_persona(req, "test-agent", registry=registry)
        assert isinstance(result.system, list)
        assert len(result.system) == 2
        assert result.system[0]["type"] == "text"
        assert result.system[0]["text"] == "You are a test agent."
        assert result.system[1]["text"] == "Existing block"

    def test_empty_system_prompt_returns_unchanged(self):
        agent = _make_agent(prompt="")
        registry = _make_registry(agent)
        req = _make_request(system="Original")
        result = apply_agent_persona(req, "test-agent", registry=registry)
        assert result is req

    def test_does_not_mutate_original_request(self):
        agent = _make_agent()
        registry = _make_registry(agent)
        req = _make_request(system="Original")
        result = apply_agent_persona(req, "test-agent", registry=registry)
        assert req.system == "Original"
        assert result.system != req.system

    def test_preserves_other_request_fields(self):
        agent = _make_agent()
        registry = _make_registry(agent)
        req = _make_request(system="Original")
        result = apply_agent_persona(req, "test-agent", registry=registry)
        assert result.model == req.model
        assert result.messages == req.messages
        assert result.stream == req.stream

    def test_multiple_agents_only_selected_one(self):
        agent_a = _make_agent("agent-a", "I am agent A.")
        agent_b = _make_agent("agent-b", "I am agent B.")
        registry = _make_registry(agent_a, agent_b)
        req = _make_request(system=None)
        result = apply_agent_persona(req, "agent-b", registry=registry)
        assert result.system == "I am agent B."
