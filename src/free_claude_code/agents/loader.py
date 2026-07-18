"""Parse agent definition markdown files into AgentDefinition objects."""

from pathlib import Path

from .models import AgentDefinition


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
    return AgentDefinition(
        agent_id=agent_id,
        name=fields.get("name", agent_id),
        description=fields.get("description", ""),
        division=fields.get("division", "engineering"),
        emoji=fields.get("emoji", ""),
        vibe=fields.get("vibe", ""),
        system_prompt=body,
    )


def load_agents_from_directory(directory: Path) -> list[AgentDefinition]:
    """Load all agent definitions from markdown files in a directory."""
    if not directory.is_dir():
        return []
    return [load_agent_file(path) for path in sorted(directory.glob("*.md"))]
