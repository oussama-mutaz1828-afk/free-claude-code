"""System prompt injection for agent personas."""

from loguru import logger

from free_claude_code.core.anthropic.models import MessagesRequest
from free_claude_code.core.trace import trace_event

from .registry import AgentRegistry, get_agent_registry


def apply_agent_persona(
    request: MessagesRequest,
    agent_persona: str,
    *,
    registry: AgentRegistry | None = None,
) -> MessagesRequest:
    """Prepend the selected agent persona's system prompt to the request.

    Returns the request unchanged if agent_persona is empty or not found.
    """
    if not agent_persona:
        return request

    reg = registry or get_agent_registry()
    agent = reg.get(agent_persona)
    if agent is None:
        logger.warning(
            "AGENT_PERSONA '{}' not found in registry, skipping", agent_persona
        )
        return request

    persona_prompt = agent.system_prompt
    if not persona_prompt:
        return request

    existing = request.system
    if existing is None:
        merged: str | list[object] = persona_prompt
    elif isinstance(existing, str):
        merged = f"{persona_prompt}\n\n{existing}"
    elif isinstance(existing, list):
        merged = [{"type": "text", "text": persona_prompt}, *existing]
    else:
        merged = persona_prompt

    trace_event(
        stage="routing",
        event="free_claude_code.agents.persona_injected",
        source="agents",
        agent_id=agent.agent_id,
        agent_name=agent.name,
    )
    logger.debug("AGENT_PERSONA: injected '{}' system prompt", agent.agent_id)
    return request.model_copy(update={"system": merged})
