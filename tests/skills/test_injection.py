"""Tests for skill system prompt injection."""

from free_claude_code.core.anthropic.models import Message, MessagesRequest
from free_claude_code.skills.injection import apply_skill
from free_claude_code.skills.models import SkillDefinition, SkillMetadata
from free_claude_code.skills.registry import SkillRegistry


def _make_registry(*skills: SkillDefinition) -> SkillRegistry:
    return SkillRegistry(list(skills))


def _make_skill(
    skill_id: str = "test-skill", instructions: str = "Do the test thing."
) -> SkillDefinition:
    return SkillDefinition(
        skill_id=skill_id,
        name="Test Skill",
        description="Testing",
        version="1.0.0",
        author="test",
        license="MIT",
        metadata=SkillMetadata(origin="test"),
        instructions=instructions,
    )


def _make_request(
    system: str | list[object] | None = None,
) -> MessagesRequest:
    return MessagesRequest(
        model="claude-sonnet-4-20250514",
        messages=[Message(role="user", content="Hello")],
        system=system,
    )


class TestApplySkill:
    def test_empty_skill_returns_unchanged(self):
        req = _make_request(system="Original")
        result = apply_skill(req, "")
        assert result is req

    def test_unknown_skill_returns_unchanged(self):
        registry = _make_registry()
        req = _make_request(system="Original")
        result = apply_skill(req, "nonexistent", registry=registry)
        assert result is req

    def test_inject_into_none_system(self):
        skill = _make_skill()
        registry = _make_registry(skill)
        req = _make_request(system=None)
        result = apply_skill(req, "test-skill", registry=registry)
        assert isinstance(result.system, str)
        assert "Do the test thing." in result.system

    def test_inject_prepends_to_string_system(self):
        skill = _make_skill()
        registry = _make_registry(skill)
        req = _make_request(system="Original system prompt")
        result = apply_skill(req, "test-skill", registry=registry)
        assert isinstance(result.system, str)
        assert result.system.index("Do the test thing.") < result.system.index(
            "Original system prompt"
        )

    def test_inject_prepends_to_list_system(self):
        skill = _make_skill()
        registry = _make_registry(skill)
        existing_blocks = [{"type": "text", "text": "Existing block"}]
        req = _make_request(system=existing_blocks)
        result = apply_skill(req, "test-skill", registry=registry)
        assert isinstance(result.system, list)
        assert len(result.system) == 2
        assert "Do the test thing." in result.system[0]["text"]

    def test_empty_instructions_returns_unchanged(self):
        skill = _make_skill(instructions="")
        registry = _make_registry(skill)
        req = _make_request(system="Original")
        result = apply_skill(req, "test-skill", registry=registry)
        assert result is req

    def test_skill_header_included(self):
        skill = _make_skill()
        registry = _make_registry(skill)
        req = _make_request(system=None)
        result = apply_skill(req, "test-skill", registry=registry)
        assert "[Skill: Test Skill]" in result.system

    def test_preserves_other_request_fields(self):
        skill = _make_skill()
        registry = _make_registry(skill)
        req = _make_request(system="Original")
        result = apply_skill(req, "test-skill", registry=registry)
        assert result.model == req.model
        assert result.messages == req.messages
