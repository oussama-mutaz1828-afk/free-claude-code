"""Rule registry: loads and indexes all bundled rule definitions."""

from functools import lru_cache
from pathlib import Path

from .loader import load_rules_from_directory
from .models import RuleDefinition

DEFINITIONS_DIR = Path(__file__).parent / "definitions"


class RuleRegistry:
    """Thread-safe, immutable registry of all available rules."""

    def __init__(self, rules: list[RuleDefinition]) -> None:
        self._rules = {rule.rule_id: rule for rule in rules}
        self._by_category: dict[str, list[RuleDefinition]] = {}
        for rule in rules:
            self._by_category.setdefault(rule.category, []).append(rule)

    @property
    def rule_ids(self) -> list[str]:
        return sorted(self._rules)

    @property
    def rules(self) -> list[RuleDefinition]:
        return [self._rules[rid] for rid in self.rule_ids]

    @property
    def categories(self) -> list[str]:
        return sorted(self._by_category)

    def get(self, rule_id: str) -> RuleDefinition | None:
        return self._rules.get(rule_id)

    def list_by_category(self, category: str) -> list[RuleDefinition]:
        return list(self._by_category.get(category, []))

    def __len__(self) -> int:
        return len(self._rules)

    def __contains__(self, rule_id: str) -> bool:
        return rule_id in self._rules


@lru_cache
def get_rule_registry() -> RuleRegistry:
    """Return the singleton rule registry loaded from bundled definitions."""
    rules = load_rules_from_directory(DEFINITIONS_DIR)
    return RuleRegistry(rules)
