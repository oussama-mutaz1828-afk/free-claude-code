"""Parse skill definition directories into SkillDefinition objects."""

from pathlib import Path

from .models import SkillDefinition, SkillMetadata


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
    current_key: str | None = None
    for line in frontmatter_block.splitlines():
        stripped_line = line.strip()
        if stripped_line.startswith("origin:"):
            fields["origin"] = stripped_line.split(":", 1)[1].strip()
            continue
        colon_pos = line.find(":")
        if colon_pos == -1:
            continue
        key = line[:colon_pos].strip()
        value = line[colon_pos + 1 :].strip()
        if key == "metadata":
            current_key = key
            continue
        if current_key == "metadata" and key in ("origin",):
            fields[key] = value
            continue
        current_key = None
        fields[key] = value
    return fields, body


def _collect_reference_files(skill_dir: Path) -> tuple[str, ...]:
    """Collect relative paths of files in the references/ subdirectory."""
    refs_dir = skill_dir / "references"
    if not refs_dir.is_dir():
        return ()
    return tuple(
        str(p.relative_to(skill_dir))
        for p in sorted(refs_dir.rglob("*"))
        if p.is_file()
    )


def load_skill_directory(skill_dir: Path) -> SkillDefinition | None:
    """Load a single skill definition from a directory containing SKILL.md."""
    skill_file = skill_dir / "SKILL.md"
    if not skill_file.is_file():
        return None

    raw = skill_file.read_text(encoding="utf-8")
    fields, body = _parse_frontmatter(raw)

    skill_id = skill_dir.name
    ref_files = _collect_reference_files(skill_dir)

    return SkillDefinition(
        skill_id=skill_id,
        name=fields.get("name", skill_id),
        description=fields.get("description", ""),
        version=fields.get("version", ""),
        author=fields.get("author", ""),
        license=fields.get("license", ""),
        metadata=SkillMetadata(origin=fields.get("origin", "ECC")),
        instructions=body,
        has_references=len(ref_files) > 0,
        reference_files=ref_files,
    )


def load_skills_from_directory(directory: Path) -> list[SkillDefinition]:
    """Load all skill definitions from subdirectories in a directory."""
    if not directory.is_dir():
        return []
    skills: list[SkillDefinition] = []
    for entry in sorted(directory.iterdir()):
        if not entry.is_dir():
            continue
        skill = load_skill_directory(entry)
        if skill is not None:
            skills.append(skill)
    return skills
