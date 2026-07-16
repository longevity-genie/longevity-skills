---
name: aging-news-digest
description: Compile a comprehensive aging/longevity/geroscience news digest in the style of HEALES' (Healthy Life Extension Society) monthly "Scientific News" editions authored by Sven Bulterijs. Use when the user asks to "compile the aging news digest", "make this month's HEALES digest", "aging research roundup", "longevity news digest", or when running the recurring scheduled version of this task. Produces a PDF (default), and optionally a PPTX/Google Doc/Markdown/email draft, plus an interactive HTML dashboard.
license: See repository LICENSE.
---

# Aging News Digest (HEALES "Scientific News" style)

This skill produces a broad, coverage-first sweep of everything relevant that happened in
aging/longevity/geroscience within a time window — research, business, conferences, AI/foundation
models, and grant opportunities — formatted as a HEALES-style PDF (orange-themed, title page,
section dividers, one page per research/model entry) plus a self-contained interactive HTML
dashboard. It can be run interactively (answer the PARAMETERS questions or use AUTO defaults) or
as an unattended scheduled task (in which case: execute autonomously, make reasonable choices,
note them in the output, and never take "write" actions on connectors — sending emails, posting,
etc. — unless the run explicitly asks for that specific action).

## PARAMETERS (ask the user, or use AUTO defaults for a scheduled/unattended run)

```
PERIOD             = AUTO   # AUTO = trailing 5 weeks up to today; or e.g. "1 Dec 2025 - 10 Jan 2026"
                             # — applies to Sections 1a, 2, 3
CONFERENCE_HORIZON = AUTO   # AUTO = from today through 31 December of the current year
                             # — applies to Section 1b and Section 4's conference sub-list
                             # — deliberately WIDER than PERIOD (see CURRENT-DATE AWARENESS)
MAX_ITEMS = 120              # SOFT cap only — raise it rather than dropping real news
OUTPUT    = pdf              # one of: pdf | pptx | doc | markdown | email
LANGUAGE  = English          # abstracts kept verbatim in their original language
```

If `PERIOD = AUTO`, resolve it to the window from 5 weeks before today through today, and state the
resolved dates explicitly in the output header. If `CONFERENCE_HORIZON = AUTO`, resolve it to today
through 31 December of the current year and state it explicitly too.

## CURRENT-DATE AWARENESS (mandatory, every run)

Resolve the actual current date via a bash `date` call — never assume or guess it (a past conference
being reported as upcoming is a real embarrassing mistake this skill has made before). For **every**
conference/event mentioned anywhere in the digest (Section 1b and Section 4's conference sub-list
alike), explicitly compare its event date(s) to today and label it:

- **Already occurred** (event end-date before today): label "(already took place, DD Month-DD
  Month)" and place it in Section 1b as a recap item, never in Section 4's "upcoming" list.
- **Ongoing now** (today falls within the event's date range): label "(ongoing now, through DD
  Month)".
- **Genuinely upcoming** (start-date after today): the only case that belongs in Section 4's
  "Conferences" sub-list as something to plan for.

Do this comparison for every conference, every run — never carry forward a conference's "upcoming"
status from a prior run without rechecking. Also re-verify cancellation/postponement/relocation
status every run (conference line-ups get changed with little notice) — trust the item's own
official page over any aggregator or prior write-up.

For every conference, always report three separate fields, never conflated: **event date(s)**,
**abstract/CFP submission deadline** (state "no separate CFP - registration only" if none), and
**registration deadline** if different (e.g. early-bird cutoffs).

## SCOPE NOTE

Scoped only to aging/longevity/geroscience research, business, conferences, AI/foundation models,
and grant/conference opportunities. If the account running this also runs other unrelated scheduled
tasks, never let unrelated items bleed into this digest's Section 4, even if they surface in the
same search/channel results.

## SELF-UPDATING PRINCIPLE

