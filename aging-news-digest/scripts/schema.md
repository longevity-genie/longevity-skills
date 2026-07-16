# Data schema for the aging-news-digest build scripts

`build_pdf.py` and `build_dashboard.py` both read a set of JSON files from a data directory
(default: the current directory) and are format-agnostic about *how* the data was produced —
whether by direct subagent output, or by parsing markdown research files. Instruct research
subagents to produce data matching these shapes directly wherever practical; it removes an entire
fragile regex-parsing step.

Six files, all in the same directory:

## `peerreviewed.json` — Section 2, peer-reviewed papers

A list of cluster objects:

```json
[
  {
    "name": "Cellular Senescence & SASP",
    "intro": "One paragraph, written by you, explaining why this theme matters for radical life extension.",
    "entries": [
      {
        "title": "Exact paper title, as published.",
        "authors": "Smith J, Doe A, et al",
        "journal": "Nature Aging",
        "date": "2026 Jul 10",
        "pmid": "42431471",
        "doi": "10.1038/s41586-026-xxxxx",
        "link": "https://doi.org/10.1038/s41586-026-xxxxx",
        "tag": "ORIGINAL RESEARCH",
        "abstract": "Complete verbatim abstract, never truncated. May contain \\n\\n between paragraphs."
      }
    ]
  }
]
```

`tag` must be exactly `"ORIGINAL RESEARCH"` or contain the word `REVIEW` (e.g.
`"REVIEW/PERSPECTIVE/COMMENTARY"`) — the build script keys off `"ORIGINAL" in tag.upper()` to color
the badge.

## `preprints.json` — Section 2, preprints

Same cluster-list shape, entries use slightly different field names (matching what a bioRxiv/medRxiv
connector naturally returns):

```json
[
  {
    "name": "Cellular Senescence & SASP",
    "intro": "Cluster-level paragraph.",
    "entries": [
      {
        "title": "...",
        "authors": "Lastname, F.; Lastname2, F2.",
        "server_date": "bioRxiv, posted 2026-06-19 (v1)",
        "category": "Cell Biology",
        "doi": "10.64898/2026.06.15.732173 — https://doi.org/10.64898/2026.06.15.732173",
        "type": "ORIGINAL RESEARCH",
        "published_in_journal": "Not yet (published_doi = NA)",
        "abstract": "Complete verbatim abstract."
      }
    ]
  }
]
```

## `section1.json` — Section 1a/1b, business & conferences

```json
{
  "business": [
    {"title": "...", "date": "2026-07-15", "desc": "1-3 sentence summary, may be multiple sentences.",
     "sources_md": "Sources: [Name](https://...), [Name2](https://...)"}
  ],
  "business_context": "Optional industry-wide context paragraph (not tied to one company).",
  "conf_recap": [
    {"title": "...", "event_dates": "2026-06-13 to 2026-06-19, Newry, Maine, USA",
     "cfp_deadline": "not found", "registration_deadline": "n/a",
     "status": "Already occurred (took place 13 June - 19 June 2026)"}
  ],
  "conf_upcoming": [
    {"title": "...", "event_dates": "...", "cfp_deadline": "...",
     "registration_deadline": "...", "status": "Upcoming"}
  ]
}
```

## `section3.json` — Section 3, foundation models

```json
{
  "glossary": "Plain-language glossary paragraph used once at the top of Section 3.",
  "3a_intro": "Intro paragraph for the aging-specific cluster.",
  "3a": [
    {
      "heading": "1. Model Name — 2026",
      "note_on_dating": "Optional note if slightly outside the window.",
      "what_it_is": "Plain-language explanation, jargon defined on first use.",
      "task_scale": "Task / training scale / params / license.",
      "link": "https://...",
      "code_availability": "Real GitHub/HuggingFace link, or 'No public code/model release found as of this run.'",
      "why_it_matters": "Bespoke, model-specific sentence — never generic."
    }
  ],
  "3b_intro": "Intro paragraph for the general-purpose cluster.",
  "3b": [ "... same shape as 3a entries ..." ]
}
```

## `section4.json` — Section 4, opportunities

```json
{
  "urgent": [ {"Deadline": "...", "Item": "...", "Type": "...", "Notes": "...", "Link": "..."} ],
  "grants": [
    {"Deadline": "...", "Opportunity (name + funder)": "...", "Benefit (amount + duration)": "...",
     "Eligibility (career stage / region / PhD required)": "...", "Location": "...", "Focus": "...",
     "Source": "...", "Link": "..."}
  ],
  "conferences": [
    {"Abstract/CFP deadline": "...", "Registration deadline": "...", "Event date(s)": "...",
     "Conference": "...", "Location": "...", "Focus": "...", "Source": "...", "Link": "..."}
  ],
  "recap_md": "Free-text markdown-ish block of already-decided/resolved/closed items."
}
```

`urgent`/`grants` rows are colored by the build script based on keywords in whatever column is named
`"Deadline"` — rolling/no-deadline items get a green "ROLLING" badge, anything mentioning a date in
the next few weeks gets a red "URGENT" badge, everything else gets an amber "OPEN" badge. Adjust the
`urgency_class_grant()` function in `build_pdf.py` / `urgencyClass()` in the dashboard's JS if the
urgency window changes.

## `featured_picks.json` — Featured section

```json
[
  {
    "title": "Exact paper/model title",
    "venue": "Journal, date (PMCID if full text was read) — or 'bioRxiv preprint, posted DATE'",
    "link": "https://doi.org/... or https://www.biorxiv.org/content/...",
    "fulltext_used": true,
    "summary": "6-10+ sentence original synthesis, never the verbatim abstract. Written in your own words."
  }
]
```

**Validate this file with `python3 -c "import json; json.load(open('featured_picks.json'))"`
immediately after writing it** — hand-authored prose routinely contains literal `"` characters
(quoted phrases, scare quotes) that break JSON if not escaped as `\"` or replaced with `'`.
