"""Parse rule definition markdown files into RuleDefinition objects."""

import re
from pathlib import Path

from .models import RuleDefinition

_PATTERN_RE = re.compile(r'-\s*"([^"]+)"')


def _parse_frontmatter(raw: str) -> tuple[dict[str, object], str]:
    """Extract YAML-style frontmatter and body from a markdown string."""
    stripped = raw.lstrip()
    if not stripped.startswith("---"):
        return {}, raw

    end = stripped.find("---", 3)
    if end == -1:
        return {}, raw

    frontmatter_block = stripped[3:end].strip()
    body = stripped[end + 3 :].strip()

    fields: dict[str, object] = {}
    in_paths = False
    paths: list[str] = []

    for line in frontmatter_block.splitlines():
        stripped_line = line.strip()
        if stripped_line.startswith("paths:"):
            in_paths = True
            continue
        if in_paths:
            match = _PATTERN_RE.match(stripped_line)
            if match:
                paths.append(match.group(1))
                continue
            in_paths = False
        colon_pos = line.find(":")
        if colon_pos == -1:
            continue
        key = line[:colon_pos].strip()
        value = line[colon_pos + 1 :].strip()
        fields[key] = value

    if paths:
        fields["paths"] = paths
    return fields, body


def load_rule_file(path: Path, category: str) -> RuleDefinition:
    """Load a single rule definition from a markdown file."""
    raw = path.read_text(encoding="utf-8")
    fields, body = _parse_frontmatter(raw)

    rule_id = f"{category}/{path.stem}" if category != "common" else path.stem
    paths_val = fields.get("paths")
    file_patterns: tuple[str, ...] = ()
    if isinstance(paths_val, list):
        file_patterns = tuple(str(p) for p in paths_val)

    return RuleDefinition(
        rule_id=rule_id,
        category=category,
        file_patterns=file_patterns,
        instructions=body,
    )


def load_rules_from_directory(directory: Path) -> list[RuleDefinition]:
    """Load all rule definitions from a rules directory structure.

    Expects subdirectories like common/, python/, typescript/, etc.
    """
    if not directory.is_dir():
        return []
    rules: list[RuleDefinition] = []
    for category_dir in sorted(directory.iterdir()):
        if not category_dir.is_dir():
            continue
        category = category_dir.name
        rules.extend(
            load_rule_file(md_file, category)
            for md_file in sorted(category_dir.glob("*.md"))
        )
    return rules
