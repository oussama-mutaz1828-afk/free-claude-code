# Skills

Claude Code skills usable while developing Free Claude Code. Each skill is a self-contained
`SKILL.md` plus supporting references and scripts.

## codex-delegate

Ported from [amElnagdy/delegate-skills](https://github.com/amElnagdy/delegate-skills)
(`skills/codex-delegate/`, MIT license). Delegates a bounded coding task to the OpenAI Codex CLI as a
background implementer: the orchestrator writes the brief, dispatches it with `scripts/relay.mjs`,
then reviews the diff and commits it — Codex's sandbox never writes `.git`. See
[codex-delegate/SKILL.md](codex-delegate/SKILL.md) for the full loop.
