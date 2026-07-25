"""Parse agent definition markdown files into AgentDefinition objects."""

import re
from pathlib import Path

from .models import AgentDefinition

_TOOLS_RE = re.compile(r"\[([^\]]*)\]")


def _parse_tools(value: str) -> tuple[str, ...]:
    """Parse a tools field like '["Read", "Grep", "Glob"]' into a tuple."""
    match = _TOOLS_RE.search(value)
    if not match:
        return ()
    inner = match.group(1)
    return tuple(t.strip().strip('"').strip("'") for t in inner.split(",") if t.strip())


def _parse_frontmatter(raw: str) -> tuple[dict[str, str], str]:
    """Extract YAML-style frontmatter and body from a markdown string.

    Returns (frontmatter_dict, body_text).
    """
    stripped = raw.lstrip()
    if not stripped.startswith("---"):
        return {}, raw

    end = stripped.find("---", 3)
    if end == -1:
        return {}, raw

    frontmatter_block = stripped[3:end].strip()
    body = stripped[end + 3 :].strip()

    fields: dict[str, str] = {}
    for line in frontmatter_block.splitlines():
        colon_pos = line.find(":")
        if colon_pos == -1:
            continue
        key = line[:colon_pos].strip()
        value = line[colon_pos + 1 :].strip()
        fields[key] = value
    return fields, body


def _agent_id_from_path(path: Path) -> str:
    return path.stem


def load_agent_file(path: Path) -> AgentDefinition:
    """Load a single agent definition from a markdown file."""
    raw = path.read_text(encoding="utf-8")
    fields, body = _parse_frontmatter(raw)

    agent_id = _agent_id_from_path(path)
    tools = _parse_tools(fields.get("tools", ""))
    return AgentDefinition(
        agent_id=agent_id,
        name=fields.get("name", agent_id),
        description=fields.get("description", ""),
        division=fields.get("division", "engineering"),
        emoji=fields.get("emoji", ""),
        vibe=fields.get("vibe", ""),
        system_prompt=body,
        tools=tools,
        model=fields.get("model", ""),
    )


def load_agents_from_directory(directory: Path) -> list[AgentDefinition]:
    """Load all agent definitions from markdown files in a directory."""
    if not directory.is_dir():
        return []
    return [load_agent_file(path) for path in sorted(directory.glob("*.md"))]
