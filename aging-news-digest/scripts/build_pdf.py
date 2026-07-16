#!/usr/bin/env python3
"""
Build the HEALES-style "Scientific News" Aging Digest PDF from a set of JSON data files.

See schema.md in this same folder for the exact shape of each input file.

Usage:
    python3 build_pdf.py --data-dir . --period "11 June 2026 - 16 July 2026 (trailing 5 weeks)" \\
        --horizon "16 July 2026 - 31 December 2026" --compiled 2026-07-16 --out digest_full

This writes <out>.html (for inspection / debugging) plus a set of digest_full_chunk*.html files
and merges the rendered PDFs into <out>.pdf.

IMPORTANT — long-document rendering: the shell tool this was designed under has a hard ~45s
timeout per call and background processes do not survive between calls. This script therefore
splits the HTML at section/cluster boundaries and calls weasyprint separately per chunk when
run via `--render-chunks`; a orchestrating agent should call this script once with
`--split-only` to produce the chunk HTML files, then render each chunk PDF in its own shell call
(weasyprint renders roughly 15-25 pages/second), then run this script again with `--merge-only`
to combine them with pypdf. See the "Split / render / merge" section at the bottom of this file
for the exact three-step invocation.
"""
import json, html, re, os, sys, argparse, glob

def load(data_dir, name, required=True):
    path = os.path.join(data_dir, name)
    if not os.path.exists(path):
        if required:
            raise FileNotFoundError(f"Missing required data file: {path}")
        return None
    with open(path, encoding='utf-8') as f:
        return json.load(f)

def esc(s):
    return html.escape(s or '', quote=False)

def md_inline(s):
    """Very small markdown->html for bold/links used inside data fields."""
    if not s:
        return ''
    s = esc(s)
    s = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', s)
    s = re.sub(r'\[(.+?)\]\((https?://[^\s)]+)\)', r'<a href="\2">\1</a>', s)
    s = re.sub(r'(?<!["\'>])(https?://[^\s<]+)', r'<a href="\1">\1</a>', s)
    return s

def para(text):
    text = md_inline(text)
    parts = [p for p in text.split('\n\n') if p.strip()]
    return ''.join(f'<p>{p}</p>' for p in parts) or f'<p>{text}</p>'

