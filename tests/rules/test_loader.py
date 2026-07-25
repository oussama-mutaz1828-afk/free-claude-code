"""Tests for rule definition file loader."""

from pathlib import Path

from free_claude_code.rules.loader import (
    _parse_frontmatter,
    load_rule_file,
    load_rules_from_directory,
)
from free_claude_code.rules.registry import DEFINITIONS_DIR


class TestParseFrontmatter:
    def test_no_frontmatter(self):
        fields, body = _parse_frontmatter("Just a body")
        assert fields == {}
        assert body == "Just a body"

    def test_frontmatter_with_paths(self):
        raw = '---\npaths:\n  - "**/*.py"\n  - "**/*.pyi"\n---\nBody'
        fields, body = _parse_frontmatter(raw)
        assert fields["paths"] == ["**/*.py", "**/*.pyi"]
        assert body == "Body"

    def test_frontmatter_without_paths(self):
        raw = "---\ntitle: Coding Style\n---\nBody"
        fields, _body = _parse_frontmatter(raw)
        assert fields["title"] == "Coding Style"
        assert "paths" not in fields


class TestLoadRuleFile:
    def test_load_common_rule(self, tmp_path: Path):
        md = tmp_path / "coding-style.md"
        md.write_text("# Coding Style\n\nBe consistent.", encoding="utf-8")
        rule = load_rule_file(md, "common")
        assert rule.rule_id == "coding-style"
        assert rule.category == "common"
        assert rule.file_patterns == ()
        assert "Be consistent." in rule.instructions

    def test_load_language_rule_with_paths(self, tmp_path: Path):
        md = tmp_path / "coding-style.md"
        md.write_text(
            '---\npaths:\n  - "**/*.py"\n---\n# Python Style\n\nUse snake_case.',
            encoding="utf-8",
        )
        rule = load_rule_file(md, "python")
        assert rule.rule_id == "python/coding-style"
        assert rule.category == "python"
        assert rule.file_patterns == ("**/*.py",)


class TestLoadRulesFromDirectory:
    def test_load_empty_directory(self, tmp_path: Path):
        rules = load_rules_from_directory(tmp_path)
        assert rules == []

    def test_load_nonexistent_directory(self, tmp_path: Path):
        rules = load_rules_from_directory(tmp_path / "nope")
        assert rules == []

    def test_load_structured_directory(self, tmp_path: Path):
        common = tmp_path / "common"
        common.mkdir()
        (common / "style.md").write_text("# Style", encoding="utf-8")
        python = tmp_path / "python"
        python.mkdir()
        (python / "style.md").write_text("# Python Style", encoding="utf-8")
        rules = load_rules_from_directory(tmp_path)
        assert len(rules) == 2
        categories = {r.category for r in rules}
        assert categories == {"common", "python"}


class TestBundledDefinitions:
    def test_definitions_directory_exists(self):
        assert DEFINITIONS_DIR.is_dir()

    def test_definitions_are_loadable(self):
        rules = load_rules_from_directory(DEFINITIONS_DIR)
        assert len(rules) >= 20

    def test_common_category_exists(self):
        rules = load_rules_from_directory(DEFINITIONS_DIR)
        categories = {r.category for r in rules}
        assert "common" in categories

    def test_all_rules_have_instructions(self):
        rules = load_rules_from_directory(DEFINITIONS_DIR)
        for rule in rules:
            assert rule.instructions, f"{rule.rule_id} missing instructions"
