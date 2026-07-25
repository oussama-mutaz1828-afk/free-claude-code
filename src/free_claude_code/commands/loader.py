"""Parse command definition markdown files into CommandDefinition objects."""

from pathlib import Path

from .models import CommandDefinition


def _parse_frontmatter(raw: str) -> tuple[dict[str, str], str]:
    """Extract YAML-style frontmatter and body from a markdown string."""
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


def load_command_file(path: Path) -> CommandDefinition:
    """Load a single command definition from a markdown file."""
    raw = path.read_text(encoding="utf-8")
    fields, body = _parse_frontmatter(raw)

    command_id = path.stem
    return CommandDefinition(
        command_id=command_id,
        description=fields.get("description", ""),
        argument_hint=fields.get("argument-hint", ""),
        instructions=body,
    )


def load_commands_from_directory(directory: Path) -> list[CommandDefinition]:
    """Load all command definitions from markdown files in a directory."""
    if not directory.is_dir():
        return []
    return [load_command_file(path) for path in sorted(directory.glob("*.md"))]
