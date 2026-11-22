#!/usr/bin/env python3
"""Static site builder for GTA Tax Training. One registry per tax (content/<tax>/site.json) drives
nav, breadcrumbs, prev/next and the sidebar. Fragments use macros:
  {{cite:KEY}}  -> link to the official source (KEY must exist in content/sources.json)
  {{svg:NAME}}  -> inline content/<tax>/figures/NAME.svg
  {{quiz}}      -> self-check built from content/<tax>/quizzes.json[slug]
  {{modules}}   -> module cards (hub pages)
Build fails on unknown cite keys, missing quizzes on module pages, or skipped heading levels."""
import json, re, os, sys, html, datetime
from html.parser import HTMLParser
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, 'docs')  # GitHub Pages serves /docs
SOURCES = json.load(open(f'{ROOT}/content/sources.json'))
ERR = []
# Per-tax chrome. SUT values reproduce the original output exactly; other taxes add their own nav/official links.
TAXES = {
    'sut': {'nav': 'Sales &amp; Use Tax', 'page': 'https://floridarevenue.com/taxes/taxesfees/Pages/sales_tax.aspx', 'page_label': 'Official Sales and Use Tax page',
            'official': [('Sales and Use Tax (DOR)', 'https://floridarevenue.com/taxes/taxesfees/Pages/sales_tax.aspx'),
                         ('Forms and Publications', 'https://floridarevenue.com/Pages/forms_index.aspx'),
                         ('Tax Information Publications', 'https://floridarevenue.com/taxes/tips/Pages/default.aspx'),
                         ('Taxpayer Education', 'https://floridarevenue.com/taxes/Pages/education.aspx')]},
    'cst': {'nav': 'Communications Services Tax', 'page': 'https://floridarevenue.com/taxes/taxesfees/Pages/cst.aspx', 'page_label': 'Official Communications Services Tax page',
            'official': [('Communications Services Tax (DOR)', 'https://floridarevenue.com/taxes/taxesfees/Pages/cst.aspx'),
                         ('CST rate table', 'https://pointmatch.floridarevenue.com/General/CommunicationsServicesTaxRates.aspx'),
                         ('Address/Jurisdiction Database', 'https://pointmatch.floridarevenue.com/Default.aspx'),
                         ('Forms and Publications', 'https://floridarevenue.com/Pages/forms_index.aspx'),
                         ('Tax Information Publications', 'https://floridarevenue.com/taxes/tips/Pages/default.aspx')]},
}
SHARED_SOURCES = SOURCES
def tax_sources(tax):  # optional per-tax citation registry (content/<tax>/sources.json), layered over shared keys for that tax only
    p = f'{ROOT}/content/{tax}/sources.json'
    return {**SHARED_SOURCES, **json.load(open(p))} if os.path.exists(p) else SHARED_SOURCES
BUILD_DATE = datetime.date.today().isoformat()
esc = html.escape

def cite(key, used):
    s = SOURCES.get(key)
    if not s: ERR.append(f'unknown cite key {key}'); return f'[?{key}]'
    if key not in used: used.append(key)
    return f'<a class="cite" href="{esc(s["url"])}">[{esc(s["short"])}]</a>'

def render_quiz(slug, qs):
    out = [f'<section class="quiz" aria-labelledby="quiz-{slug}-h" data-quiz>',
           f'<h2 id="quiz-{slug}-h">Self-check</h2>',
           '<p>Choose an answer for each question, then select <strong>Check answer</strong>. Nothing is recorded or sent anywhere.</p>']
    for i, q in enumerate(qs, 1):
        qid = f'{slug}-q{i}'
        out.append(f'<fieldset data-question id="{qid}"><legend>{i}. {q["q"]}</legend>')
        for j, opt in enumerate(q['options']):
            corr = ' data-correct' if j == q['answer'] else ''
            out.append(f'<label><input type="radio" name="{qid}" value="{j}"{corr}> <span>{opt}</span></label>')
        out.append(f'<button type="button" class="btn" data-check>Check answer</button>')
        out.append(f'<div class="feedback" role="status" aria-live="polite" data-feedback></div>')
        out.append(f'<details class="answer-key"><summary>Show the answer</summary><p><strong>Answer:</strong> {q["options"][q["answer"]]}. {q["why"]}</p></details>')
        out.append('<template data-why>' + q['why'] + '</template></fieldset>')
    out.append('<p class="score" role="status" aria-live="polite" data-score></p></section>')
    return '\n'.join(out)

class HeadingCheck(HTMLParser):
    def __init__(s): super().__init__(); s.levels = []; s.ids = []
    def handle_starttag(s, tag, attrs):
        if re.fullmatch(r'h[1-6]', tag): s.levels.append(int(tag[1]))
        for k, v in attrs:
            if k == 'id': s.ids.append(v)

