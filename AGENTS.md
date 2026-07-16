# longevity-skills — agent instructions

This repository is a collection of portable **agent skills** for longevity research and advocacy. Skills target **Claude Desktop’s Cowork tab** first (Cowork is merged into Desktop as of mid-2026; macOS, Windows, and Linux beta), and also work in Claude Code, Cursor, Google Antigravity, and other tools that load the open `SKILL.md` format.

Human-facing install/use docs live in [README.md](README.md). Follow this file when editing the repo or helping users install skills.

## Layout

```text
longevity-skills/
├── README.md                 # how to install and run (Cowork-first)
├── AGENTS.md                 # this file — shared agent context
├── CLAUDE.md                 # Claude Code entrypoint (@AGENTS.md)
├── LICENSE                   # AGPL-3.0
└── <skill-name>/
    ├── SKILL.md              # required: YAML frontmatter + instructions
    ├── scripts/              # optional helpers the skill may run
    └── references/           # optional docs/templates the skill may read
```

Each skill is a **self-contained folder**. Do not put a `README.md` inside a skill folder (skill folders are meant to be copied/uploaded as-is; human docs stay at the repo root).

## Skill authoring rules

When creating or editing a skill:

1. **Folder name = skill `name`** (lowercase, hyphens only), matching frontmatter `name`.
2. **`SKILL.md` frontmatter must include** at least:
   - `name`
   - `description` — what it does **and** when to use it (trigger phrases matter)
3. Put repeatable workflows in the skill body; keep this repo’s root docs short.
4. Supporting scripts belong under `<skill>/scripts/`. Prefer absolute imports in Python; use type hints; use `uv` / `typer` if adding a CLI.
5. Prefer live research and real outputs over mocks when a skill says to produce digests, PDFs, or dashboards.
6. For scheduled/unattended skills: use AUTO defaults, note choices in the output, and never take connector “write” actions (email, post, etc.) unless the run explicitly requests them.
7. List every new skill in [README.md](README.md) under **Skills**.

## Installing / using skills (for agents helping users)

### Claude Desktop / Cowork (preferred)

1. Clone or download the skill folder (e.g. `aging-news-digest/`).
2. In Claude Desktop → **Cowork** tab: **Customize → Skills** → upload the folder (zip if required) or copy it into the connected Skills directory. Keep `SKILL.md` and `scripts/` together. Desktop is available on macOS, Windows, and Linux (beta: Ubuntu 22.04+ / Debian 12+).
3. Enable the skill under **My Skills**.
4. Run with `/<skill-name>` or a natural-language request that matches the description.
5. For recurring digests: use the **Scheduled** sidebar UI (**New task** → manual setup or create with Claude), or ask in chat / `/schedule`. Use AUTO defaults; no unsolicited connector writes.

### Other hosts

| Tool | Personal / global | Project / workspace |
| --- | --- | --- |
| Claude Code | `~/.claude/skills/<name>/` | `.claude/skills/<name>/` |
| Cursor | `~/.cursor/skills/<name>/` | `.cursor/skills/<name>/` (also reads `.claude/skills/`) |
| Antigravity | `~/.gemini/config/skills/<name>/` | `.agents/skills/<name>/` |
| claude.ai | Zip folder → Customize / Settings → Skills → upload | — |

Copy the whole skill directory — not only `SKILL.md`.

## Current skills

- `aging-news-digest` — HEALES-style aging/longevity news digest (PDF + interactive HTML dashboard); interactive or scheduled.

## Working in this repo

- Prefer editing existing skill instructions over inventing parallel docs.
- Do not invent placeholder paths; keep scripts runnable from the skill folder context.
- Do not commit secrets. Do not create drive-by markdown changelogs unless asked.
- After changing a skill that users already installed elsewhere, remind them to re-copy or re-upload so the host picks up updates.