Every organisation, funder, conference, journal, or newsletter named anywhere in this skill is a
**bootstrap anchor / example, never a source of truth**. Every run must: (a) re-query the live
databases/aggregators named in SOURCES for the current window, (b) discover new entrants via search,
and (c) verify every time-sensitive fact (deadlines, dates, amounts, event status) against the
item's own official page before including it. Aggregators are frequently stale — never report a
date/venue/status from an aggregator without confirming on the official page; if you can't confirm,
mark it "unconfirmed - verify" rather than stating it as fact.

## GOAL

Produce a **comprehensive** digest — a broad news sweep, not a curated "best of the top journals."
Treat preprints and community/advocacy news as first-class content. Sections are clearly separated —
never mix business news, conference listings, AI/foundation-model items, and different research
types in one flat list. Five parts:

0. **Featured — picks for radical life extension** (mandatory every run, goes first after the title
   page). See FEATURED PICKS below.
1. **Business/Conferences/General news** — split into:
   - **1a. Business & industry news** — funding rounds, IPOs, government programs, company
     milestones (verify clinical-trial phase via a ClinicalTrials.gov connector rather than press
     coverage alone if available), acquisitions, launches, policy/regulatory news. Uses PERIOD.
   - **1b. Conferences & community** — using the wider CONFERENCE_HORIZON, each event labeled
     already-occurred/ongoing/upcoming; notable talks, documentaries, community/activism
     (HEALES and other advocacy orgs), fundraising campaigns.
