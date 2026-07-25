"""Tests for agent definition file loader."""

from pathlib import Path

import pytest

from free_claude_code.agents.loader import (
    _parse_frontmatter,
    load_agent_file,
    load_agents_from_directory,
)
from free_claude_code.agents.registry import DEFINITIONS_DIR


class TestParseFrontmatter:
    def test_no_frontmatter(self):
        fields, body = _parse_frontmatter("Just a body")
        assert fields == {}
        assert body == "Just a body"

    def test_basic_frontmatter(self):
        raw = "---\nname: Test Agent\ndescription: A test\n---\nBody text here"
        fields, body = _parse_frontmatter(raw)
        assert fields["name"] == "Test Agent"
        assert fields["description"] == "A test"
        assert body == "Body text here"

    def test_frontmatter_with_leading_whitespace(self):
        raw = "\n  ---\nname: Agent\n---\nBody"
        fields, body = _parse_frontmatter(raw)
        assert fields["name"] == "Agent"
        assert body == "Body"

    def test_frontmatter_no_closing_delimiter(self):
        raw = "---\nname: Broken\nStill going"
        fields, body = _parse_frontmatter(raw)
        assert fields == {}
        assert body == raw

    def test_frontmatter_empty_values(self):
        raw = "---\nname:\nemoji: 🧪\n---\nBody"
        fields, _body = _parse_frontmatter(raw)
        assert fields["name"] == ""
        assert fields["emoji"] == "🧪"

    def test_lines_without_colon_are_skipped(self):
        raw = "---\nno colon here\nname: Valid\n---\nBody"
        fields, _body = _parse_frontmatter(raw)
        assert "no colon here" not in fields
        assert fields["name"] == "Valid"


class TestLoadAgentFile:
    def test_load_valid_file(self, tmp_path: Path):
        md = tmp_path / "test-agent.md"
        md.write_text(
            "---\nname: Test\ndescription: Desc\ndivision: testing\nemoji: 🧪\nvibe: Vibes\n---\nSystem prompt here.",
            encoding="utf-8",
        )
        agent = load_agent_file(md)
        assert agent.agent_id == "test-agent"
        assert agent.name == "Test"
        assert agent.description == "Desc"
        assert agent.division == "testing"
        assert agent.emoji == "🧪"
        assert agent.vibe == "Vibes"
        assert agent.system_prompt == "System prompt here."

    def test_load_file_without_frontmatter(self, tmp_path: Path):
        md = tmp_path / "plain.md"
        md.write_text("Just a plain file.", encoding="utf-8")
        agent = load_agent_file(md)
        assert agent.agent_id == "plain"
        assert agent.name == "plain"
        assert agent.division == "engineering"
        assert agent.system_prompt == "Just a plain file."

    def test_agent_id_from_filename(self, tmp_path: Path):
        md = tmp_path / "my-cool-agent.md"
        md.write_text("---\nname: Cool\n---\nPrompt", encoding="utf-8")
        agent = load_agent_file(md)
        assert agent.agent_id == "my-cool-agent"

    def test_load_ecc_agent_with_tools_and_model(self, tmp_path: Path):
        md = tmp_path / "architect.md"
        md.write_text(
            '---\nname: architect\ndescription: Software architect\ntools: ["Read", "Grep", "Glob"]\nmodel: opus\n---\nYou are an architect.',
            encoding="utf-8",
        )
        agent = load_agent_file(md)
        assert agent.agent_id == "architect"
        assert agent.tools == ("Read", "Grep", "Glob")
        assert agent.model == "opus"

    def test_load_agent_without_tools_defaults_empty(self, tmp_path: Path):
        md = tmp_path / "simple.md"
        md.write_text("---\nname: Simple\n---\nPrompt", encoding="utf-8")
        agent = load_agent_file(md)
        assert agent.tools == ()
        assert agent.model == ""


class TestLoadAgentsFromDirectory:
    def test_load_empty_directory(self, tmp_path: Path):
        agents = load_agents_from_directory(tmp_path)
        assert agents == []

    def test_load_nonexistent_directory(self, tmp_path: Path):
        agents = load_agents_from_directory(tmp_path / "nope")
        assert agents == []

    def test_load_multiple_files(self, tmp_path: Path):
        for name in ["alpha.md", "beta.md", "gamma.md"]:
            (tmp_path / name).write_text(
                f"---\nname: {name}\n---\nPrompt for {name}",
                encoding="utf-8",
            )
        agents = load_agents_from_directory(tmp_path)
        assert len(agents) == 3
        ids = [a.agent_id for a in agents]
        assert ids == ["alpha", "beta", "gamma"]

    def test_ignores_non_md_files(self, tmp_path: Path):
        (tmp_path / "agent.md").write_text("---\nname: A\n---\nP", encoding="utf-8")
        (tmp_path / "notes.txt").write_text("Not an agent", encoding="utf-8")
        (tmp_path / "config.json").write_text("{}", encoding="utf-8")
        agents = load_agents_from_directory(tmp_path)
        assert len(agents) == 1


class TestBundledDefinitions:
    def test_definitions_directory_exists(self):
        assert DEFINITIONS_DIR.is_dir()

    def test_definitions_are_loadable(self):
        agents = load_agents_from_directory(DEFINITIONS_DIR)
        assert len(agents) >= 10

    @pytest.mark.parametrize(
        "agent_id",
        [
            "software-architect",
            "code-reviewer",
            "frontend-developer",
            "backend-architect",
            "senior-developer",
            "devops-automator",
            "api-platform-engineer",
            "data-engineer",
            "prompt-engineer",
            "sre",
            "security-architect",
            "test-engineer",
            "ux-designer",
            "mobile-app-builder",
            "incident-response-commander",
            "solidity-smart-contract-engineer",
            "codebase-onboarding-engineer",
            "ai-data-remediation-engineer",
            "feishu-integration-developer",
            "voice-ai-integration-engineer",
            "multi-agent-systems-architect",
            "drupal-shopping-cart-engineer",
            "wordpress-shopping-cart-engineer",
            "payments-billing-engineer",
            "wordpress-performance-engineer",
            "search-relevance-engineer",
            "uswds-developer",
            "mobile-release-engineer",
            "video-streaming-engineer",
            "ui-designer",
            "ux-researcher",
            "ux-architect",
            "search-query-analyst",
            "outbound-strategist",
            "deal-strategist",
            "sales-engineer",
            "architect",
            "python-reviewer",
            "typescript-reviewer",
            "react-reviewer",
            "rust-reviewer",
            "go-reviewer",
            "planner",
            "code-explorer",
            "security-reviewer",
            "performance-optimizer",
            "tdd-guide",
        ],
    )
    def test_expected_agent_exists(self, agent_id: str):
        agents = load_agents_from_directory(DEFINITIONS_DIR)
        ids = {a.agent_id for a in agents}
        assert agent_id in ids

    def test_all_agents_have_required_fields(self):
        agents = load_agents_from_directory(DEFINITIONS_DIR)
        for agent in agents:
            assert agent.name, f"{agent.agent_id} missing name"
            assert agent.description, f"{agent.agent_id} missing description"
            assert agent.division, f"{agent.agent_id} missing division"
            assert agent.system_prompt, f"{agent.agent_id} missing system_prompt"