CSS = """
@page {
  size: A4;
  margin: 20mm 18mm 22mm 18mm;
  @bottom-center { content: "HEALES Scientific News \\2014 Aging Research Digest \\2014 " counter(page); font-size: 8pt; color: #9b8a7a; }
}
@page cover { margin: 0; }
* { box-sizing: border-box; }
body { font-family: "Noto Sans", "DejaVu Sans", Arial, sans-serif; color: #2b2018; font-size: 11pt; line-height: 1.5; }
.orange { color: #E67E22; }
h1, h2, h3, h4 { font-family: "Noto Sans", Arial, sans-serif; color: #7a3b0e; line-height: 1.25; }
a { color: #c0521c; text-decoration: none; }

.cover-page { page: cover; page-break-after: always; height: 297mm; width: 210mm;
  background: linear-gradient(160deg, #E67E22 0%, #C0521C 55%, #7a3b0e 100%);
  color: white; display: flex; flex-direction: column; justify-content: center; align-items: center; text-align: center; padding: 30mm; }
.cover-page .kicker { letter-spacing: 4px; text-transform: uppercase; font-size: 13pt; opacity: 0.9; margin-bottom: 10mm; }
.cover-page h1 { color: white; font-size: 34pt; margin: 0 0 8mm 0; }
.cover-page .sub { font-size: 15pt; margin-bottom: 14mm; opacity: 0.95;}
.cover-page .meta { font-size: 11pt; background: rgba(255,255,255,0.14); border-radius: 10px; padding: 6mm 8mm; margin-top: 8mm; line-height: 1.8;}
.cover-page .foot { position: absolute; bottom: 16mm; font-size: 9pt; opacity: 0.85; }

.banner-page { page-break-after: always; }
.banner-page h2 { border-bottom: 3px solid #E67E22; padding-bottom: 3mm; }
.conn-table { width: 100%; border-collapse: collapse; margin-top: 6mm; font-size: 10pt;}
.conn-table th { background: #f3e3d3; text-align: left; padding: 3mm 4mm; color: #7a3b0e;}
.conn-table td { padding: 3mm 4mm; border-bottom: 1px solid #eee; vertical-align: top;}
.status-ok { color: #1a7a3c; font-weight: bold; }
.status-err { color: #b0231c; font-weight: bold; }
.status-empty { color: #b0761c; font-weight: bold; }
.status-skip { color: #888; font-weight: bold; }

.divider { page-break-before: always; page-break-after: always;
  background: linear-gradient(160deg, #f7ead9 0%, #f0d3ab 100%); height: 257mm;
  display:flex; flex-direction:column; justify-content:center; padding: 20mm 22mm; border-left: 14px solid #E67E22;}
.divider .tag { text-transform:uppercase; letter-spacing:3px; color:#c0521c; font-size:11pt; margin-bottom:6mm;}
.divider h1 { font-size: 26pt; margin: 0 0 8mm 0; color:#7a3b0e;}
.divider p { font-size: 12pt; color:#4a3826; line-height:1.7;}

.subdivider { page-break-before: always; background:#fbf3e9; border-left: 10px solid #E67E22; padding: 10mm 12mm; margin-bottom: 6mm;}
.subdivider h2 { margin: 0 0 4mm 0; font-size: 17pt;}
.subdivider p { font-size: 10.5pt; color:#4a3826; margin:0;}

.entry-page { page-break-before: always; padding-top: 2mm; }
.preprint-tag { text-align:center; letter-spacing:3px; font-weight:bold; color:white; background:#c0521c; border-radius: 3px; padding: 2mm 0; font-size: 10pt; margin-bottom: 5mm; }
.entry-title { font-size: 14pt; font-weight:bold; color:#3a2a18; margin-bottom:2mm;}
.entry-meta { font-size: 9.5pt; color:#8a6a4a; margin-bottom:4mm; }
.entry-tag { display:inline-block; font-size:8pt; font-weight:bold; letter-spacing:1px; padding:1mm 3mm; border-radius:3px; margin-left:2mm;}
.tag-original { background:#dff0d8; color:#1a7a3c;}
.tag-review { background:#f0e2c8; color:#8a5a1c;}
.abstract-block { font-size: 10.3pt; text-align: justify; border-left: 3px solid #e8c39a; padding-left: 4mm; margin-top:3mm;}
.why-matters { margin-top: 5mm; background:#fbf3e9; border-radius:5px; padding:4mm 5mm; font-size:10pt;}
.why-matters .lbl { font-weight:bold; color:#7a3b0e; }
.entry-link { margin-top: 4mm; font-size: 9.5pt;}

.cluster-intro-box { background:#fbf3e9; padding:4mm 5mm; border-radius:5px; font-size:10pt; margin-bottom:5mm;}

.featured-page { page-break-before: always; }
.featured-badge { display:inline-block; background:#E67E22; color:white; font-size:9pt; font-weight:bold; padding:1mm 4mm; border-radius:10px; margin-bottom:3mm;}
.featured-title { font-size: 15pt; font-weight:bold; color:#3a2a18; }
.featured-venue { font-size: 10pt; color:#8a6a4a; margin-bottom: 4mm;}
.featured-summary { font-size: 10.6pt; text-align:justify; }
.featured-summary p { margin: 0 0 3mm 0;}

.list-item { margin-bottom: 5mm; padding-bottom: 4mm; border-bottom: 1px solid #eee; }
.list-item h4 { margin: 0 0 1mm 0; font-size: 11.5pt; color:#3a2a18;}
.list-item .date { font-size: 9pt; color:#8a6a4a;}
.list-item p { font-size: 10.3pt; margin: 2mm 0;}
.list-item .src { font-size: 9pt; }

.conf-card { margin-bottom: 5mm; padding: 3mm 4mm; border-left: 4px solid #E67E22; background:#fffaf3;}
.conf-card.occurred { border-left-color:#aaa; background:#f6f6f6;}
.conf-card h4 { margin:0 0 1mm 0; font-size: 11pt;}
.conf-card .fields { font-size: 9.3pt; color:#4a3826; }
.badge { display:inline-block; font-size:8pt; font-weight:bold; padding:0.5mm 2.5mm; border-radius:8px; margin-left:2mm;}
.badge-upcoming { background:#dff0d8; color:#1a7a3c;}
.badge-occurred { background:#e0e0e0; color:#555;}

table.opp-table { width:100%; border-collapse:collapse; font-size: 8.7pt; margin-bottom:6mm;}
table.opp-table th { background:#7a3b0e; color:white; padding:2mm 2mm; text-align:left;}
table.opp-table td { padding:2mm 2mm; border-bottom:1px solid #e8dcc8; vertical-align:top;}
tr.urgent td { background:#fde3e0; }
tr.soon td { background:#fdecd0; }
tr.open td { background:#e6f4e2; }
.urg-badge { background:#c0271c; color:white; padding:0.5mm 2mm; border-radius:6px; font-size:8pt; font-weight:bold;}
.soon-badge { background:#d98a1c; color:white; padding:0.5mm 2mm; border-radius:6px; font-size:8pt; font-weight:bold;}
.open-badge { background:#2c8a4a; color:white; padding:0.5mm 2mm; border-radius:6px; font-size:8pt; font-weight:bold;}
.recap-badge { background:#888; color:white; padding:0.5mm 2mm; border-radius:6px; font-size:8pt; font-weight:bold;}
.recap-text { font-size: 9.3pt; white-space: pre-wrap; }
"""

