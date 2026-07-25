"""Skill registry: loads and indexes all bundled skill definitions."""

from functools import lru_cache
from pathlib import Path

from .loader import load_skills_from_directory
from .models import SkillDefinition

DEFINITIONS_DIR = Path(__file__).parent / "definitions"


class SkillRegistry:
    """Thread-safe, immutable registry of all available skills."""

    def __init__(self, skills: list[SkillDefinition]) -> None:
        self._skills = {skill.skill_id: skill for skill in skills}

    @property
    def skill_ids(self) -> list[str]:
        return sorted(self._skills)

    @property
    def skills(self) -> list[SkillDefinition]:
        return [self._skills[sid] for sid in self.skill_ids]

    def get(self, skill_id: str) -> SkillDefinition | None:
        return self._skills.get(skill_id)

    def search(self, query: str) -> list[SkillDefinition]:
        """Search skills by name or description substring (case-insensitive)."""
        q = query.lower()
        return [
            s for s in self.skills if q in s.name.lower() or q in s.description.lower()
        ]

    def __len__(self) -> int:
        return len(self._skills)

    def __contains__(self, skill_id: str) -> bool:
        return skill_id in self._skills


@lru_cache
def get_skill_registry() -> SkillRegistry:
    """Return the singleton skill registry loaded from bundled definitions."""
    skills = load_skills_from_directory(DEFINITIONS_DIR)
    return SkillRegistry(skills)