def check_headings(name, doc):
    p = HeadingCheck(); p.feed(doc)
    prev = 0
    for lv in p.levels:
        if lv > prev + 1: ERR.append(f'{name}: heading jumps h{prev}->h{lv}')
        prev = lv
    if p.levels.count(1) != 1: ERR.append(f'{name}: expected exactly one h1')
    dup = {i for i in p.ids if p.ids.count(i) > 1}
    if dup: ERR.append(f'{name}: duplicate ids {sorted(dup)}')

def page_shell(*, title, desc, depth, crumbs, nav_current, sidebar, body, pager, tax_title=None, tax='sut'):
    up = '../' * depth
    # Every page lists every guide, then the current guide's tools. Home uses the SUT tools, as before.
    navitems = [('Home', f'{up}index.html', 'home')] + [(TAXES[t]['nav'], f'{up}{t}/index.html', t) for t in TAXES] + \
               [(label, f'{up}{tax}/{slug}.html', slug) for label, slug in (('Learning path', 'learning-path'), ('Glossary', 'glossary'),
                ('Forms', 'forms'), ('Quick reference', 'quick-reference'), ('Sources', 'sources'))]
    nav = ''.join(f'<li><a href="{h}"' + (' aria-current="page"' if k == nav_current else (' class="section-current"' if k == tax and nav_current == f'{tax}-module' else '')) + f'>{t}</a></li>' for t, h, k in navitems)
    bc = ''
    if crumbs:
        items = ''.join(f'<li><a href="{h}"' + (' aria-current="page"' if i == len(crumbs) - 1 else '') + f'>{t}</a></li>' for i, (t, h) in enumerate(crumbs))
        bc = f'<nav class="breadcrumb" aria-label="Breadcrumbs"><ol>{items}</ol></nav>'
    layout_cls = 'layout' if sidebar else 'layout nosidebar'
    side = f'<aside class="sidebar" aria-label="Guide contents">{sidebar}</aside>' if sidebar else ''
    return f'''<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{title} | GTA Tax Training (unofficial)</title>
<meta name="description" content="{esc(desc)}">
<link rel="icon" href="{up}assets/favicon.svg" type="image/svg+xml">
<link rel="stylesheet" href="{up}assets/css/site.css">
<script src="{up}assets/js/site.js" defer></script>
</head>
<body>
<a class="skip" href="#main">Skip to main content</a>
<div class="wrap">
<header class="site-head">
  <a class="brand" href="{up}index.html"><span class="kicker">Florida tax training</span><span class="name">GTA Tax Training</span></a>
  <span class="tag">Unofficial training aid</span>
</header>
<nav class="primary" aria-label="Main">{'<ul>' + nav + '</ul>'}</nav>
<div class="disclaimer"><p style="margin:0"><strong>Unofficial training aid. Not legal advice.</strong> This guide summarizes public information from <a href="https://floridarevenue.com/taxes/Pages/default.aspx">floridarevenue.com</a> for learning purposes. Florida Statutes, Department rules, and official Department of Revenue publications control. Always confirm current rates and requirements with the linked official sources.</p></div>
{bc}
<div class="{layout_cls}">
<main id="main" tabindex="-1">
{body}
{pager}
</main>
{side}
</div>
<footer class="site-foot">
  <p>GTA Tax Training is an unofficial study guide built from public floridarevenue.com material. It is not published by, and does not speak for, the Florida Department of Revenue. It contains no taxpayer or confidential data; all businesses in examples are fictional. Built {BUILD_DATE}.</p>
  <p><a href="https://floridarevenue.com/taxes/Pages/default.aspx">Official Florida Department of Revenue tax site</a> · <a href="{TAXES[tax]['page']}">{TAXES[tax]['page_label']}</a> · <a href="{up}{tax}/sources.html">How this guide was researched</a></p>
</footer>
</div>
</body>
</html>
'''