def entry_tag_class(tag):
    return 'tag-original' if 'ORIGINAL' in (tag or '').upper() else 'tag-review'

def render_peer_entry(e):
    tagcls = entry_tag_class(e['tag'])
    preprint_tag = ''
    journal = e.get('journal', '')
    if 'biorxiv' in journal.lower() or 'medrxiv' in journal.lower() or '(preprint)' in journal.lower():
        preprint_tag = '<div class="preprint-tag">PREPRINT (indexed via PubMed)</div>'
    return f"""
<div class="entry-page">
  {preprint_tag}
  <div class="entry-title">{esc(e['title'])} <span class="entry-tag {tagcls}">{esc(e['tag'])}</span></div>
  <div class="entry-meta">{esc(e['authors'])} &middot; <em>{esc(e['journal'])}</em>, {esc(e['date'])} &middot; PMID: {esc(e.get('pmid',''))}</div>
  <div class="abstract-block">{para(e['abstract'])}</div>
  <div class="entry-link">DOI: <a href="{esc(e.get('link',''))}">{esc(e.get('doi',''))}</a></div>
</div>"""

def render_preprint_entry(e):
    return f"""
<div class="entry-page">
  <div class="preprint-tag">PREPRINT</div>
  <div class="entry-title">{esc(e['title'])} <span class="entry-tag {entry_tag_class(e.get('type',''))}">{esc(e.get('type',''))}</span></div>
  <div class="entry-meta">{esc(e.get('authors',''))} &middot; {esc(e.get('server_date',''))} &middot; Category: {esc(e.get('category',''))}</div>
  <div class="abstract-block">{para(e['abstract'])}</div>
  <div class="entry-link">DOI: {md_inline(e.get('doi',''))}<br/>Published in journal: {esc(e.get('published_in_journal',''))}</div>
</div>"""

def render_cluster(cluster_name, intro, entries, render_fn):
    out = f"""
<div class="subdivider">
  <h2>{esc(cluster_name)}</h2>
  <p>{md_inline(intro)}</p>
</div>"""
    for e in entries:
        out += render_fn(e)
    return out

