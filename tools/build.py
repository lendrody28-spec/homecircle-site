#!/usr/bin/env python3
"""Builds the static HomeCircle website from tools/app-content.json (pulled from the
iOS app source by extract_app_content.py) and events.json. Run from the repo root:
  python3 tools/build.py
"""
import json, html, re, datetime, pathlib

ROOT = pathlib.Path(__file__).resolve().parent.parent
C = json.loads((ROOT / "tools" / "app-content.json").read_text())
EVENTS = json.loads((ROOT / "events.json").read_text())
L = C["legal"]
E = html.escape
ITEMS = {i["id"]: i for i in C["items"]}
ARTS, DRAW, HERO, BG = C["arts"], C["drawing"], C["hero"], C["backgrounds"]
STATS = {s["id"]: s for s in C["stats"]}
TODAY = datetime.date.today().isoformat()

# Words that only make sense inside the iPhone app, changed for the web. Listed in the report.
WEB_EDITS = {
    "When it eases, jot what helped. That note stays on this phone.": "When it eases, jot down what helped.",
    "Angry: is something unnamed? You can tell a sponsor or write it here, on this phone.": "Angry: is something unnamed? You can tell a sponsor or write it down.",
    "This practice is off until you turn it on in Profile. If focusing inward brings up distress, stop.": "This practice stays hidden until you choose to show it. If focusing inward brings up distress, stop.",
    "The out-breath is the long part. The hold is optional in spirit: skip this practice if holds are off in Health safety.": "The out-breath is the long part. Skip this practice if breath holds aren't right for you (see the safety note above).",
    "Use it when the other counts are hidden by your health notes, or whenever you prefer it.": "Use it if breath holds aren't right for you, or whenever you prefer it.",
    "Kai leads a short sit with the wave of an urge.": "A short guided sit with the wave of an urge.",
    "Use the official site, or find a meeting in the app.": "Use the official site, or find a meeting with the HomeCircle meeting finder.",
}
def web(t):
    t = WEB_EDITS.get(t, t)
    return t[5:] if t.startswith("Kai: ") else t

PAGES = [("index.html", "Home"), ("library.html", "Library"), ("twelve-steps.html", "12 Steps"),
         ("meditations.html", "Meditations & breathing"), ("meetings.html", "Meetings"),
         ("help.html", "Help"), ("support.html", "Support")]
PRIVACY = L["privacyURL"]
SLUG = {
    "breath-box": "box-breathing", "breath-478": "4-7-8-breathing", "breath-46": "slow-out-breath",
    "guide-urge": "urge-surfing", "guide-halt": "halt", "guide-24h": "24-hour-plan", "guide-54321": "grounding-5-4-3-2-1",
    "guide-one": "one-thing-focus", "guide-stress": "stress-and-anxiety", "body-alcohol": "alcohol-and-the-body",
    "body-stimulants": "stimulants-and-the-body", "body-opioids": "opioids-and-the-body", "body-cannabis": "cannabis-and-the-body",
    "med-urge": "urge-surfing-meditation", "med-scan": "body-scan", "med-breath": "breathing-anchor", "med-walk": "mindful-walking",
    "med-eat": "mindful-eating", "fell-aa": "alcoholics-anonymous", "fell-na": "narcotics-anonymous", "fell-ga": "gambling-support",
    "fell-pa": "pornography-addiction-support",
}
def item_href(i, r=""):
    return f"{r}library/{SLUG[i]}.html"
STAGES_HREF, BOOKS_HREF = "library/body-and-recovery-stages.html", "library/recovery-books.html"

HELP_PANEL = [
    ("000", "Call 000", "Emergency. If a life is in danger.", "first"),
    ("131114", "Call Lifeline 13 11 14", "24 hours, crisis support.", "second"),
    ("1800858858", "Call Gambling Helpline 1800 858 858", "Gambling Help Online and its helpline. Not run by Gamblers Anonymous.", ""),
    ("1800250015", "Call 1800 250 015", "National Alcohol and Other Drug Hotline. Connects you to your state's service. Hours vary by state.", ""),
]

def head(title, desc, r):
    return f"""<!DOCTYPE html>
<html lang="en-AU" class="no-js">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<meta http-equiv="Content-Security-Policy" content="default-src 'self'; script-src 'self'; style-src 'self'; img-src 'self'; connect-src 'self' https://lendrody28-spec.github.io; base-uri 'self'; form-action 'self'; object-src 'none'">
<meta name="referrer" content="no-referrer">
<title>{E(title)}</title>
<meta name="description" content="{E(desc)}">
<link rel="icon" href="{r}favicon.png" type="image/png">
<link rel="apple-touch-icon" href="{r}assets/logo-192.png">
<link rel="stylesheet" href="{r}assets/site.css">
<script src="{r}assets/site.js" defer></script>
</head>
<body>
<a class="skip" href="#main">Skip to content</a>"""

