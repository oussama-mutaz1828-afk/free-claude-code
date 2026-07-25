"""Data models for rule definitions."""

from dataclasses import dataclass, field


@dataclass(frozen=True, slots=True)
class RuleDefinition:
    """A single rule parsed from a markdown definition file."""

    rule_id: str
    category: str
    file_patterns: tuple[str, ...] = field(default_factory=tuple)
    instructions: str = ""