def build_tax(tax):
    global SOURCES
    SOURCES = tax_sources(tax)
    reg = json.load(open(f'{ROOT}/content/{tax}/site.json'))
    quizzes = json.load(open(f'{ROOT}/content/{tax}/quizzes.json'))
    pages = reg['pages']; modules = [p for p in pages if p.get('module')]
    os.makedirs(f'{OUT}/{tax}', exist_ok=True)
    def sidebar(cur):
        mods = ''.join(f'<li><a href="{p["slug"]}.html"' + (' aria-current="page"' if p['slug'] == cur else '') + f'>{esc(p["title"])}</a></li>' for p in modules)
        tools = ''.join(f'<li><a href="{p["slug"]}.html"' + (' aria-current="page"' if p['slug'] == cur else '') + f'>{esc(p["title"])}</a></li>' for p in pages if p.get('tool'))
        return (f'<div class="panel"><h2>Modules</h2><ol>{mods}</ol></div>'
                f'<div class="panel teal"><h2>Reference</h2><ul>{tools}</ul></div>'
                '<div class="panel"><h2>Official links</h2><ul>' + ''.join(f'<li><a href="{u}">{t}</a></li>' for t, u in TAXES[tax]['official']) + '</ul></div>')
    order = [p for p in pages if p['slug'] != 'index']
    for p in pages:
        slug = p['slug']; used = []
        src = open(f'{ROOT}/content/{tax}/{slug}.html').read()
        def macro(m):
            kind, arg = m.group(1), m.group(2)
            if kind == 'cite': return ' '.join(cite(k.strip(), used) for k in arg.split(','))
            if kind == 'svg': return open(f'{ROOT}/content/{tax}/figures/{arg}.svg').read()
            if kind == 'quiz':
                if slug not in quizzes: ERR.append(f'{slug}: no quiz'); return ''
                return render_quiz(slug, quizzes[slug])
            if kind == 'modules':
                cards = ''.join(f'<li class="card"><h3><a href="{q["slug"]}.html">Module {q["module"]}: {esc(q["title"])}</a></h3><p>{esc(q["summary"])}</p><p class="meta"><span class="level">{q["level"]}</span> · about {q["minutes"]} minutes</p></li>' for q in modules)
                return f'<ul class="cards">{cards}</ul>'
            ERR.append(f'{slug}: unknown macro {kind}'); return ''
        body = re.sub(r'\{\{(cite|svg|quiz|modules):?([^}]*)\}\}', macro, src)
        if p.get('module') and slug not in quizzes: ERR.append(f'{slug}: module without quiz')
        if p.get('module') and len(used) < 3: ERR.append(f'{slug}: only {len(used)} sources cited')
        if used:
            items = ''.join(f'<li><a href="{esc(SOURCES[k]["url"])}">{esc(SOURCES[k]["title"])}</a>' + (f' ({esc(SOURCES[k]["date"])})' if SOURCES[k].get('date') else '') + '</li>' for k in used)
            body += f'\n<section aria-labelledby="sources-h"><h2 id="sources-h">Sources for this page</h2><p class="meta">Official Florida Department of Revenue pages and documents cited above, with the revision date shown on the document where it has one. Retrieved November 2026.</p><ol class="sources">{items}</ol></section>'
        head = f'<h1>{("Module " + str(p["module"]) + ": ") if p.get("module") else ""}{esc(p["title"])}</h1>'
        if p.get('module'):
            head += f'<p class="meta"><span class="level">Level: {p["level"]}</span> · About {p["minutes"]} minutes · {("Module " + str(p["module"]) + " of " + str(sum(1 for q in modules if isinstance(q["module"], int)))) if isinstance(p["module"], int) else ("Companion to Module " + str(p["module"]).rstrip("ABCDEFGH"))}</p>'
        body = head + '\n' + body
        crumbs = [('Home', '../index.html'), (reg['short'], 'index.html')] + ([(p['title'], f'{slug}.html')] if slug != 'index' else [])
        pager = ''
        if slug != 'index':
            i = order.index(p)
            prev = order[i - 1] if i > 0 else {'slug': 'index', 'title': reg['short'] + ' home'}
            nxt = order[i + 1] if i + 1 < len(order) else None
            pager = '<nav class="pager" aria-label="Previous and next pages">' + f'<a class="prev" href="{prev["slug"]}.html"><span>Previous</span><strong>{esc(prev["title"])}</strong></a>' + (f'<a class="next" href="{nxt["slug"]}.html"><span>Next</span><strong>{esc(nxt["title"])}</strong></a>' if nxt else '') + '</nav>'
        else:
            pager = f'<nav class="pager" aria-label="Start"><a class="next" href="{order[0]["slug"]}.html"><span>Start here</span><strong>{esc(order[0]["title"])}</strong></a></nav>'
        cur = {'index': tax}.get(slug, slug if slug in ('learning-path', 'glossary', 'forms', 'quick-reference', 'sources') else f'{tax}-module')
        doc = page_shell(title=esc(p['title']) + ('' if slug == 'index' else ' — ' + reg['short']), desc=p.get('summary', reg['title']), depth=1,
                         crumbs=crumbs, nav_current=cur, sidebar=sidebar(slug), body=body, pager=pager, tax=tax)
        check_headings(f'{tax}/{slug}', doc)
        open(f'{OUT}/{tax}/{slug}.html', 'w').write(doc)

def build_home():
    body = open(f'{ROOT}/content/home.html').read()
    doc = page_shell(title='Home', desc='Unofficial, source-cited training guides for Florida taxes administered by General Tax Administration.', depth=0,
                     crumbs=None, nav_current='home', sidebar=None, body=body, pager='')
    check_headings('index', doc)
    open(f'{OUT}/index.html', 'w').write(doc)

if __name__ == '__main__':
    build_home(); build_tax('sut')
    if os.path.exists(f'{ROOT}/content/cst/site.json'): build_tax('cst')
    open(f'{OUT}/.nojekyll', 'w').write('')
    if ERR:
        print('BUILD ERRORS:'); [print(' -', e) for e in ERR]; sys.exit(1)
    print('build ok')