def header(active, r):
    lis = "".join(f'<li><a href="{r}{h}"{" aria-current=\"page\"" if h == active else ""}>{E(t)}</a></li>' for h, t in PAGES)
    return f"""
<header class="site-head"><div class="wrap">
  <a class="brand" href="{r}index.html"><img src="{r}assets/logo-96.png" alt="" width="46" height="46"><span><b>HomeCircle</b><small>Support for your recovery journey</small></span></a>
  <button class="btn ghost menu-btn" id="menu-btn" type="button" aria-expanded="false" aria-controls="site-nav" hidden>Menu</button>
  <nav class="nav" id="site-nav" aria-label="Main"><ul>{lis}</ul></nav>
</div></header>"""

def footer(r):
    lines = "".join(f'<li><a class="{c}" href="tel:{d}">{E(t)}<small>{E(s)}</small></a></li>' for d, t, s, c in HELP_PANEL)
    return f"""
<footer class="site-foot"><div class="wrap cols">
  <div>
    <h2>HomeCircle</h2>
    <p>Support for your recovery journey. Free, with no accounts, no sign-in, no cookies, no ads, no trackers and no analytics.</p>
    <p>{E(L["gpLine"])} {E(L["notMedicalDevice"])} In an emergency call <a href="tel:000">000</a>.</p>
    <p>{E(L["notAffiliated"])}</p>
    <p>© 2026 LJ Endrody (Luke Endrody, ABN 53 687 374 897). Australian-owned, Brisbane, Queensland.</p>
  </div>
  <div><h2>Explore</h2><ul>{"".join(f'<li><a href="{r}{h}">{E(t)}</a></li>' for h, t in PAGES)}</ul></div>
  <div><h2>About</h2><ul>
    <li><a href="{PRIVACY}">App Privacy Policy</a></li>
    <li>Terms of Use (coming soon)</li>
    <li><a href="{r}support.html#website">About this website</a></li>
    <li><a href="mailto:{L["supportEmail"]}">{L["supportEmail"]}</a> (not a crisis line)</li>
  </ul></div>
</div></footer>
<a class="help-fab" id="help-fab" href="{r}help.html#now" aria-label="Get help now: opens Call 000 and Lifeline 13 11 14" aria-controls="help-dialog">Get help now</a>
<dialog class="help" id="help-dialog" aria-labelledby="help-title">
  <div class="help-in">
    <button class="close-x" type="button" data-close aria-label="Close">×</button>
    <h2 id="help-title">{E(C["crisis"]["sheetTitle"])}</h2>
    <p>{E(C["crisis"]["sheetIntro"])}</p>
    <ul class="help-lines">{lines}</ul>
    <p class="small">These are independent services. HomeCircle is not affiliated with them. <a href="{r}help.html">More helplines on the Help page</a>.</p>
    <button class="btn ghost" type="button" data-close>Close</button>
  </div>
</dialog>
</body>
</html>
"""

def page(path, active, title, desc, body):
    r = "../" * path.count("/")
    out = head(title, desc, r) + header(active, r) + f'\n<main id="main"><div class="wrap">\n{body}\n</div></main>' + footer(r)
    (ROOT / path).parent.mkdir(parents=True, exist_ok=True)
    (ROOT / path).write_text(out)

def art_img(key, r, cls="", eager=False):
    a = ARTS[key]
    return f'<img src="{r}assets/art/{a["asset"]}.jpg" alt="{E(a["label"])}" width="1024" height="768"{"" if eager else " loading=\"lazy\""}{f" class=\"{cls}\"" if cls else ""}>'

def tile(href, title, summary, tag, artkey, r, mins=None):
    pic = art_img(artkey, r) if artkey else f'<div class="icon-tile" aria-hidden="true">{E(title)}</div>'
    m = f" · {mins} min" if mins and mins > 1 else ""
    return f'<a class="card tile" href="{href}">{pic}<div class="tbody"><span class="tag">{E(tag)}{m}</span><h3>{E(title)}</h3><p>{E(summary)}</p></div></a>'

def src_list(links, heading="Sources"):
    lis = "".join(f'<li><a href="{E(l["url"])}" rel="noopener">{E(l["title"])}</a></li>' for l in links)
    return f'<div class="sources"><h3>{heading}</h3><ul>{lis}</ul></div>'

def stat_card(s):
    return f'<div class="stat"><p>{E(s["text"])}</p><a href="{E(s["sourceURL"])}" rel="noopener">Source: {E(s["sourceTitle"])}</a></div>'

def aside(r):
    return f"""<aside><div class="card sage"><h3>Need help now?</h3><p>If you or someone else is in danger, call <a href="tel:000">000</a>. Lifeline is there 24 hours on <a href="tel:131114">13 11 14</a>.</p><p class="small">{E(L["gpLine"])}</p><p><a href="{r}help.html">All helplines</a></p></div></aside>"""

# ---------- events ----------
MONTHS = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
def fmt_date(d):
    y, m, dd = d.split("-"); return f"{int(dd)} {MONTHS[int(m)-1]} {y}"