def render_fm_entry(e):
    dating_note = f'<p style="font-size:9pt;color:#8a6a4a;"><em>Note on dating:</em> {md_inline(e["note_on_dating"])}</p>' if e.get('note_on_dating') else ''
    return f"""
<div class="entry-page">
  <div class="entry-title">{esc(e['heading'])}</div>
  {dating_note}
  <div class="abstract-block">
    <p><strong>What it is, in plain language:</strong> {md_inline(e['what_it_is'])}</p>
    <p><strong>Task / scale:</strong> {md_inline(e['task_scale'])}</p>
    <p><strong>Link:</strong> {md_inline(e['link'])}</p>
    <p><strong>Code / model availability:</strong> {md_inline(e['code_availability'])}</p>
  </div>
  <div class="why-matters"><span class="lbl">Why it matters:</span> {md_inline(e['why_it_matters'])}</div>
</div>"""

def render_featured(f):
    return f"""
<div class="featured-page">
  <div class="featured-badge">FEATURED PICK &mdash; RADICAL LIFE EXTENSION</div>
  <div class="featured-title">{esc(f['title'])}</div>
  <div class="featured-venue">{esc(f['venue'])} &middot; <a href="{esc(f['link'])}">{esc(f['link'])}</a> {"&middot; full text read" if f.get('fulltext_used') else "&middot; abstract-based (full text not available)"}</div>
  <div class="featured-summary">{para(f['summary'])}</div>
</div>"""

def render_business_item(item):
    return f"""
<div class="list-item">
  <h4>{esc(item['title'])} <span class="date">({esc(item['date'])})</span></h4>
  <p>{md_inline(item['desc'])}</p>
  <div class="src">{md_inline(item.get('sources_md',''))}</div>
</div>"""

def render_conf_item(item, occurred):
    cls = 'occurred' if occurred else ''
    badge = '<span class="badge badge-occurred">ALREADY OCCURRED</span>' if occurred else '<span class="badge badge-upcoming">UPCOMING</span>'
    return f"""
<div class="conf-card {cls}">
  <h4>{esc(item['title'])} {badge}</h4>
  <div class="fields">
    <strong>Event date(s):</strong> {md_inline(item.get('event_dates',''))}<br/>
    <strong>Abstract/CFP deadline:</strong> {md_inline(item.get('cfp_deadline','') or 'not found')}<br/>
    <strong>Registration deadline:</strong> {md_inline(item.get('registration_deadline','') or 'not found')}<br/>
    <strong>Status:</strong> {md_inline(item.get('status',''))}
  </div>
</div>"""

def urgency_class_grant(deadline, urgent_keywords):
    d = (deadline or '').lower()
    if any(k in d for k in urgent_keywords):
        return 'urgent', 'urg-badge', 'URGENT'
    if 'rolling' in d or 'ongoing' in d or 'no deadline' in d:
        return 'open', 'open-badge', 'ROLLING'
    return 'soon', 'soon-badge', 'OPEN'

def render_grants_table(rows, urgent_keywords):
    if not rows:
        return '<p><em>None found.</em></p>'
    keys = list(rows[0].keys())
    out = '<table class="opp-table"><thead><tr>' + ''.join(f'<th>{esc(k)}</th>' for k in keys) + '<th>Status</th></tr></thead><tbody>'
    for r in rows:
        deadline = r.get('Deadline', '')
        rowcls, badgecls, label = urgency_class_grant(deadline, urgent_keywords)
        out += f'<tr class="{rowcls}">' + ''.join(f'<td>{md_inline(r.get(k,""))}</td>' for k in keys) + f'<td><span class="{badgecls}">{label}</span></td></tr>'
    out += '</tbody></table>'
    return out