2. **Aging research articles** — split into **preprints** and **peer-reviewed**, never interleaved.
   Within each, group by research theme/cluster (cellular senescence & SASP, epigenetics & aging
   clocks, mitochondria & metabolism, neurodegeneration, stem cells & regeneration, longevity
   genetics, musculoskeletal aging, cardiovascular aging, reproductive aging, geroprotectors,
   proteostasis/autophagy/genomic damage, computational/AI methods, general — non-exhaustive, don't
   drop a relevant theme just because it isn't listed). Within each theme, keep original
   experimental research separate from reviews/perspectives/commentaries.
3. **Foundation Models & AI for Aging** — split into:
   - **3a. Aging-specific models** — clocks of any modality, cell-state/rejuvenation models,
     mortality/healthspan predictors.
   - **3b. General-purpose biological foundation models** — protein-structure/design, DNA/genomic
     language models, single-cell/virtual-cell FMs, spatial-biology, pathology/imaging FMs,
     multi-omic FMs from major labs (Arc Institute, EvolutionaryScale/Biohub, Google DeepMind, Meta
     AI, Chan Zuckerberg Initiative, NVIDIA BioNeMo, etc.) — relevant even without an "aging" label;
     search separately and broadly, don't rely on keyword search alone to surface these.
   For every 3a/3b entry, check for a public code repo (GitHub) or model release (Hugging Face); if
   genuinely not found say so explicitly rather than omitting the question. Write in **plain
   language** — many readers are wet-lab biologists/clinicians, not ML specialists — explain jargon
   on first use per section without dumbing down the actual science.
4. **Open opportunities — conferences & grant calls** — actionable items with concrete deadlines and
   eligibility. See SECTION 4 below for the full sourcing methodology.

### FEATURED PICKS (mandatory every run)

Select ~6-10 of the most promising items from Sections 2 and 3, for a radical-life-extension
audience (advanced citizen scientists, aging researchers, longevity activists with working
scientific literacy). Criteria: strong/validated interventions, mechanistic breakthroughs with
translational plausibility, biomarker/AI tools worth tracking — favor items with available full
text. **Must be original experimental discoveries — never reviews, commentaries, or perspectives.**
If a candidate reads like a review, disqualify it and pick a genuine original-research paper
instead. For each pick: read the full text where available (PubMed/PMC connector's
`get_full_text_article`, or a preprint connector's full-text access) rather than just the abstract;
write a **custom, synthesized summary in your own words** (roughly 6-10 sentences, more if complex)
— never copy/paraphrase the verbatim abstract here, this is the one section where depth is expected.
Explain the finding, the mechanism/method, the concrete result (numbers where available), and why it
matters for radical life extension specifically. Cite title, venue/date, and a direct link/DOI.

### WHY-IT-MATTERS QUALITY BAR (read before writing any "why it matters" line)

A "why it matters" line must be grounded in what **that specific paper** found — never a generic,
topic-templated sentence copy-pasted across every item sharing a tag (e.g. never write the same
"senolytics are one of the most clinically advanced classes of intervention..." sentence on dozens
of different senescence papers). Self-check: if the same sentence could be pasted onto five other
papers in the same theme without anyone noticing, it's not specific enough — rewrite or drop it.

Given the volume in Section 2 (can run 200+ items), don't fake a per-paper line for all of them.
Instead write **one solid paragraph per research cluster** explaining why that theme matters,
visibly labeled as cluster-level, and skip the per-card line for papers in that theme. Section 3 is
small enough (typically under 10 items) that **every** model gets a genuinely bespoke "why it
matters" line — no volume excuse there. Featured picks always get bespoke treatment as part of their
full custom summary (no separate line needed).

## CONNECTOR-FIRST PRINCIPLE

Before reaching for WebSearch/WebFetch on literature or trials, run `ToolSearch` for installed MCP
connectors that do this natively (bioRxiv/medRxiv, PubMed/PMC, Elicit, ClinicalTrials.gov, Open
Targets, Synapse — connector tool names are session-specific/UUID-prefixed, search by keyword each
run rather than hardcoding names). Only fall back to WebSearch/WebFetch of `api.biorxiv.org` or
Europe PMC REST directly if a connector is unavailable or unproductive — bioRxiv/medRxiv HTML pages
block scraped WebFetch (HTTP 403).

Known connector quirks (learned the hard way, check whether still true each run):
- `search_preprints` on the bioRxiv/medRxiv connector filters by **date range + category only, no
  keyword search**, and has been observed to silently cap results at ~30/page regardless of a
  higher requested `limit` — paginate with `cursor` and pull every relevant category (cell biology,
  genetics, genomics, neuroscience, bioinformatics, molecular biology, systems biology, physiology,
  pathology, biochemistry, cancer biology, immunology, developmental biology, plus `medrxiv` for
  epidemiology/clinical), then keyword-filter titles/abstracts yourself.
- PubMed/PMC's `get_article_metadata` errors with "result exceeds maximum allowed tokens" above
  roughly 15 PMIDs per batch — but it always auto-saves the complete untruncated JSON to a file path
  given in the error message; batch in groups of ~15 and read the auto-saved file via bash/python
  (not the Read tool, to avoid re-incurring the token cost) on overflow. **Never** truncate or
  shorten an abstract to fit — split the batch instead.
- The Elicit connector's `search_papers` may return `api_access_denied` depending on the connected
  account's plan — if so, report it as an ERRORED connector in the status banner (not silently
  skipped) and proceed with PubMed/bioRxiv keyword search alone.
- `get_full_text_article` (PubMed/PMC) needs a PMCID, not a PMID — convert via `convert_article_ids`
  first, and expect many papers to have no PMC full text at all (report "abstract-based" for those
  Featured Picks rather than guessing).

## CONNECTOR-STATUS BANNER (mandatory, every run)

At the very top of the output, before the Featured section, list every connector attempted this
run — literature connectors (bioRxiv/medRxiv, PubMed/PMC, Elicit, ClinicalTrials.gov, Open Targets,
Synapse) are expected every run, each gets an explicit OK / ERRORED / EMPTY-SUSPICIOUS status.
Telegram/WhatsApp/Gmail (optional, Section 4 only) get "not connected, skipped" if absent, or a named
callout if connected-but-broken. Never say "connectors worked fine" as a blanket statement — name
each one.

## SECTION 4 — OPPORTUNITIES SOURCING & FORMAT

**Step 0, always first:** read the prior run's Section 4 (if this is a recurring/scheduled run and a
previous digest exists) before searching anything new — build a mental list of what's tracked and
its last-verified status.

**Caching policy:** carry forward an item unchanged (citing "carried from prior run") if it has a
confirmed real URL, a fixed deadline that hasn't arrived, and nothing was flagged uncertain last
time — but always re-run the CURRENT-DATE AWARENESS comparison for conferences even when carrying
other details forward. Re-check anything marked "verify"/"TBD" last time, anything with a rolling or
soon-arriving deadline (within ~10 days), or anything not yet PhD-eligibility-checked.