def events_html(limit=8):
    evs = sorted([e for e in EVENTS["events"] if e.get("end", e["start"]) >= TODAY], key=lambda e: e["start"])
    lis = []
    for k, e in enumerate(evs):
        y, m, d = e["start"].split("-")
        rng = fmt_date(e["start"]) + (f' to {fmt_date(e["end"])}' if e.get("end") and e["end"] != e["start"] else "")
        hid = " hidden data-more" if k >= limit else ""
        lis.append(f'<li class="event" data-end="{e.get("end", e["start"])}"{hid}><div class="date"><b>{int(d)}</b>{MONTHS[int(m)-1]} {y}</div><div><h3><a href="{E(e["source"])}" rel="noopener">{E(e["title"])}</a></h3><p>{E(rng)} · {E(e["place"])}, {E(e["state"])} · {E(e["fellowship"])}</p><p>Listed by {E(e["organiser"])}. Check the official page for times and details.</p></div></li>')
    more = f'<button class="btn ghost" id="events-more" type="button"{"" if len(evs) > limit else " hidden"}>Show all {len(evs)} events</button>'
    return f"""<section aria-labelledby="ev-h">
<h2 id="ev-h">Upcoming events</h2>
<p>Conventions, rallies, round-ups, unity days and service events from the fellowships' own event pages, soonest first. Each one links to its official page.</p>
<p class="note small">HomeCircle is independent and isn't affiliated with or endorsed by Alcoholics Anonymous or Narcotics Anonymous. We only list events posted on their official pages and don't run or check them. Dates and details can change, so always check the official page.</p>
<ul class="events" id="events-list" data-src="events.json" data-limit="{limit}">{"".join(lis)}</ul>
<div class="card sage" id="events-empty"{" hidden" if evs else ""}><h3>No upcoming events listed right now</h3><p>Check the fellowships' own event pages: <a href="https://members.aa.org.au/events/">AA Australia events</a> and <a href="https://www.na.org.au/multi/events/">NA Australia upcoming events</a>.</p></div>
<div class="btn-row">{more}<a class="btn ghost" href="https://members.aa.org.au/events/">All AA Australia events</a><a class="btn ghost" href="https://www.na.org.au/multi/events/">All NA Australia events</a></div>
<p class="small">Event list checked on {fmt_date(EVENTS["updated"])}.</p>
</section>"""

# ---------- home ----------
def build_home():
    r = ""
    feats = [
        ("meetings.html", "Find a meeting", "AA and NA meetings across Australia. Search by suburb, postcode and day.", "Meetings", "groundSee"),
        ("meditations.html", "Breathe now", "An animated breathing guide: box, 4-7-8 or a slow out-breath.", "Breathing", "breatheIn"),
        ("library.html", "Library", "Guides, breathing, meditation, body and fellowships.", "Library", "oneThing"),
        ("twelve-steps.html", "The 12 Steps", C["twelveStepsCopy"]["summary"], "12 Steps", "dayPlan"),
    ]
    tiles = "".join(tile(h, t, s, tg, a, r) for h, t, s, tg, a in feats)
    body = f"""
<section class="hero">
  <div>
    <p class="eyebrow">Free · Australian · No sign-in</p>
    <h1><span class="grad-text">Support for your recovery journey</span></h1>
    <p class="lede">HomeCircle is a free Australian recovery support app, and this website brings its no-account tools to your computer: find AA and NA meetings, breathe along with a guide, and read plain-language guides and the 12 Steps.</p>
    <div class="btn-row"><a class="btn" href="meetings.html">Find a meeting</a><a class="btn ghost" href="meditations.html">Breathe now</a><a class="btn ghost" href="library.html">Open the Library</a></div>
    <p class="small">Everything here is free. No accounts, no cookies, no ads, no trackers and no analytics.</p>
  </div>
  <div class="hero-art"><img src="assets/logo-192.png" alt="HomeCircle logo: three people with arms raised inside a circle" width="260" height="260"><p>You're not alone.</p></div>
</section>
<div class="notice"><strong>Need help right now?</strong> {E(L["notMedicalDevice"])} In an emergency call <a href="tel:000">000</a>. For crisis support call Lifeline on <a href="tel:131114">13 11 14</a>.</div>
<h2>What you can do here</h2>
<div class="grid g4">{tiles}</div>
<div class="grid g3 mt"></div>
{events_html()}
<h2>The HomeCircle app</h2>
<div class="grid g2">
  <div class="card"><h3>In the iPhone app</h3><ul>
    <li><strong>Meetings near you</strong>, with a map.</li>
    <li><strong>A private journal and sober date</strong> that stay on your phone.</li>
    <li><strong>Kai, the Recovery Coach</strong>: built-in templates on your phone for reflection and encouragement. It isn't AI and nothing you type leaves your phone. Kai isn't on the website yet.</li>
    <li><strong>The same Library</strong>, breathing and meditation guides.</li>
  </ul><div class="btn-row"><a class="btn" href="https://apps.apple.com/au/app/homecircle/id6819366068">Get HomeCircle free on the App Store</a></div></div>
  <div class="card sage"><h3>Support, not medical care</h3><p>{E(L["gpLine"])}</p><p>{E(L["notAffiliated"])}</p><p>HomeCircle never reproduces the Big Book or NA literature. We link to the free official pages instead.</p></div>
</div>"""
    body = body.replace('<div class="grid g3 mt"></div>\n', "")
    page("index.html", "index.html", "HomeCircle – Support for your recovery journey",
         "HomeCircle is a free Australian recovery support app and website: find AA and NA meetings, breathing and meditation guides, the 12 Steps and helplines. No accounts.", body)

