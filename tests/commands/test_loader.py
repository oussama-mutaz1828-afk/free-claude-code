"""Tests for command definition file loader."""

from pathlib import Path

from free_claude_code.commands.loader import (
    _parse_frontmatter,
    load_command_file,
    load_commands_from_directory,
)
from free_claude_code.commands.registry import DEFINITIONS_DIR


class TestParseFrontmatter:
    def test_no_frontmatter(self):
        fields, body = _parse_frontmatter("Just a body")
        assert fields == {}
        assert body == "Just a body"

    def test_basic_frontmatter(self):
        raw = "---\ndescription: Code review\nargument-hint: [pr-number]\n---\nBody"
        fields, body = _parse_frontmatter(raw)
        assert fields["description"] == "Code review"
        assert fields["argument-hint"] == "[pr-number]"
        assert body == "Body"


class TestLoadCommandFile:
    def test_load_valid_file(self, tmp_path: Path):
        md = tmp_path / "code-review.md"
        md.write_text(
            "---\ndescription: Review code\nargument-hint: [pr]\n---\nReview steps.",
            encoding="utf-8",
        )
        cmd = load_command_file(md)
        assert cmd.command_id == "code-review"
        assert cmd.description == "Review code"
        assert cmd.argument_hint == "[pr]"
        assert cmd.instructions == "Review steps."

    def test_load_file_without_frontmatter(self, tmp_path: Path):
        md = tmp_path / "plain.md"
        md.write_text("Just instructions.", encoding="utf-8")
        cmd = load_command_file(md)
        assert cmd.command_id == "plain"
        assert cmd.description == ""
        assert cmd.instructions == "Just instructions."


class TestLoadCommandsFromDirectory:
    def test_load_empty_directory(self, tmp_path: Path):
        cmds = load_commands_from_directory(tmp_path)
        assert cmds == []

    def test_load_nonexistent_directory(self, tmp_path: Path):
        cmds = load_commands_from_directory(tmp_path / "nope")
        assert cmds == []

    def test_load_multiple_files(self, tmp_path: Path):
        for name in ["alpha.md", "beta.md"]:
            (tmp_path / name).write_text(
                f"---\ndescription: {name}\n---\nInstructions",
                encoding="utf-8",
            )
        cmds = load_commands_from_directory(tmp_path)
        assert len(cmds) == 2


class TestBundledDefinitions:
    def test_definitions_directory_exists(self):
        assert DEFINITIONS_DIR.is_dir()

    def test_definitions_are_loadable(self):
        cmds = load_commands_from_directory(DEFINITIONS_DIR)
        assert len(cmds) >= 50

    def test_all_commands_have_instructions(self):
        cmds = load_commands_from_directory(DEFINITIONS_DIR)
        for cmd in cmds:
            assert cmd.instructions, f"{cmd.command_id} missing instructions"
