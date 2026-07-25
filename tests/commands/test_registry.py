"""Tests for the command registry."""

from free_claude_code.commands.models import CommandDefinition
from free_claude_code.commands.registry import CommandRegistry, get_command_registry


def _make_command(command_id: str, description: str = "") -> CommandDefinition:
    return CommandDefinition(
        command_id=command_id,
        description=description or f"Test {command_id}",
        argument_hint="",
        instructions=f"Instructions for {command_id}.",
    )


class TestCommandRegistry:
    def test_empty_registry(self):
        reg = CommandRegistry([])
        assert len(reg) == 0
        assert reg.commands == []

    def test_register_and_get(self):
        cmd = _make_command("test-cmd")
        reg = CommandRegistry([cmd])
        assert len(reg) == 1
        assert "test-cmd" in reg
        assert reg.get("test-cmd") is cmd

    def test_get_missing_returns_none(self):
        reg = CommandRegistry([])
        assert reg.get("nonexistent") is None

    def test_command_ids_sorted(self):
        cmds = [_make_command("c"), _make_command("a"), _make_command("b")]
        reg = CommandRegistry(cmds)
        assert reg.command_ids == ["a", "b", "c"]

    def test_search(self):
        cmds = [
            _make_command("code-review", "Review code quality"),
            _make_command("build-fix", "Fix build errors"),
        ]
        reg = CommandRegistry(cmds)
        results = reg.search("review")
        assert len(results) == 1
        assert results[0].command_id == "code-review"

    def test_contains(self):
        reg = CommandRegistry([_make_command("present")])
        assert "present" in reg
        assert "absent" not in reg


class TestGetCommandRegistry:
    def test_returns_populated_registry(self):
        reg = get_command_registry()
        assert len(reg) >= 50

    def test_singleton(self):
        a = get_command_registry()
        b = get_command_registry()
        assert a is b