# ---------- library hub ----------
def build_library():
    r = ""
    sections = [
        ("guide", "Guides", [i for i in C["items"] if i["category"] == "guide"]),
        ("breathing", "Breathing", [i for i in C["items"] if i["category"] == "breathing"]),
        ("meditation", "Meditation", [i for i in C["items"] if i["category"] == "meditation"]),
        ("body", "Body", [i for i in C["items"] if i["category"] == "body"]),
        ("fellowship", "Fellowships", [i for i in C["items"] if i["category"] == "fellowship"]),
    ]
    chips = '<div class="filters" role="group" aria-label="Show category" hidden><button class="chip" type="button" data-filter="all" aria-pressed="true">All</button>' + "".join(f'<button class="chip" type="button" data-filter="{k}" aria-pressed="false">{t}</button>' for k, t, _ in sections) + "</div>"
    out = []
    for k, t, items in sections:
        tiles = []
        if k == "body":
            tiles.append(tile(STAGES_HREF, C["stageCopy"]["title"], C["stageCopy"]["summary"], "Body", "handOnChest", r, 6))
        if k == "fellowship":
            tiles.append(tile("twelve-steps.html", C["twelveStepsCopy"]["title"], C["twelveStepsCopy"]["summary"], "Fellowship", "dayPlan", r))
            tiles.append(tile(BOOKS_HREF, C["booksCopy"]["title"], C["booksCopy"]["summary"], "Fellowship", None, r))
        for i in items:
            tiles.append(tile(item_href(i["id"]), i["title"], web(i["summary"]), i["tag"], HERO.get(i["id"]), r, i["minutes"]))
        out.append(f'<section data-cat="{k}" aria-labelledby="h-{k}"><h2 id="h-{k}">{t}</h2><div class="grid g4">{"".join(tiles)}</div></section>')
    body = f"""<h1>Library</h1>
<p class="lede">Resources and tools to support your growth: guides, breathing, meditation, body and fellowships. The same Library as the HomeCircle app, free to use here.</p>
{chips}
{"".join(out)}
<p class="note small">{E(L["gpLine"])} {E(L["notAffiliated"])}</p>"""
    page("library.html", "library.html", "Library – HomeCircle", "Free recovery guides, breathing, meditation, body and fellowship pages from the HomeCircle app.", body)

# ---------- breathing widget ----------
def breath_widget(ids, r, default):
    opts = "".join(f'<option value="{i}"{" selected" if i == default else ""}>{E(ITEMS[i]["title"])}</option>' for i in ids)
    cues = "".join(f'<div data-cue-for="{i}"><p><strong>{E(ITEMS[i]["title"])}:</strong> {E(ITEMS[i]["summary"])}</p><ul>' + "".join(f'<li><strong>{E(s["title"])}</strong>: {E(s["cue"])}</li>' for s in ITEMS[i]["steps"]) + "</ul></div>" for i in ids)
    choose = f'<div><label for="b-pattern">Pattern</label><select id="b-pattern" data-pattern>{opts}</select></div>' if len(ids) > 1 else ""
    return f"""<div class="breath player" data-breath="{default}">
  <div class="breath-stage" aria-hidden="true"><div class="breath-ring"></div><div class="breath-ball"></div><div class="breath-label dark"><b data-phase>Ready</b><span data-count></span></div></div>
  <div>
    <div class="grid g2">{choose}<div><label for="b-min">Length</label><select id="b-min" data-minutes><option value="1">1 min</option><option value="3" selected>3 min</option><option value="5">5 min</option></select></div></div>
    <div class="btn-row"><button class="btn" type="button" data-start aria-pressed="false">Start</button><span class="status" data-left aria-hidden="true"></span></div>
    <p class="sr-only small" data-live aria-live="polite"></p>
    {cues}
    <p class="small">Stop whenever you want. Press Stop or Esc to end.</p>
  </div>
</div>"""

def safety_notes(i):
    out = []
    if i["kind"] in ("breathing", "meditation"):
        out.append(f'<div class="note"><strong>Before you start.</strong> {E(L["beforeYouStart"])}</div>')
    if i.get("breathHold"):
        out.append(f'<div class="notice"><strong>Breath holds.</strong> {E(L["breathHold"])} The <a href="{item_href("breath-46", "../")}">slow out-breath</a> has no hold.</div>')
    if i.get("traumaSensitive"):
        out.append(f'<div class="note">{E(L["trauma"])}</div>')
    return "".join(out)

