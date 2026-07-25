"""Tests for skill definition file loader."""

from pathlib import Path

from free_claude_code.skills.loader import (
    _parse_frontmatter,
    load_skill_directory,
    load_skills_from_directory,
)
from free_claude_code.skills.registry import DEFINITIONS_DIR


class TestParseFrontmatter:
    def test_no_frontmatter(self):
        fields, body = _parse_frontmatter("Just a body")
        assert fields == {}
        assert body == "Just a body"

    def test_basic_frontmatter(self):
        raw = "---\nname: api-design\ndescription: REST API patterns\n---\nBody text"
        fields, body = _parse_frontmatter(raw)
        assert fields["name"] == "api-design"
        assert fields["description"] == "REST API patterns"
        assert body == "Body text"

    def test_frontmatter_with_metadata_origin(self):
        raw = "---\nname: test\nmetadata:\n  origin: ECC\n---\nBody"
        fields, body = _parse_frontmatter(raw)
        assert fields["name"] == "test"
        assert fields["origin"] == "ECC"
        assert body == "Body"

    def test_frontmatter_no_closing_delimiter(self):
        raw = "---\nname: Broken\nStill going"
        fields, body = _parse_frontmatter(raw)
        assert fields == {}
        assert body == raw


class TestLoadSkillDirectory:
    def test_load_valid_skill(self, tmp_path: Path):
        skill_dir = tmp_path / "test-skill"
        skill_dir.mkdir()
        (skill_dir / "SKILL.md").write_text(
            "---\nname: test-skill\ndescription: A test skill\n---\nDo this thing.",
            encoding="utf-8",
        )
        skill = load_skill_directory(skill_dir)
        assert skill is not None
        assert skill.skill_id == "test-skill"
        assert skill.name == "test-skill"
        assert skill.description == "A test skill"
        assert skill.instructions == "Do this thing."
        assert not skill.has_references

    def test_load_skill_with_references(self, tmp_path: Path):
        skill_dir = tmp_path / "fancy-skill"
        skill_dir.mkdir()
        (skill_dir / "SKILL.md").write_text(
            "---\nname: fancy\n---\nInstructions",
            encoding="utf-8",
        )
        refs = skill_dir / "references"
        refs.mkdir()
        (refs / "schema.md").write_text("Schema docs", encoding="utf-8")
        skill = load_skill_directory(skill_dir)
        assert skill is not None
        assert skill.has_references
        assert len(skill.reference_files) == 1
        assert "references/schema.md" in skill.reference_files

    def test_load_missing_skill_md(self, tmp_path: Path):
        skill_dir = tmp_path / "empty-skill"
        skill_dir.mkdir()
        result = load_skill_directory(skill_dir)
        assert result is None

    def test_load_defaults_when_no_frontmatter(self, tmp_path: Path):
        skill_dir = tmp_path / "plain-skill"
        skill_dir.mkdir()
        (skill_dir / "SKILL.md").write_text("Just instructions.", encoding="utf-8")
        skill = load_skill_directory(skill_dir)
        assert skill is not None
        assert skill.skill_id == "plain-skill"
        assert skill.name == "plain-skill"
        assert skill.instructions == "Just instructions."


class TestLoadSkillsFromDirectory:
    def test_load_empty_directory(self, tmp_path: Path):
        skills = load_skills_from_directory(tmp_path)
        assert skills == []

    def test_load_nonexistent_directory(self, tmp_path: Path):
        skills = load_skills_from_directory(tmp_path / "nope")
        assert skills == []

    def test_load_multiple_skills(self, tmp_path: Path):
        for name in ["alpha", "beta", "gamma"]:
            d = tmp_path / name
            d.mkdir()
            (d / "SKILL.md").write_text(
                f"---\nname: {name}\n---\nInstructions for {name}",
                encoding="utf-8",
            )
        skills = load_skills_from_directory(tmp_path)
        assert len(skills) == 3
        ids = [s.skill_id for s in skills]
        assert ids == ["alpha", "beta", "gamma"]

    def test_skips_directories_without_skill_md(self, tmp_path: Path):
        valid = tmp_path / "valid"
        valid.mkdir()
        (valid / "SKILL.md").write_text("---\nname: v\n---\nP", encoding="utf-8")
        invalid = tmp_path / "invalid"
        invalid.mkdir()
        (invalid / "README.md").write_text("Not a skill", encoding="utf-8")
        skills = load_skills_from_directory(tmp_path)
        assert len(skills) == 1


class TestBundledDefinitions:
    def test_definitions_directory_exists(self):
        assert DEFINITIONS_DIR.is_dir()

    def test_definitions_are_loadable(self):
        skills = load_skills_from_directory(DEFINITIONS_DIR)
        assert len(skills) >= 100

    def test_all_skills_have_instructions(self):
        skills = load_skills_from_directory(DEFINITIONS_DIR)
        for skill in skills:
            assert skill.instructions, f"{skill.skill_id} missing instructions"