def render_conf_table(rows):
    if not rows:
        return '<p><em>None found.</em></p>'
    keys = list(rows[0].keys())
    out = '<table class="opp-table"><thead><tr>' + ''.join(f'<th>{esc(k)}</th>' for k in keys) + '</tr></thead><tbody>'
    for r in rows:
        out += '<tr>' + ''.join(f'<td>{md_inline(r.get(k,""))}</td>' for k in keys) + '</tr>'
    out += '</tbody></table>'
    return out

def status_css(s):
    if s.startswith('OK'):
        return 'status-ok'
    if 'ERROR' in s.upper():
        return 'status-err'
    if 'skipped' in s.lower():
        return 'status-skip'
    return 'status-empty'

def build_html(args):
    peer = load(args.data_dir, 'peerreviewed.json')
    prep = load(args.data_dir, 'preprints.json')
    sec1 = load(args.data_dir, 'section1.json')
    sec3 = load(args.data_dir, 'section3.json')
    sec4 = load(args.data_dir, 'section4.json')
    featured = load(args.data_dir, 'featured_picks.json')
    conn_status = load(args.data_dir, 'connector_status.json', required=False) or [
        ["bioRxiv/medRxiv connector", "OK", "Fill in real status."],
        ["PubMed/PMC connector", "OK", "Fill in real status."],
        ["Elicit connector", "OK", "Fill in real status."],
        ["ClinicalTrials.gov connector", "OK", "Fill in real status."],
        ["Open Targets connector", "OK", "Fill in real status."],
        ["Synapse connector", "OK", "Fill in real status."],
        ["Telegram connector", "Not connected, skipped", ""],
        ["WhatsApp connector", "Not connected, skipped", ""],
        ["Gmail connector", "Not connected, skipped", ""],
    ]

    urgent_keywords = [k.strip() for k in args.urgent_keywords.split(',')] if args.urgent_keywords else ['urgent']

    parts = [f"<html><head><meta charset='utf-8'><style>{CSS}</style></head><body>"]

    parts.append(f"""
<div class="cover-page">
  <div class="kicker">HEALES &middot; Healthy Life Extension Society</div>
  <h1>Scientific News</h1>
  <div class="sub">Aging Research Digest</div>
  <div class="meta">
    News period: {esc(args.period)}<br/>
    Conference &amp; opportunity horizon: {esc(args.horizon)}<br/>
    Compiled: {esc(args.compiled)}
  </div>
  <div class="foot">In the style of the monthly editions authored by Sven Bulterijs for HEALES</div>
</div>""")

    rows_html = ''.join(f'<tr><td>{esc(n)}</td><td class="{status_css(s)}">{esc(s)}</td><td>{md_inline(d)}</td></tr>' for n, s, d in conn_status)
    parts.append(f"""
<div class="banner-page">
  <h2>Connector Status Banner</h2>
  <p>Status of every data connector attempted in this run.</p>
  <table class="conn-table"><thead><tr><th>Connector</th><th>Status</th><th>Notes</th></tr></thead><tbody>{rows_html}</tbody></table>
</div>""")

    parts.append('<div class="divider"><div class="tag">Part 0</div><h1>Featured &mdash; Picks for Radical Life Extension</h1><p>A hand-selected set of the most promising original-research findings and AI/biomarker tools from this edition&#39;s Sections 2 and 3.</p></div>')
    for f in featured:
        parts.append(render_featured(f))

    parts.append('<div class="divider"><div class="tag">Section 1a</div><h1>Business &amp; Industry News</h1><p>Funding rounds, clinical-trial milestones, company news, and policy developments in aging/longevity biotech from the news period.</p></div>')
    biz_html = ''.join(render_business_item(i) for i in sec1['business'])
    ctx = sec1.get('business_context', '')
    parts.append(f'<div style="padding-top:4mm;">{biz_html}' + (f'<div class="cluster-intro-box"><strong>Industry-wide context:</strong> {md_inline(ctx)}</div>' if ctx else '') + '</div>')

    parts.append('<div class="divider"><div class="tag">Section 1b</div><h1>Conferences &amp; Community</h1><p>Every conference below is explicitly dated against today and labeled already-occurred or upcoming.</p></div>')
    parts.append('<h3 style="margin-top:0;">Already occurred (recap)</h3>')
    parts.append(''.join(render_conf_item(i, True) for i in sec1.get('conf_recap', [])))
    parts.append('<h3>Upcoming</h3>')
    parts.append(''.join(render_conf_item(i, False) for i in sec1.get('conf_upcoming', [])))

    n_prep = sum(len(c['entries']) for c in prep)
    parts.append(f'<div class="divider"><div class="tag">Section 2 &mdash; Preprints</div><h1>Aging Research: Preprints</h1><p>{n_prep} preprints screened as aging/longevity-relevant for this window. Grouped by research theme; original experimental work is kept separate from reviews within each theme.</p></div>')
    for c in prep:
        parts.append(render_cluster(c['name'], c['intro'], c['entries'], render_preprint_entry))

    n_peer = sum(len(c['entries']) for c in peer)
    parts.append(f'<div class="divider"><div class="tag">Section 2 &mdash; Peer-Reviewed</div><h1>Aging Research: Peer-Reviewed Articles</h1><p>{n_peer} peer-reviewed papers for this window, spanning all impact levels. Grouped by research theme; original experimental work is kept separate from reviews within each theme.</p></div>')
    for c in peer:
        parts.append(render_cluster(c['name'], c['intro'], c['entries'], render_peer_entry))

    parts.append(f'<div class="divider"><div class="tag">Section 3</div><h1>Foundation Models &amp; AI for Aging</h1><p>{md_inline(sec3.get("glossary",""))}</p></div>')
    parts.append(f'<div class="subdivider"><h2>3a &mdash; Aging-Specific Models</h2><p>{md_inline(sec3.get("3a_intro",""))}</p></div>')
    for e in sec3.get('3a', []):
        parts.append(render_fm_entry(e))
    parts.append(f'<div class="subdivider"><h2>3b &mdash; General-Purpose Biological Foundation Models</h2><p>{md_inline(sec3.get("3b_intro",""))}</p></div>')
    for e in sec3.get('3b', []):
        parts.append(render_fm_entry(e))

    parts.append('<div class="divider"><div class="tag">Section 4</div><h1>Open Opportunities: Conferences &amp; Grant Calls</h1><p>Actionable items with concrete deadlines and eligibility, checked against live official pages. Red = urgent, amber = open with a set deadline, green = rolling/open-ended.</p></div>')
    parts.append('<h3 style="margin-top:0;">Urgent</h3>')
    parts.append(render_grants_table(sec4.get('urgent', []), urgent_keywords))
    parts.append('<h3>Grant / funding calls</h3>')
    parts.append(render_grants_table(sec4.get('grants', []), urgent_keywords))
    parts.append('<h3>Conferences</h3>')
    parts.append(render_conf_table(sec4.get('conferences', [])))
    parts.append('<div class="subdivider" style="page-break-before: always;"><h2>Status recap</h2><p>Mechanisms and conferences checked and found closed, stale, already passed, or resolved.</p></div>')
    recap_html = md_inline(sec4.get('recap_md', '')).replace('\n\n', '</p><p>').replace('\n', '<br/>')
    parts.append(f'<div class="recap-text"><p>{recap_html}</p></div>')

    parts.append("</body></html>")
    return ''.join(parts), n_prep, n_peer


