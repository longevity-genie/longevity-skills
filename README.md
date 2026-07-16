# longevity-skills

Collection of agent skills useful for longevity research and advocacy. Skills work with [Claude Desktop](https://claude.com/download) / Cowork (macOS, Windows, Linux beta), Claude Code, Cursor, Google Antigravity, and other tools that load the open `SKILL.md` format.

Each skill lives in its own subfolder with a `SKILL.md` (and any supporting scripts/references). Copy a skill folder into your tool’s skills directory — the agent loads it when your request matches the skill’s description, or when you invoke it by name.

Agents working in this repository should follow [`AGENTS.md`](AGENTS.md). Claude Code also loads [`CLAUDE.md`](CLAUDE.md) (which imports `AGENTS.md`).

## Using with Claude Desktop / Cowork (recommended)

As of mid-2026, **Cowork is part of [Claude Desktop](https://claude.com/download)** (Chat, Cowork, and Code in one app) on **macOS, Windows, and Linux (beta)**. Cowork is also rolling out on web/mobile for paid plans. These skills are aimed at the **Cowork** tab: research, write files, run scripts, and schedule recurring digests.

Download Desktop from [claude.com/download](https://claude.com/download). Linux beta currently targets Ubuntu 22.04+ / Debian 12+ (x86_64 and arm64).

### Install a skill

1. Clone this repo (or download a single skill folder):

   ```bash
   git clone https://github.com/longevity-genie/longevity-skills.git
   ```

2. In Claude Desktop, open the **Cowork** tab, then **Customize** in the left sidebar → **Skills**.
3. Add the skill folder (e.g. `aging-news-digest/`) via upload, or copy it into the local Skills folder Desktop is already using.
   - Keep the folder structure intact: `aging-news-digest/SKILL.md` plus any `scripts/` next to it.
   - Zip the skill folder first if the UI asks for a zip upload.
4. Confirm the skill appears under **My Skills** and is enabled.

### Run a skill

- **By name:** type `/aging-news-digest` (or the skill’s `name` from its frontmatter).
- **By intent:** ask in plain language, e.g. *“Compile this month’s HEALES-style aging news digest.”* Cowork loads the matching skill when the description fits.

Example prompt:

```text
/aging-news-digest

Compile the aging news digest for the trailing 5 weeks.
Output PDF + interactive HTML dashboard.
```

### Schedule a recurring run

Skills that support unattended runs (like `aging-news-digest`) work well as scheduled Cowork tasks. You can set them up in the **UI** or in chat:

**UI (recommended):**

1. Click **Scheduled** in the left sidebar.
2. **New task** → **Set up manually** (or **Create with Claude**).
3. Enter the task name, prompt (mention the skill / `/aging-news-digest`, AUTO defaults, PDF + HTML), cadence (hourly / daily / weekly / weekdays / manual), and optional model/folder.
4. **Save**. Review upcoming and past runs from the same **Scheduled** page; you can also pause, resume, edit, delete, or **run on demand**.

**In chat:** ask Claude to schedule the task, or use `/schedule`, and confirm when prompted.

In the scheduled prompt, say to use AUTO defaults and not send emails / post to connectors unless you explicitly ask. Remote scheduled tasks can keep running even when your computer is asleep or Desktop is closed (local-folder tasks still need the machine available).

### Tips

- Prefer **Skills** for repeatable workflows; put standing tone/source rules in Cowork **Instructions**.
- After updating a skill from git, re-upload or replace the local copy so Desktop picks up changes.
- Official overview: [Customize Claude Cowork](https://claude.com/resources/tutorials/customize-claude-cowork) · [Schedule recurring tasks](https://support.claude.com/en/articles/13854387-schedule-recurring-tasks-in-cowork).

## Other AI IDEs / agents

Same `SKILL.md` folders work elsewhere — only the install path differs.

| Tool | Where to put a skill folder |
| --- | --- |
| **Claude Code** | Personal: `~/.claude/skills/<skill-name>/` · Project: `.claude/skills/<skill-name>/` |
| **Cursor** | Personal: `~/.cursor/skills/<skill-name>/` · Project: `.cursor/skills/<skill-name>/` (also reads `.claude/skills/`) |
| **Google Antigravity** | Global: `~/.gemini/config/skills/<skill-name>/` · Workspace: `.agents/skills/<skill-name>/` |
| **claude.ai** | Zip the skill folder → Settings / Customize → Skills → upload |

Quick copy examples:

```bash
# Claude Code / Claude Desktop (personal)
cp -R aging-news-digest ~/.claude/skills/aging-news-digest

# Cursor (personal)
cp -R aging-news-digest ~/.cursor/skills/aging-news-digest

# Antigravity (workspace)
mkdir -p .agents/skills && cp -R aging-news-digest .agents/skills/aging-news-digest
```

Then invoke with `/aging-news-digest` or by describing the task. In Cursor and Claude Code, skills are discovered at session start — restart or open a new chat if a freshly copied skill does not appear.

## Skills

- [`aging-news-digest/`](aging-news-digest/SKILL.md) — compiles a comprehensive aging/longevity/geroscience news digest (business, conferences, research preprints & peer-reviewed papers, AI foundation models, grant opportunities) into a HEALES-style PDF and an interactive HTML dashboard. Works standalone or as a recurring scheduled task.
