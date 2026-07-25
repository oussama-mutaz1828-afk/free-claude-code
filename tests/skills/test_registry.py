"""Tests for the skill registry."""

from free_claude_code.skills.models import SkillDefinition, SkillMetadata
from free_claude_code.skills.registry import SkillRegistry, get_skill_registry


def _make_skill(skill_id: str, description: str = "") -> SkillDefinition:
    return SkillDefinition(
        skill_id=skill_id,
        name=skill_id,
        description=description or f"Test {skill_id}",
        version="1.0.0",
        author="test",
        license="MIT",
        metadata=SkillMetadata(origin="test"),
        instructions=f"Instructions for {skill_id}.",
    )


class TestSkillRegistry:
    def test_empty_registry(self):
        reg = SkillRegistry([])
        assert len(reg) == 0
        assert reg.skills == []
        assert reg.skill_ids == []

    def test_register_and_get(self):
        skill = _make_skill("test-skill")
        reg = SkillRegistry([skill])
        assert len(reg) == 1
        assert "test-skill" in reg
        assert reg.get("test-skill") is skill

    def test_get_missing_returns_none(self):
        reg = SkillRegistry([])
        assert reg.get("nonexistent") is None

    def test_skill_ids_sorted(self):
        skills = [_make_skill("c"), _make_skill("a"), _make_skill("b")]
        reg = SkillRegistry(skills)
        assert reg.skill_ids == ["a", "b", "c"]

    def test_search_by_name(self):
        skills = [
            _make_skill("api-design", "REST API patterns"),
            _make_skill("python-testing", "Python test workflows"),
            _make_skill("react-patterns", "React component patterns"),
        ]
        reg = SkillRegistry(skills)
        results = reg.search("python")
        assert len(results) == 1
        assert results[0].skill_id == "python-testing"

    def test_search_case_insensitive(self):
        skills = [_make_skill("API-Design", "REST patterns")]
        reg = SkillRegistry(skills)
        results = reg.search("api")
        assert len(results) == 1

    def test_contains(self):
        reg = SkillRegistry([_make_skill("present")])
        assert "present" in reg
        assert "absent" not in reg


class TestGetSkillRegistry:
    def test_returns_populated_registry(self):
        reg = get_skill_registry()
        assert len(reg) >= 100

    def test_singleton(self):
        a = get_skill_registry()
        b = get_skill_registry()
        assert a is b