def player(i, r):
    lis = []
    for s in i["steps"]:
        a = DRAW.get(s["drawing"])
        img = art_img(a, r) if a else ""
        secs = f' <span class="small">({s["seconds"]} seconds)</span>' if s["seconds"] else ""
        lis.append(f'<li class="pstep" data-seconds="{s["seconds"]}"><div class="grid g2">{img}<div><h3>{E(s["title"])}{secs}</h3><p>{E(web(s["cue"]))}</p></div></div></li>')
    return f"""<section class="player" data-player aria-labelledby="pl-h"><h2 id="pl-h" class="mt0">Step by step</h2>
<div class="pcontrols" hidden><div class="progress" aria-hidden="true"><i></i></div><p class="status" data-pos aria-live="polite"></p></div>
<ol class="steps-list">{"".join(lis)}</ol>
<div class="pcontrols btn-row" hidden><button class="btn ghost" type="button" data-prev>Back</button><button class="btn" type="button" data-play>Start</button><button class="btn ghost" type="button" data-next>Next</button><span class="count" data-pcount aria-hidden="true"></span></div>
</section>"""

def build_item(i):
    path = item_href(i["id"])
    r = "../"
    hero = HERO.get(i["id"])
    parts = [f'<p class="crumbs"><a href="../library.html">Library</a> › {E(i["category"].title() if i["category"] != "guide" else "Guides")}</p>',
             f'<h1>{E(i["title"])}</h1><p class="lede">{E(web(i["summary"]))}</p>']
    main = []
    if hero:
        main.append(f'<figure class="figure">{art_img(hero, r, eager=True)}</figure>')
    main.append(safety_notes(i))
    if i["category"] == "body":
        main.append(f'<div class="notice"><strong>Safety.</strong> {E(C["stageCopy"]["safetyLine"])} {E(C["stageCopy"]["noDosing"])}</div>')
    paras = "".join(f"<p>{E(web(p))}</p>" for p in i["paragraphs"])
    if i["id"] == "med-scan":
        main.append(f'<div class="card sage" id="bodyscan-optin" hidden><h2 class="mt0">Body scan is off until you choose it</h2><p>It walks attention through the body. Skip it if that doesn\'t feel right. Nothing is saved.</p><button class="btn" type="button">Show the body scan</button></div><div id="bodyscan-content"><h2 tabindex="-1">About this practice</h2>{paras}')
    else:
        main.append(f'<div>{paras}</div>')
    if i["kind"] == "breathing":
        main.append(f'<h2>Breathe along</h2>{breath_widget([i["id"]], r, i["id"])}')
    elif i["steps"]:
        main.append(player(i, r))
    if i["id"] == "med-scan":
        main.append("</div>")
    bg = BG.get(i["id"])
    if bg:
        main.append(f'<div class="card"><h2 class="mt0">Where this comes from</h2><p>{E(bg["origin"])}</p><h2>Why it can help</h2><p>{E(bg["why"])}</p>{src_list(bg["sources"])}</div>')
    links = [l for l in i["links"] if not l.get("inAppMeetings")]
    if any(l.get("inAppMeetings") for l in i["links"]):
        main.append('<p><a class="btn" href="../meetings.html">Find a meeting</a></p>')
    if links:
        main.append(src_list(links, "Official pages" if i["category"] == "fellowship" else "Read more"))
    if i.get("phoneDial"):
        main.append(f'<p><a class="btn ghost" href="tel:{i["phoneDial"]}">Call {E(i["phoneDisplay"])}</a></p>')
    if i["id"] == "guide-stress":
        main.append(stat_card(STATS["abs-anxiety"]))
    main.append(f'<p class="small">{E(L["gpLine"])}</p>')
    body = "".join(parts) + f'<div class="layout"><div>{"".join(main)}</div>{aside(r)}</div>'
    page(path, "library.html", f'{i["title"]} – HomeCircle Library', web(i["summary"]), body)

def build_stages():
    r = "../"; S = C["stageCopy"]
    cards = []
    for s in C["stages"]:
        notes = "".join(f"<p>{E(n)}</p>" for n in s["notes"])
        st = stat_card(STATS[s["statID"]]) if s.get("statID") else ""
        tr = ""
        if s.get("practiceID"):
            it = ITEMS[s["practiceID"]]
            tr = f'<p><a href="{item_href(it["id"], r)}">{E(s["tryThis"])} Open {E(it["title"])}.</a></p>'
        cards.append(f'<div class="card"><h3>{E(s["title"])}</h3>{notes}{st}{tr}</div>')
    allstats = "".join(stat_card(s) for s in C["stats"] if s["id"] != "abs-anxiety")
    body = f"""<p class="crumbs"><a href="../library.html">Library</a> › Body</p>
<h1>{E(S["title"])}</h1><p class="lede">{E(S["summary"])}</p>
<div class="layout"><div>
<figure class="figure">{art_img("handOnChest", r, eager=True)}</figure>
<p>{E(S["intro"])}</p>
<div class="notice"><p><strong>{E(S["safetyLine"])}</strong></p><p>{E(S["warningSigns"])}</p><p class="small">{E(S["noDosing"])}</p><a class="btn danger" href="tel:000">Call 000</a></div>
<div class="grid g2">{"".join(cards)}</div>
<div class="card mt"><h2 class="mt0">Checked facts</h2><p>Each number below is shown with its source.</p>{allstats}</div>
<div class="card mt"><h2 class="mt0">Where this comes from</h2><p>These notes are based on Australian health information from the Alcohol and Drug Foundation and Healthdirect. Each number on this page shows its source. HomeCircle is support, not medical care.</p>{src_list([{"title": l["title"], "url": l["url"]} for l in C["stageSources"]])}</div>
<p class="small">{E(L["gpLine"])}</p>
</div>{aside(r)}</div>"""
    page(STAGES_HREF, "library.html", f'{S["title"]} – HomeCircle Library', S["summary"], body)