**Verify, don't assume:** a well-known funder/mechanism being famous or previously open does not
mean it's open now — many "obvious" big names (Horizon Europe Cluster 1's general topics, AFAR's
non-Hevolution programs, Hevolution's direct grant pages, Longevity Impetus Grants) sit closed/stale
for long stretches with outdated "current" language left on the page. Always fetch the live page
directly and check the actual current deadline. Explicitly check ALL of: AFAR (all named programs,
not just the flagship), NIA Division of Aging Biology NOFOs (cross-check grants.nih.gov), Hevolution
Foundation direct grants, Longevity Impetus Grants, Longevity Science Foundation, American Aging
Association, Nathan Shock Centers, SENS Research Foundation, Wellcome Discovery Awards, Chan
Zuckerberg Initiative, DFG (Sachbeihilfe/Emmy Noether/Walter Benjamin — rolling), UEFISCDI,
Horizon Europe Cluster 1 Health work-programme PDF, EIC Pathfinder Challenges, IHI open calls, MSCA
Postdoctoral Fellowships + Doctoral Networks, Eureka/Eurostars/Globalstars. A short Section 4 list
is usually a sign of not having checked broadly enough — report each mechanism's actual live status
(open with deadline, or closed/stale — and say so, that's useful information too).

**Conference sourcing:** primary source is AgingBiotech.info (agingbiotech.info/conferences and
/opportunities) — note that almost every content page there is a thin HTML shell whose real content
is an iframe pointing to a published Google Sheet/Doc: WebFetch the page, extract the
`docs.google.com/...` URL from the returned plain text (WebFetch cannot open docs.google.com
directly), then open that exact URL with Claude-in-Chrome (`navigate` + `get_page_text`). Also check
Longevity Events (longevents.hyperadvancer.com), Longevity Alliance, Lifespan.io, SENS. Cross-check
every date/venue/status against the conference's own official site — the sheet's free-text notes
column is often the most current source (it has, historically, correctly flagged a major conference
relocation that some third-party writeups missed).

**Optional multi-channel sourcing:** if Telegram/WhatsApp/Gmail connectors happen to be available,
scan connected chats/inbox for aging-relevant grant/fellowship/conference mentions (never assume a
specific channel/group name exists — discover what's actually connected each run) — filter hard for
topical fit and report the hit rate. Every entry sourced this way needs the real URL pulled from the
message text itself; drop the entry rather than inventing a link if none can be found. These three
are fully optional — the skill must work correctly with none of them present.

**Verification required for anything new:** actually fetch the source page for eligibility/deadline
before including it (never paraphrase a headline or guess a domain); for anything that could
plausibly require a completed PhD (postdoc programs, "Fellow" titles), explicitly state whether a
doctorate is required for the PI/lead applicant.

**Table format** — for each item: Deadline | Opportunity (name+funder) | Benefit (amount+duration,
or format/fee for conferences) | Eligibility (career stage, region, PhD-required Y/N) | Location
(flag USA in-person as visa/cost-heavy, EU in-person as cheap/easy travel) | Focus/Audience | Source
(exactly where found) | Link (real, direct — never a placeholder). Conference rows split Deadline
into abstract/CFP deadline, registration deadline, and event date(s) as three separate fields.

**Structure:** "Urgent" (due within 2-3 weeks, grants or conferences) first, then "Grant / funding
calls" and "Conferences" sorted soonest-deadline first, then a "Status recap" of already-decided or
confirmed-closed/stale items (context only, keeps resolved items traceable rather than silently
vanishing). This section is a **living document** across runs when used as a recurring task — update
rather than regenerate from zero; move newly-passed deadlines into the recap with an outcome if
known.

## SOURCES

**Maintained living sources (check first):**
- AgingBiotech.info — companies/investors/nonprofits DB, conferences calendar, opportunities list
  (see the Google-Sheet-iframe note above).
- Longevity Events (longevents.hyperadvancer.com), Longevity Alliance, Lifespan.io, SENS, HEALES.
- Grants: AFAR, NIA, Hevolution, Longevity Impetus Grants, Longevity Science Foundation, American
  Aging Association, Nathan Shock Centers, DFG, UEFISCDI, Horizon Europe Cluster 1, EIC Pathfinder,
  IHI, MSCA, Eureka/Eurostars.
- Interventions/pipeline: Lifespan.io Rejuvenation Roadmap.
- Reference DBs: HAGR (genomics.senescence.info — GenAge, DrugAge, LongevityMap, CellAge).
- Foundation-model lists: "awesome" GitHub repos (bio-foundation-models, single-cell, protein
  foundation models), rewire.it/blog, and major-lab release pages/blogs directly (Arc Institute,
  EvolutionaryScale/Biohub, Google DeepMind, Meta AI/FAIR, Chan Zuckerberg Initiative, NVIDIA
  BioNeMo, Ginkgo Bioworks, Recursion).

**Literature (all journals/impact levels, no prestige filter):** bioRxiv/medRxiv (preprints, tag
PREPRINT), PubMed/PMC (peer-reviewed), Elicit (semantic cross-check), arXiv q-bio/cs.LG (foundation
models, WebSearch — no dedicated connector as of this writing).

**News/community:** Lifespan.io, Longevity.Technology, Fierce Biotech, Endpoints; rewire.it/blog,
"In Search Of" (Julia Klim); HEALES channels, Longevity Alliance, other advocacy orgs. Search for
new relevant newsletters each run and fold them in.

## SELECTION

Coverage over selectivity — capture everything relevant in PERIOD, no top-tier-journal filter (the
real HEALES editions are mostly preprints and specialist-journal papers). Span the whole field:
mechanistic & interventional biology, biomarkers/clocks of any type, longevity genetics, stem-cell
aging & rejuvenation, neurodegeneration, senescence & senolytics, calorie restriction &
pharmacological interventions, etc. — these are examples, not a whitelist. De-duplicate preprints
that later appeared as journal articles (keep the journal version, note the preprint). MAX_ITEMS is
a soft cap — raise it rather than dropping real news; push overflow into an "Also notable" list
(title + link) so nothing is silently cut, and report true totals found.

## IMPLEMENTATION GUIDE (how to actually execute this without blowing context or timing out)

This digest routinely runs to 300-500+ items across all sections. Doing the research and the
document-building in the same context window does not scale. Use this pipeline:

1. **Fan out research to parallel subagents**, one per vertical: (a) Section 1a+1b (business +
   conferences, mostly WebSearch/WebFetch/Chrome), (b) Section 2 preprints (bioRxiv/medRxiv
   connector), (c) Section 2 peer-reviewed (PubMed/PMC + Elicit), (d) Section 3 (foundation models,
   mixed connectors + WebSearch), (e) Section 4 (grants/conferences, mixed). Give each subagent the
   exact date-resolved PERIOD/CONFERENCE_HORIZON, the relevant methodology sections above verbatim,
   and an explicit instruction to **write structured output to a specific file path** rather than
   return it all in the chat response (a 350-paper batch will blow past tool-result size limits).
   Tell every subagent explicitly to run `ToolSearch` for the relevant connectors first, and to
   never truncate/shorten an abstract to fit a size limit — split into more file-writes instead.

2. **Standardize the output schema.** Rather than letting each subagent invent its own prose format
   and then regex-parsing it afterward (fragile, and this skill's first run needed several rounds of
   parser-debugging to recover from inconsistent formatting), instruct subagents to write directly
   to the JSON schema documented in `scripts/schema.md` in this skill folder — one file per section,
   or all into a single `research_data.json` if the run is small enough. This makes the downstream
   build step deterministic instead of regex-guessing.

3. **Read back only small samples**, never whole multi-hundred-KB files, to sanity-check structure
   before building. Use `bash`/`jq`/`python` to probe/validate large JSON or tool-result files rather
   than the `Read` tool, which chunks by line count and can silently truncate large payloads.

4. **Build the PDF via `scripts/build_pdf.py`** (bundled in this skill), which reads
   `research_data.json` and produces `digest_full.html`, styled with the HEALES orange theme
   (title page, connector banner, one page per Featured pick / Section 2 & 3 entry, flowing cards
   for Section 1, color-coded tables for Section 4). **Do not render the whole HTML to PDF in one
   `weasyprint` call if it's very long** — the sandbox's bash tool call has a hard ~45-second
   timeout and background processes do **not** survive between tool calls (each bash invocation is
   a fresh, isolated container). Instead: split the HTML at section/cluster boundaries into 5-8
   chunks (the script's `split_chunks` step does this automatically), render each chunk to its own
   PDF within one bash call (weasyprint renders roughly 15-25 pages/second, so a ~400-500 page
   digest splits comfortably into chunks that each render in under 15 seconds), then merge with
   `pypdf.PdfWriter`. Verify the final page count and spot-check `extract_text()` on a few pages
   before presenting it.

5. **Build the HTML dashboard via `scripts/build_dashboard.py`**, which embeds the same JSON as a
   `<script>` data blob plus vanilla-JS tab/search filtering — no build step, no external network
   calls except (optionally) a CDN font. After writing it, grep-count `<script` vs `</script` (must
   be equal — an abstract containing a literal `</script>`-like string would otherwise break the
   page) and run `node --check` on the extracted JS to catch template-literal/quoting errors before
   presenting it.

6. **JSON-escaping gotcha:** if any research content is hand-authored (e.g. Featured Pick summaries
   written directly by the orchestrating agent rather than a subagent), remember that JSON string
   values cannot contain a literal, unescaped `"` — quoted phrases inside prose ("don't eat me"
   signals, "why it matters" asides, etc.) must use escaped quotes (`\"`) or single quotes, or the
   file will fail to parse. Validate with `python3 -c "import json; json.load(open(...))"` immediately
   after writing any hand-authored JSON, before building anything downstream from it.

7. **Present only the final deliverables** (PDF + dashboard HTML) via the file-sharing mechanism —
   keep intermediate JSON/HTML/scripts in a working subfolder, not mixed in with what's shown to the
   user.

## OUTPUT FORMAT (PDF default — see `scripts/build_pdf.py` for the exact implementation)

Title page ("Scientific News — Aging Research Digest", resolved PERIOD, resolved
CONFERENCE_HORIZON, run date) immediately followed by the connector-status banner, then Featured
(one page per pick), then an orange divider page per section/sub-section (Section name + a plain
prose overview paragraph — never literally prefixed "TL;DR:"), then content. Section 2's preprint/
peer-reviewed dividers sub-divide by cluster with a cluster-level overview. One page per entry within
Featured, Section 2, and Section 3 (bold title, authors where applicable, full verbatim abstract,
PREPRINT tag centered at top where applicable, paper-specific "why it matters" only where genuinely
specific). Section 1 renders as flowing short-form cards, not one page each. Section 4 renders as
color-coded tables (red = urgent, amber = open with deadline, green = rolling/open-ended, grey =
status recap). Large, readable fonts and generous spacing — a cramped/ugly layout has been flagged
before, don't regress.

For `OUTPUT = pptx`: same section structure via the pptx skill, one slide per entry. For `doc`:
Google Drive doc titled "Scientific News — <PERIOD>". For `markdown`: a single `.md` file, same
structure. For `email`: create (never send) a Gmail draft with the digest in the body.

**Optional artifact:** also produce a single self-contained interactive HTML dashboard (tabbed:
Featured / Business & Industry / Conferences & Community / Foundation Models (3a/3b) / Research —
Preprints / Research — Peer-Reviewed / Open Opportunities), each tab with its own overview paragraph
and a search box scoped to that tab. Don't also ship a standalone data.json/items.csv as a
user-facing deliverable — keep those as internal working files only.

Always print a concise chat summary: resolved PERIOD, resolved CONFERENCE_HORIZON, counts per
section, Featured Pick titles, connector health (name every connector, OK or broken), and where
every output file was saved. Never auto-send email or post to any channel without explicit
confirmation.

## Copyright note

Abstracts are reproduced verbatim as bibliographic excerpts with full attribution and links, matching
the existing HEALES editions. Never reproduce full article bodies in the output — full text may be
read privately to write a Featured Pick summary, but only the custom summary is published.
