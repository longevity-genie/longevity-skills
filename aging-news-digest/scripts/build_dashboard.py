#!/usr/bin/env python3
"""
Build the self-contained interactive HTML dashboard for the aging-news-digest skill.

See schema.md in this same folder for the exact shape of each input file.

Usage:
    python3 build_dashboard.py --data-dir . --period "11 June 2026 - 16 July 2026" \\
        --horizon "16 July 2026 - 31 December 2026" --compiled 2026-07-16 \\
        --out aging-news-dashboard.html

After writing the output, this script self-checks that <script>/</script> tags are balanced and
that the extracted JS parses (via `node --check` if node is available) — a research abstract
containing a literal quote or an unescaped backtick can otherwise silently break the page.
"""
import json, os, argparse, subprocess, shutil, sys

def load(data_dir, name):
    with open(os.path.join(data_dir, name), encoding='utf-8') as f:
        return json.load(f)

HTML_TEMPLATE = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<title>HEALES Scientific News — Aging Research Digest</title>
<style>
:root{
  --orange:#E67E22; --darkorange:#7a3b0e; --midorange:#c0521c;
  --cream:#fbf3e9; --creamdark:#f0d3ab; --text:#2b2018; --muted:#8a6a4a;
  --green:#1a7a3c; --greenbg:#e6f4e2; --red:#c0271c; --redbg:#fde3e0; --amber:#d98a1c; --amberbg:#fdecd0;
}
*{box-sizing:border-box;}
body{font-family:-apple-system,"Segoe UI",Roboto,"Helvetica Neue",Arial,sans-serif;background:#fffdf9;color:var(--text);margin:0;line-height:1.6;font-size:16px;}
header{background:linear-gradient(135deg,var(--orange),var(--midorange) 60%,var(--darkorange));color:white;padding:28px 32px;}
header h1{margin:0 0 6px 0;font-size:28px;}
header .meta{font-size:14px;opacity:0.95;}
nav{display:flex;flex-wrap:wrap;gap:4px;background:var(--darkorange);padding:0 16px;position:sticky;top:0;z-index:10;}
nav button{background:none;border:none;color:#f5e2ce;padding:14px 18px;font-size:15px;cursor:pointer;border-bottom:3px solid transparent;font-weight:600;}
nav button.active{color:white;border-bottom:3px solid var(--orange);background:rgba(255,255,255,0.08);}
nav button:hover{background:rgba(255,255,255,0.12);}
.tabpanel{display:none;padding:24px 32px 60px 32px;max-width:1200px;margin:0 auto;}
.tabpanel.active{display:block;}
.overview{background:var(--cream);border-left:5px solid var(--orange);padding:14px 18px;border-radius:6px;margin-bottom:20px;font-size:15px;color:#4a3826;}
.searchbox{width:100%;max-width:420px;padding:10px 14px;font-size:15px;border:2px solid var(--creamdark);border-radius:8px;margin-bottom:18px;}
.searchbox:focus{outline:none;border-color:var(--orange);}
.cluster{margin-bottom:28px;}
.cluster h3{color:var(--darkorange);border-bottom:2px solid var(--creamdark);padding-bottom:6px;font-size:19px;}
.cluster-intro{font-size:14px;color:#5a4632;margin-bottom:14px;}
.card{background:white;border:1px solid #eee0cc;border-radius:8px;padding:16px 18px;margin-bottom:12px;box-shadow:0 1px 3px rgba(0,0,0,0.04);}
.card h4{margin:0 0 4px 0;font-size:16px;color:#2b2018;}
.card .meta{font-size:12.5px;color:var(--muted);margin-bottom:8px;}
.card .abstract{font-size:14px;text-align:justify;}
.card .abstract p{margin:0 0 8px 0;}
.tag{display:inline-block;font-size:10.5px;font-weight:700;letter-spacing:0.5px;padding:2px 8px;border-radius:10px;margin-left:6px;vertical-align:middle;}
.tag-original{background:#dff0d8;color:var(--green);}
.tag-review{background:#f0e2c8;color:#8a5a1c;}
.tag-preprint{background:var(--midorange);color:white;}
.badge{display:inline-block;font-size:11px;font-weight:700;padding:2px 9px;border-radius:10px;margin-left:6px;}
.badge-upcoming{background:var(--greenbg);color:var(--green);}
.badge-occurred{background:#e0e0e0;color:#555;}
.badge-urgent{background:var(--red);color:white;}
.badge-soon{background:var(--amber);color:white;}
.badge-open{background:var(--green);color:white;}
.link{font-size:13px;}
a{color:var(--midorange);}
.why{background:var(--cream);border-radius:6px;padding:10px 14px;margin-top:10px;font-size:13.5px;}
.why b{color:var(--darkorange);}
.featured-card{border:2px solid var(--orange);background:linear-gradient(180deg,#fffaf3,white);}
.featured-badge{display:inline-block;background:var(--orange);color:white;font-size:11px;font-weight:700;padding:3px 10px;border-radius:10px;margin-bottom:8px;}
table{width:100%;border-collapse:collapse;font-size:13.5px;margin-bottom:24px;}
table th{background:var(--darkorange);color:white;padding:8px 8px;text-align:left;}
table td{padding:8px 8px;border-bottom:1px solid #eee0cc;vertical-align:top;}
tr.urgent td{background:var(--redbg);}
tr.soon td{background:var(--amberbg);}
tr.open td{background:var(--greenbg);}
.hidden{display:none !important;}
.count-note{font-size:13px;color:var(--muted);margin-bottom:10px;}
footer{text-align:center;color:var(--muted);font-size:12px;padding:24px;}
</style>
</head>
<body>
<header>
  <h1>HEALES Scientific News — Aging Research Digest</h1>
  <div class="meta">News period: __PERIOD__ &nbsp;|&nbsp; Conference &amp; opportunity horizon: __HORIZON__ &nbsp;|&nbsp; Compiled __COMPILED__</div>
</header>
<nav id="tabnav"></nav>
<div id="panels"></div>
<footer>Abstracts reproduced verbatim as bibliographic excerpts with full attribution and links. In the style of HEALES' monthly editions authored by Sven Bulterijs.</footer>

<script>
const DATA = __DATA_JSON__;
const URGENT_KEYWORDS = __URGENT_KEYWORDS_JSON__;

function esc(s){ if(!s) return ''; const d=document.createElement('div'); d.innerText=s; return d.innerHTML; }
function mdInline(s){
  if(!s) return '';
  let out = esc(s);
  out = out.replace(/\\*\\*(.+?)\\*\\*/g, '<strong>$1</strong>');
  out = out.replace(/\\[(.+?)\\]\\((https?:\\/\\/[^\\s)]+)\\)/g, '<a href="$2" target="_blank">$1</a>');
  out = out.replace(/(^|[^"'>])(https?:\\/\\/[^\\s<]+)/g, '$1<a href="$2" target="_blank">$2</a>');
  return out;
}
function para(text){
  if(!text) return '';
  const parts = text.split(/\\n\\n+/).filter(p=>p.trim());
  return parts.map(p=>'<p>'+mdInline(p)+'</p>').join('');
}

const TABS = [
  {id:'featured', label:'Featured'},
  {id:'business', label:'Business & Industry'},
  {id:'conferences', label:'Conferences & Community'},
  {id:'models', label:'Foundation Models & AI'},
  {id:'preprints', label:'Research — Preprints'},
  {id:'peerreviewed', label:'Research — Peer-Reviewed'},
  {id:'opportunities', label:'Open Opportunities'},
];

function renderNav(){
  const nav = document.getElementById('tabnav');
  nav.innerHTML = TABS.map((t,i)=>`<button data-tab="${t.id}" class="${i===0?'active':''}" onclick="showTab('${t.id}')">${t.label}</button>`).join('');
}
function showTab(id){
  document.querySelectorAll('#tabnav button').forEach(b=>b.classList.toggle('active', b.dataset.tab===id));
  document.querySelectorAll('.tabpanel').forEach(p=>p.classList.toggle('active', p.id==='panel-'+id));
}

function filterCards(inputEl, containerSelector){
  const q = inputEl.value.toLowerCase();
  document.querySelectorAll(containerSelector + ' [data-search]').forEach(el=>{
    const match = el.dataset.search.toLowerCase().includes(q);
    el.classList.toggle('hidden', !match);
  });
  document.querySelectorAll(containerSelector + ' .cluster').forEach(cl=>{
    const anyVisible = cl.querySelectorAll('[data-search]:not(.hidden)').length > 0;
    cl.classList.toggle('hidden', q.length>0 && !anyVisible);
  });
}

function renderFeatured(){
  let out = '<div class="overview">A hand-selected set of the most promising original-research findings and AI/biomarker tools from Sections 2 and 3, chosen for strong or validated interventions, mechanistic breakthroughs with translational plausibility, and tools worth tracking. Each was read in full text where available and synthesized here in an original summary, not the verbatim abstract.</div>';
  (DATA.featured || []).forEach(f=>{
    out += `<div class="card featured-card" data-search="${esc((f.title+' '+f.summary).toLowerCase())}">
      <div class="featured-badge">FEATURED PICK</div>
      <h4>${esc(f.title)}</h4>
      <div class="meta">${esc(f.venue)} &middot; <a href="${esc(f.link)}" target="_blank">${esc(f.link)}</a> &middot; ${f.fulltext_used?'full text read':'abstract-based'}</div>
      <div class="abstract">${para(f.summary)}</div>
    </div>`;
  });
  return out;
}

function renderBusiness(){
  const b = DATA.sec1;
  let out = '<div class="overview">Funding rounds, clinical-trial milestones, company news, and policy developments in aging/longevity biotech from the news period.</div>';
  out += '<input class="searchbox" placeholder="Search business news..." oninput="filterCards(this, \\'#panel-business\\')">';
  (b.business || []).forEach(item=>{
    out += `<div class="card" data-search="${esc((item.title+' '+item.desc).toLowerCase())}">
      <h4>${esc(item.title)} <span class="meta">(${esc(item.date)})</span></h4>
      <div class="abstract">${para(item.desc)}</div>
      <div class="link">${mdInline(item.sources_md||'')}</div>
    </div>`;
  });
  if(b.business_context){
    out += `<div class="card"><b>Industry-wide context:</b> ${mdInline(b.business_context)}</div>`;
  }
  return out;
}

function renderConfCard(item, occurred){
  const badge = occurred ? '<span class="badge badge-occurred">ALREADY OCCURRED</span>' : '<span class="badge badge-upcoming">UPCOMING</span>';
  return `<div class="card" data-search="${esc((item.title+' '+(item.event_dates||'')).toLowerCase())}">
    <h4>${esc(item.title)} ${badge}</h4>
    <div class="meta">
      <b>Event date(s):</b> ${mdInline(item.event_dates||'')}<br>
      <b>Abstract/CFP deadline:</b> ${mdInline(item.cfp_deadline||'not found')}<br>
      <b>Registration deadline:</b> ${mdInline(item.registration_deadline||'not found')}<br>
      <b>Status:</b> ${mdInline(item.status||'')}
    </div>
  </div>`;
}

function renderConferences(){
  const b = DATA.sec1;
  let out = '<div class="overview">Every conference is dated against today and labeled already-occurred or upcoming — no past event is presented as open to attend.</div>';
  out += '<input class="searchbox" placeholder="Search conferences..." oninput="filterCards(this, \\'#panel-conferences\\')">';
  out += '<h3>Already occurred (recap)</h3>';
  (b.conf_recap || []).forEach(i=> out += renderConfCard(i, true));
  out += '<h3>Upcoming</h3>';
  (b.conf_upcoming || []).forEach(i=> out += renderConfCard(i, false));
  return out;
}

function renderFMEntry(e){
  const isPreprint = /preprint/i.test(e.heading) || /preprint/i.test(e.note_on_dating||'');
  return `<div class="card" data-search="${esc((e.heading+' '+e.what_it_is).toLowerCase())}">
    ${isPreprint?'<span class="tag tag-preprint">PREPRINT</span>':''}
    <h4>${esc(e.heading)}</h4>
    ${e.note_on_dating?`<div class="meta"><i>Note on dating:</i> ${mdInline(e.note_on_dating)}</div>`:''}
    <div class="abstract">
      <p><b>What it is, in plain language:</b> ${mdInline(e.what_it_is)}</p>
      <p><b>Task / scale:</b> ${mdInline(e.task_scale)}</p>
      <p><b>Link:</b> ${mdInline(e.link)}</p>
      <p><b>Code / model availability:</b> ${mdInline(e.code_availability)}</p>
    </div>
    <div class="why"><b>Why it matters:</b> ${mdInline(e.why_it_matters)}</div>
  </div>`;
}

function renderModels(){
  const s3 = DATA.sec3;
  let out = `<div class="overview">${mdInline(s3.glossary||'')}</div>`;
  out += '<input class="searchbox" placeholder="Search foundation models..." oninput="filterCards(this, \\'#panel-models\\')">';
  out += `<div class="cluster"><h3>3a — Aging-Specific Models</h3><div class="cluster-intro">${mdInline(s3['3a_intro']||'')}</div>`;
  (s3['3a']||[]).forEach(e=> out += renderFMEntry(e));
  out += '</div>';
  out += `<div class="cluster"><h3>3b — General-Purpose Biological Foundation Models</h3><div class="cluster-intro">${mdInline(s3['3b_intro']||'')}</div>`;
  (s3['3b']||[]).forEach(e=> out += renderFMEntry(e));
  out += '</div>';
  return out;
}

function renderPreprintEntry(e){
  const tagcls = /ORIGINAL/i.test(e.type||'') ? 'tag-original' : 'tag-review';
  return `<div class="card" data-search="${esc((e.title+' '+e.abstract).toLowerCase())}">
    <span class="tag tag-preprint">PREPRINT</span>
    <h4>${esc(e.title)} <span class="tag ${tagcls}">${esc(e.type||'')}</span></h4>
    <div class="meta">${esc(e.authors||'')} &middot; ${esc(e.server_date||'')} &middot; ${esc(e.category||'')}</div>
    <div class="abstract">${para(e.abstract)}</div>
    <div class="link">${mdInline(e.doi||'')}</div>
  </div>`;
}

function renderPeerEntry(e){
  const tagcls = /ORIGINAL/i.test(e.tag||'') ? 'tag-original' : 'tag-review';
  return `<div class="card" data-search="${esc((e.title+' '+e.abstract).toLowerCase())}">
    <h4>${esc(e.title)} <span class="tag ${tagcls}">${esc(e.tag||'')}</span></h4>
    <div class="meta">${esc(e.authors||'')} &middot; <i>${esc(e.journal||'')}</i>, ${esc(e.date||'')} &middot; PMID: ${esc(e.pmid||'')}</div>
    <div class="abstract">${para(e.abstract)}</div>
    <div class="link">DOI: <a href="${esc(e.link||'')}" target="_blank">${esc(e.doi||'')}</a></div>
  </div>`;
}

function renderResearchTab(clusters, renderFn, tabId, label, total){
  let out = `<div class="overview">${total} ${label} screened as aging/longevity-relevant for the news window. Grouped by research theme; original experimental work kept separate from reviews/perspectives.</div>`;
  out += `<input class="searchbox" placeholder="Search ${label}..." oninput="filterCards(this, '#panel-${tabId}')">`;
  clusters.forEach(c=>{
    out += `<div class="cluster"><h3>${esc(c.name)} <span class="count-note">(${c.entries.length})</span></h3><div class="cluster-intro">${mdInline(c.intro)}</div>`;
    c.entries.forEach(e=> out += renderFn(e));
    out += '</div>';
  });
  return out;
}

function urgencyClass(deadline){
  const d = (deadline||'').toLowerCase();
  if(URGENT_KEYWORDS.some(k=>d.includes(k))) return ['urgent','badge-urgent','URGENT'];
  if(d.includes('rolling') || d.includes('ongoing') || d.includes('no deadline')) return ['open','badge-open','ROLLING'];
  return ['soon','badge-soon','OPEN'];
}

function renderTable(rows, extraStatusCol){
  if(!rows || !rows.length) return '<p><em>None found.</em></p>';
  const keys = Object.keys(rows[0]);
  let out = '<table><thead><tr>' + keys.map(k=>`<th>${esc(k)}</th>`).join('') + (extraStatusCol?'<th>Status</th>':'') + '</tr></thead><tbody>';
  rows.forEach(r=>{
    let rowcls = '';
    let statusCell = '';
    if(extraStatusCol){
      const [cls, badgecls, label] = urgencyClass(r['Deadline']);
      rowcls = cls;
      statusCell = `<td><span class="badge ${badgecls}">${label}</span></td>`;
    }
    out += `<tr class="${rowcls}">` + keys.map(k=>`<td>${mdInline(r[k])}</td>`).join('') + statusCell + '</tr>';
  });
  out += '</tbody></table>';
  return out;
}

function renderOpportunities(){
  const s4 = DATA.sec4;
  let out = '<div class="overview">Actionable items with concrete deadlines and eligibility, checked against live official pages. Red = urgent, amber = open with a set deadline, green = rolling/open-ended.</div>';
  out += '<h3>Urgent</h3>' + renderTable(s4.urgent, true);
  out += '<h3>Grant / funding calls</h3>' + renderTable(s4.grants, true);
  out += '<h3>Conferences</h3>' + renderTable(s4.conferences, false);
  out += '<h3>Status recap</h3><div class="card" style="white-space:pre-wrap;font-size:13px;">' + mdInline(s4.recap_md||'') + '</div>';
  return out;
}

function renderPanels(){
  const panels = document.getElementById('panels');
  const renderers = {
    featured: renderFeatured,
    business: renderBusiness,
    conferences: renderConferences,
    models: renderModels,
    preprints: ()=>renderResearchTab(DATA.prep, renderPreprintEntry, 'preprints', 'preprints', DATA.meta.n_prep),
    peerreviewed: ()=>renderResearchTab(DATA.peer, renderPeerEntry, 'peerreviewed', 'peer-reviewed papers', DATA.meta.n_peer),
    opportunities: renderOpportunities,
  };
  panels.innerHTML = TABS.map((t,i)=>`<div class="tabpanel ${i===0?'active':''}" id="panel-${t.id}"></div>`).join('');
  TABS.forEach(t=>{ document.getElementById('panel-'+t.id).innerHTML = renderers[t.id](); });
}

renderNav();
renderPanels();
</script>
</body>
</html>
"""

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--data-dir', default='.')
    ap.add_argument('--period', required=True)
    ap.add_argument('--horizon', required=True)
    ap.add_argument('--compiled', required=True)
    ap.add_argument('--out', default='aging-news-dashboard.html')
    ap.add_argument('--urgent-keywords', default='urgent',
                     help='Comma-separated substrings of "Deadline" values that should render as URGENT (red).')
    args = ap.parse_args()

    peer = load(args.data_dir, 'peerreviewed.json')
    prep = load(args.data_dir, 'preprints.json')
    sec1 = load(args.data_dir, 'section1.json')
    sec3 = load(args.data_dir, 'section3.json')
    sec4 = load(args.data_dir, 'section4.json')
    featured = load(args.data_dir, 'featured_picks.json')

    data = {
        'peer': peer, 'prep': prep, 'sec1': sec1, 'sec3': sec3, 'sec4': sec4, 'featured': featured,
        'meta': {
            'period': args.period, 'horizon': args.horizon, 'compiled': args.compiled,
            'n_peer': sum(len(c['entries']) for c in peer),
            'n_prep': sum(len(c['entries']) for c in prep),
        }
    }

    out = HTML_TEMPLATE
    out = out.replace('__DATA_JSON__', json.dumps(data, ensure_ascii=False))
    out = out.replace('__URGENT_KEYWORDS_JSON__', json.dumps([k.strip().lower() for k in args.urgent_keywords.split(',')]))
    out = out.replace('__PERIOD__', args.period)
    out = out.replace('__HORIZON__', args.horizon)
    out = out.replace('__COMPILED__', args.compiled)

    out_path = os.path.join(args.data_dir, args.out)
    with open(out_path, 'w', encoding='utf-8') as f:
        f.write(out)
    print(f"Wrote {out_path} ({len(out)} chars)", file=sys.stderr)

    # Self-check: balanced script tags + valid embedded JSON + (if node available) valid JS.
    n_open = out.count('<script>')
    n_close = out.count('</script>')
    if n_open != n_close:
        print(f"WARNING: <script> tags unbalanced ({n_open} open vs {n_close} close) — "
              f"a research abstract may contain a literal '</script>'-like string.", file=sys.stderr)
    else:
        print(f"OK: <script>/</script> balanced ({n_open} pairs)", file=sys.stderr)

    if shutil.which('node'):
        start = out.find('<script>') + len('<script>')
        end = out.find('</script>')
        js_path = out_path + '.jscheck.js'
        with open(js_path, 'w', encoding='utf-8') as f:
            f.write(out[start:end])
        result = subprocess.run(['node', '--check', js_path], capture_output=True, text=True)
        if result.returncode == 0:
            print("OK: extracted JS passes `node --check`", file=sys.stderr)
        else:
            print(f"WARNING: `node --check` failed:\n{result.stderr}", file=sys.stderr)
        os.remove(js_path)
    else:
        print("node not available — skipped JS syntax self-check.", file=sys.stderr)

if __name__ == '__main__':
    main()
