"""Data models for skill definitions."""

from dataclasses import dataclass, field


@dataclass(frozen=True, slots=True)
class SkillMetadata:
    """Origin and authorship metadata for a skill."""

    origin: str = "ECC"


@dataclass(frozen=True, slots=True)
class SkillDefinition:
    """A single skill parsed from a SKILL.md definition file."""

    skill_id: str
    name: str
    description: str
    version: str
    author: str
    license: str
    metadata: SkillMetadata
    instructions: str
    has_references: bool = False
    reference_files: tuple[str, ...] = field(default_factory=tuple)