def build_books():
    r = "../"; B = C["booksCopy"]
    cards = "".join(f'<a class="card tile" href="{E(b["url"])}" rel="noopener"><div class="tbody"><span class="tag">{E(b["opens"])}</span><h3>{E(b["title"])}</h3><p>{E(b["detail"])}</p></div></a>' for b in C["books"])
    body = f"""<p class="crumbs"><a href="../library.html">Library</a> › Fellowships</p>
<h1>{E(B["title"])}</h1><p class="lede">{E(B["note"])}</p>
<div class="grid g3">{cards}</div>
<div class="card mt"><h2 class="mt0">Where this comes from</h2><p>Every link goes to a free page that Alcoholics Anonymous World Services or Narcotics Anonymous World Services hosts on its own site.</p></div>
<p class="small">{E(C["twelveStepsCopy"]["independence"])}</p>"""
    page(BOOKS_HREF, "library.html", "Recovery books (free to read) – HomeCircle", B["summary"], body)

def build_steps():
    r = ""; T = C["twelveStepsCopy"]
    cards = "".join(f'<div class="card"><p class="num">Step {s["number"]}</p><h3>{E(s["theme"])}</h3><p>{E(s["note"])}</p><p class="reflect">{E(s["reflection"])}</p></div>' for s in C["twelveSteps"])
    body = f"""<div class="layout"><div>
<h1>{E(T["title"])}</h1><p class="lede">{E(T["intro"])}</p>
<div class="btn-row"><a class="btn" href="{E(T["officialURL"])}" rel="noopener">{E(T["officialLinkTitle"])}</a><a class="btn ghost" href="{BOOKS_HREF}">Free recovery books</a></div>
<div class="twelve">{cards}</div>
<div class="card mt"><h2 class="mt0">Where this comes from</h2><p>The 12 Steps were first written down by Alcoholics Anonymous in the 1930s. Narcotics Anonymous and other fellowships adapted them. The notes on this page are HomeCircle's own plain-language summaries, not the official text.</p>{src_list([{"title": "The Twelve Steps (opens aa.org)", "url": T["officialURL"]}])}</div>
<p class="small">{E(T["independence"])}</p>
</div><aside><figure class="figure">{art_img("dayPlan", r, eager=True)}</figure><div class="card sage"><h3>Find a meeting</h3><p>Many people work the Steps with a sponsor they meet at meetings.</p><p><a href="meetings.html">Search AA and NA meetings</a></p></div></aside></div>"""
    page("twelve-steps.html", "twelve-steps.html", "The 12 Steps – HomeCircle", T["summary"], body)

def build_meditations():
    r = ""
    br = ["breath-46", "breath-box", "breath-478"]
    meds = [i for i in C["items"] if i["category"] == "meditation"]
    tiles_b = "".join(tile(item_href(i), ITEMS[i]["title"], ITEMS[i]["summary"], "Breathing", HERO.get(i), r, ITEMS[i]["minutes"]) for i in br)
    tiles_m = "".join(tile(item_href(i["id"]), i["title"], web(i["summary"]), "Meditation", HERO.get(i["id"]), r, i["minutes"]) for i in meds)
    body = f"""<h1>Meditations and breathing</h1>
<p class="lede">Breathe along with the circle: it grows as you breathe in and shrinks as you breathe out. Then try a short guided meditation.</p>
<div class="note"><strong>Before you start.</strong> {E(L["beforeYouStart"])}</div>
<div class="notice"><strong>Breath holds.</strong> {E(L["breathHold"])} The slow out-breath has no hold.</div>
<h2>Breathing guide</h2>
{breath_widget(br, r, "breath-46")}
<h2>Breathing practices</h2><div class="grid g3">{tiles_b}</div>
<h2>Meditations</h2><p>Each meditation is a few short steps. Eyes can stay open. Stop if you feel unwell.</p><div class="grid g3">{tiles_m}</div>
<p class="note small">{E(L["trauma"])} {E(L["gpLine"])}</p>"""
    page("meditations.html", "meditations.html", "Meditations and breathing – HomeCircle", "A free animated breathing guide (box, 4-7-8, slow out-breath) and short guided meditations.", body)