def split_html(full_html, n_chunks=7, max_chunk_chars=180_000):
    """Split into byte-size-balanced pieces at safe boundaries (divider/subdivider/entry-page
    starts) for chunked weasyprint rendering. n_chunks is a soft target; max_chunk_chars is the
    hard cap used to keep any single weasyprint call fast enough for a ~45s shell-tool timeout
    (weasyprint renders roughly 15-25 pages/second; 180k chars of this template is comfortably
    under 15s even on the slowest chunks observed in testing)."""
    head_end = full_html.find('</head>') + 7
    body_start = full_html.find('<body>') + 6
    head = full_html[:head_end]
    end = full_html.rfind('</body>')

    # Any of these class openings is a safe page-break point.
    boundary_re = re.compile(r'<div class="(?:divider|subdivider|entry-page|featured-page|list-item|conf-card)')
    boundary_positions = [m.start() for m in boundary_re.finditer(full_html) if body_start < m.start() < end]
    bounds = sorted(set([body_start] + boundary_positions + [end]))

    # Greedily accumulate boundaries into chunks capped at max_chunk_chars.
    chunks = []
    chunk_start = bounds[0]
    for i in range(1, len(bounds)):
        if bounds[i] - chunk_start > max_chunk_chars:
            chunks.append(full_html[chunk_start:bounds[i - 1]])
            chunk_start = bounds[i - 1]
    chunks.append(full_html[chunk_start:end])

    docs = [head + '<body>' + c + '</body></html>' for c in chunks if c.strip()]
    return docs


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--data-dir', default='.')
    ap.add_argument('--period', required=True)
    ap.add_argument('--horizon', required=True)
    ap.add_argument('--compiled', required=True)
    ap.add_argument('--out', default='digest_full')
    ap.add_argument('--urgent-keywords', default='urgent',
                     help='Comma-separated substrings of "Deadline" values that should render as URGENT (red).')
    ap.add_argument('--mode', choices=['html', 'split', 'merge'], default='html',
                     help='html: write the full single HTML file. split: write chunk HTML files '
                          'for separate weasyprint calls. merge: merge existing chunk*.pdf files '
                          'in --data-dir into <out>.pdf using pypdf.')
    ap.add_argument('--n-chunks', type=int, default=7)
    args = ap.parse_args()

    if args.mode == 'merge':
        from pypdf import PdfWriter, PdfReader
        chunk_pdfs = sorted(glob.glob(os.path.join(args.data_dir, f'{args.out}_chunk*.pdf')))
        if not chunk_pdfs:
            print("No chunk PDFs found to merge.", file=sys.stderr)
            sys.exit(1)
        writer = PdfWriter()
        total = 0
        for fn in chunk_pdfs:
            r = PdfReader(fn)
            total += len(r.pages)
            for p in r.pages:
                writer.add_page(p)
        out_path = os.path.join(args.data_dir, f'{args.out}.pdf')
        with open(out_path, 'wb') as f:
            writer.write(f)
        print(f"Merged {len(chunk_pdfs)} chunks, {total} total pages -> {out_path}", file=sys.stderr)
        return

    full_html, n_prep, n_peer = build_html(args)
    print(f"Built HTML: {len(full_html)} chars, {n_prep} preprints, {n_peer} peer-reviewed papers", file=sys.stderr)

    if args.mode == 'html':
        out_path = os.path.join(args.data_dir, f'{args.out}.html')
        with open(out_path, 'w', encoding='utf-8') as f:
            f.write(full_html)
        print(f"Wrote {out_path}. Render it directly with weasyprint if it's short, "
              f"or re-run with --mode split for a long document.", file=sys.stderr)
    elif args.mode == 'split':
        docs = split_html(full_html, n_chunks=args.n_chunks)
        for i, doc in enumerate(docs):
            path = os.path.join(args.data_dir, f'{args.out}_chunk{i}.html')
            with open(path, 'w', encoding='utf-8') as f:
                f.write(doc)
            print(f"Wrote {path} ({len(doc)} chars)", file=sys.stderr)
        print(f"\nNow render each chunk in its own shell call, e.g.:\n"
              f"  python3 -c \"from weasyprint import HTML; HTML('{args.out}_chunk0.html').write_pdf('{args.out}_chunk0.pdf')\"\n"
              f"...then run this script again with --mode merge.", file=sys.stderr)

if __name__ == '__main__':
    main()
