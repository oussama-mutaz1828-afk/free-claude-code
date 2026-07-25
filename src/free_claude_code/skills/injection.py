"""System prompt injection for skills."""

from loguru import logger

from free_claude_code.core.anthropic.models import MessagesRequest
from free_claude_code.core.trace import trace_event

from .registry import SkillRegistry, get_skill_registry


def apply_skill(
    request: MessagesRequest,
    active_skill: str,
    *,
    registry: SkillRegistry | None = None,
) -> MessagesRequest:
    """Prepend the selected skill's instructions to the request system prompt.

    Returns the request unchanged if active_skill is empty or not found.
    """
    if not active_skill:
        return request

    reg = registry or get_skill_registry()
    skill = reg.get(active_skill)
    if skill is None:
        logger.warning(
            "ACTIVE_SKILL '{}' not found in registry, skipping", active_skill
        )
        return request

    instructions = skill.instructions
    if not instructions:
        return request

    skill_header = f"[Skill: {skill.name}]\n\n{instructions}"

    existing = request.system
    if existing is None:
        merged: str | list[object] = skill_header
    elif isinstance(existing, str):
        merged = f"{skill_header}\n\n{existing}"
    elif isinstance(existing, list):
        merged = [{"type": "text", "text": skill_header}, *existing]
    else:
        merged = skill_header

    trace_event(
        stage="routing",
        event="free_claude_code.skills.skill_injected",
        source="skills",
        skill_id=skill.skill_id,
        skill_name=skill.name,
    )
    logger.debug("ACTIVE_SKILL: injected '{}' instructions", skill.skill_id)
    return request.model_copy(update={"system": merged})