def build_meetings():
    days = "".join(f'<option value="{k}">{d}</option>' for k, d in enumerate(["Sunday", "Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"]))
    states = "".join(f'<option value="{s}">{s}</option>' for s in ["QLD", "NSW", "VIC", "WA", "SA", "TAS", "ACT", "NT"])
    body = f"""<h1>Find a meeting</h1>
<p class="lede">AA and NA meetings across Australia, from the same public list the HomeCircle app uses. Search by suburb or postcode, and pick a day.</p>
<form class="card" id="finder" role="search" hidden>
  <div class="form-row">
    <div class="wide"><label for="f-q">Suburb, postcode or meeting name</label><input type="search" id="f-q" name="q" autocomplete="off" placeholder="For example Bethania or 4205"></div>
    <div><label for="f-state">State</label><select id="f-state"><option value="">All of Australia</option>{states}<option value="online">Online meetings</option></select></div>
    <div><label for="f-day">Day</label><select id="f-day"><option value="">Any day</option><option value="today">Today</option>{days}</select></div>
    <div><label for="f-fellowship">Fellowship</label><select id="f-fellowship"><option value="">AA and NA</option><option value="AA">AA</option><option value="NA">NA</option></select></div>
    <div><label for="f-format">Format</label><select id="f-format"><option value="">Any</option><option value="in_person">In person</option><option value="online">Online</option><option value="hybrid">Hybrid</option></select></div>
  </div>
  <div class="btn-row"><button class="btn" type="submit">Search</button><button class="btn ghost" type="button" id="f-near">Near me</button></div>
  <p class="small">Near me asks your browser for your location only when you press it. It's used on this page to sort by distance and is never sent to HomeCircle or anyone else.</p>
</form>
<div class="card" id="finder-nojs"><p>The meeting finder needs JavaScript. You can use the official lists instead.</p></div>
<p class="status" id="f-status" role="status" aria-live="polite"></p>
<div class="results" id="results"></div>
<div class="btn-row"><button class="btn ghost" type="button" id="f-more" hidden>Show more</button></div>
<div class="grid g2 mt">
  <div class="card sage"><h2 class="mt0">About the list</h2><p id="feed-info">AA and NA meetings from public listings.</p><p>Listings come from public sources: AA Australia's Meeting Guide feed and NA Australia's BMLT meeting list. Times can change, so check with the group if you're unsure. Each meeting links to its official listing.</p><p class="small">Times show in the meeting's own time zone.</p></div>
  <div class="card"><h2 class="mt0">Official meeting lists</h2><ul><li><a href="https://meetings.aa.org.au/">AA meetings list (AA Australia)</a></li><li><a href="https://www.na.org.au/multi/">NA Australia meetings</a></li><li><a href="https://www.gamblinghelponline.org.au/">Gambling Help Online</a> and <a href="https://www.gaaustralia.org.au/">Gamblers Anonymous</a></li></ul><p class="small">{E(L["notAffiliated"])} At meetings, please respect each group's own guidelines, and don't record or share what people say.</p></div>
</div>
<p class="note small">{E(L["privateDetails"])}</p>
<script src="assets/meetings.js" defer></script>"""
    page("meetings.html", "meetings.html", "Find an AA or NA meeting – HomeCircle", "Search AA and NA meetings in Australia by suburb, postcode and day. Free, no sign-in.", body)

