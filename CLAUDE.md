# longevity-skills — Claude Code

@AGENTS.md

## Claude-specific notes

- Prefer loading a skill via `/skill-name` (e.g. `/aging-news-digest`) or by matching the skill description; do not paste an entire `SKILL.md` into chat unless debugging.
- When installing for Claude Code itself, copy skill folders into `~/.claude/skills/<name>/` (personal) or `.claude/skills/<name>/` (this project).
- Claude Desktop’s **Cowork** tab remains the primary runtime for research/digest skills (browsing, file writing, **Scheduled** UI or `/schedule`). Use Claude Code when editing skills in this repo or running script helpers locally.
- If a skill ships Python helpers under `scripts/`, run them with `uv` when the skill or project expects it.
