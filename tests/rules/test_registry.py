"""Tests for the rule registry."""

from free_claude_code.rules.models import RuleDefinition
from free_claude_code.rules.registry import RuleRegistry, get_rule_registry


def _make_rule(rule_id: str, category: str = "common") -> RuleDefinition:
    return RuleDefinition(
        rule_id=rule_id,
        category=category,
        instructions=f"Instructions for {rule_id}.",
    )


class TestRuleRegistry:
    def test_empty_registry(self):
        reg = RuleRegistry([])
        assert len(reg) == 0
        assert reg.rules == []
        assert reg.categories == []

    def test_register_and_get(self):
        rule = _make_rule("coding-style")
        reg = RuleRegistry([rule])
        assert len(reg) == 1
        assert "coding-style" in reg
        assert reg.get("coding-style") is rule

    def test_get_missing_returns_none(self):
        reg = RuleRegistry([])
        assert reg.get("nonexistent") is None

    def test_rule_ids_sorted(self):
        rules = [_make_rule("c"), _make_rule("a"), _make_rule("b")]
        reg = RuleRegistry(rules)
        assert reg.rule_ids == ["a", "b", "c"]

    def test_list_by_category(self):
        rules = [
            _make_rule("style", "common"),
            _make_rule("python/style", "python"),
            _make_rule("testing", "common"),
        ]
        reg = RuleRegistry(rules)
        common = reg.list_by_category("common")
        assert len(common) == 2
        assert all(r.category == "common" for r in common)

    def test_categories(self):
        rules = [
            _make_rule("a", "common"),
            _make_rule("b", "python"),
            _make_rule("c", "typescript"),
        ]
        reg = RuleRegistry(rules)
        assert reg.categories == ["common", "python", "typescript"]

    def test_contains(self):
        reg = RuleRegistry([_make_rule("present")])
        assert "present" in reg
        assert "absent" not in reg


class TestGetRuleRegistry:
    def test_returns_populated_registry(self):
        reg = get_rule_registry()
        assert len(reg) >= 20

    def test_singleton(self):
        a = get_rule_registry()
        b = get_rule_registry()
        assert a is b

    def test_has_common_category(self):
        reg = get_rule_registry()
        assert "common" in reg.categories