def build_help():
    from_app = [
        ("Lifeline", "131114", "13 11 14", "24 hours. Call 13 11 14", None),
        ("Beyond Blue", "1300224636", "1300 22 4636", "24 hours. Call 1300 22 4636", None),
        (L["nationalName"], "1800250015", L["nationalNumber"], "Call 1800 250 015", L["nationalNote"]),
        (L["adisName"], "1800177833", L["adisNumber"], "Call 1800 177 833", L["adisNote"]),
        ("Gambling Helpline", "1800858858", "1800 858 858", "Call 1800 858 858", None),
        ("AA Australia", "1300222222", "1300 222 222", "Call 1300 222 222", None),
        ("NA Australia", "1300652820", "1300 652 820", "Call 1300 652 820", None),
    ]
    lines = "".join(f'<div class="card"><h3>{E(n)}</h3><p>{E(d)}</p>{f"<p class=\"small\">{E(note)}</p>" if note else ""}<a class="btn ghost" href="tel:{dial}">Call {E(disp)}</a></div>' for n, dial, disp, d, note in from_app)
    conduct = "Be kind. At meetings you find through HomeCircle, please respect that group's own guidelines, and don't record or share what people say. HomeCircle is support, not medical care."
    body = f"""<div id="now" class="btn-row"><a class="btn danger" href="tel:000">Call 000</a><a class="btn" href="tel:131114">Call Lifeline 13 11 14</a></div>
<h1>Get help</h1>
<p class="lede">We're here to support you. Help is always available. You're not alone.</p>
<p><strong>{E(L["notMedicalDevice"])}</strong></p>
<div class="notice"><strong>Call 000 immediately</strong> if a life is in danger. Call 000 or go to your nearest emergency department.</div>
<h2>Helplines</h2>
<div class="grid g3">{lines}</div>
<p class="small">These are independent services. HomeCircle is not affiliated with them.</p>
<h2>Self-help kit</h2>
<p>Tools to support you in the moment.</p>
<div class="grid g4">{tile(item_href("guide-urge"), "Urge plan", ITEMS["guide-urge"]["summary"], "Guide", "urgeWave", "")}{tile(item_href("guide-halt"), "HALT", ITEMS["guide-halt"]["summary"], "Guide", "haltPause", "")}{tile(item_href("guide-24h"), "24-hour plan", ITEMS["guide-24h"]["summary"], "Guide", "dayPlan", "")}{tile("meditations.html", "Breathe now", "An animated breathing guide.", "Breathing", "breatheOut", "")}</div>
<div class="grid g2 mt">
<div class="card"><h2 class="mt0">Keep your details private</h2><p>{E(L["privateDetails"])}</p></div>
<div class="card"><h2 class="mt0">Code of conduct</h2><p>{E(conduct)}</p></div>
</div>
<h2 id="family">Family &amp; Partners</h2>
<div class="note">This is not medical advice. For any major concern, see a local doctor or GP. If a life is in danger, call 000.</div>
<p>For partners, family members, and couples. These lines are beside someone in recovery.</p>
<div class="grid g2">
<div class="card"><h3>Al-Anon Family Groups Australia</h3><p>For families and friends of someone with a drinking problem.</p><div class="btn-row"><a class="btn ghost" href="tel:1300252666">Call 1300 252 666</a><a class="btn ghost" href="https://al-anon.org.au/">Open site</a></div></div>
<div class="card"><h3>Alateen</h3><p>Part of Al-Anon Australia, for ages about 13 to 18. Same Australian line. HomeCircle itself is an 18+ app.</p><div class="btn-row"><a class="btn ghost" href="tel:1300252666">Call 1300 252 666</a><a class="btn ghost" href="https://al-anon.org.au/">Open site</a></div></div>
</div>
<h2>More information</h2>
<p><a href="https://adf.org.au/">Alcohol and Drug Foundation</a> · <a href="https://www.healthdirect.gov.au/alcohol">Alcohol on Healthdirect</a> · <a href="https://www.gamblinghelponline.org.au/">Gambling Help Online</a></p>
<p class="small">{E(L["gpLine"])}</p>"""
    page("help.html", "help.html", "Get help – HomeCircle", "Helplines for Australia: 000, Lifeline 13 11 14, Beyond Blue, alcohol and drug lines, Gambling Helpline, and family support.", body)

def build_support():
    src = (ROOT / "tools" / "support-app-faq.html").read_text()
    body = f"""<h1>HomeCircle Support</h1>
<p class="lede">Help with the HomeCircle website and app, and how to contact us.</p>
<div class="notice"><strong>In crisis or need help now?</strong> HomeCircle is not an emergency service. Call <a href="tel:000">000</a> in an emergency, or Lifeline on <a href="tel:131114">13 11 14</a>. <a href="help.html">More helplines</a>.</div>
<h2>Contact us</h2>
<div class="card"><p>Email: <a href="mailto:{L["supportEmail"]}">{L["supportEmail"]}</a></p><p>Please include whether you're using the website or the app, your device, and a short description of the issue. We aim to reply within 2 business days. This email is not a crisis line.</p></div>
<h2 id="website">About this website</h2>
<h3>Do I need an account?</h3><p>No. The website has no accounts and no sign-in, and everything on it is free.</p>
<h3>Does the website collect my data?</h3><p>No. There are no cookies, no ads, no trackers, no analytics and no third-party scripts or fonts. The site doesn't save anything about you, and the breathing guide and meditations don't record anything.</p>
<h3>How does the meeting finder work?</h3><p>Your browser downloads the same public meeting list the app uses, from GitHub Pages, and searches it on your computer. What you type isn't sent anywhere. <strong>Near me</strong> only asks for your location when you press it, and your location stays on the page. The site and the list are hosted on GitHub Pages, which, like any web host, receives normal web requests.</p>
<h3>Is Kai on the website?</h3><p>Not yet. Kai, the Recovery Coach, is a feature of the iPhone app.</p>
<h3>Spotted a wrong meeting or event?</h3><p>Meetings and events come from AA and NA's own public listings. Please tell the group or the fellowship, and email us too so we know.</p>
<h2>The iPhone app</h2>
{src}
<h2>Privacy</h2><p>Read the <a href="{PRIVACY}">App Privacy Policy</a> to learn how HomeCircle keeps your information on your phone.</p>"""
    page("support.html", "support.html", "Support – HomeCircle", "Get help with HomeCircle: contact, FAQs about the website and app, and crisis support.", body)

build_home(); build_library(); build_steps(); build_meditations(); build_meetings(); build_help(); build_support()
for i in C["items"]:
    build_item(i)
build_stages(); build_books()
print("built")
