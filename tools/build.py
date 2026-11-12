#!/usr/bin/env python3
"""Builds the static HomeCircle website from tools/app-content.json (pulled from the
iOS app source by extract_app_content.py) and events.json. Run from the repo root:
  python3 tools/build.py
"""
import json, html, re, datetime, pathlib

ROOT = pathlib.Path(__file__).resolve().parent.parent
C = json.loads((ROOT / "tools" / "app-content.json").read_text())
EVENTS = json.loads((ROOT / "events.json").read_text())
UPDATES = json.loads((ROOT / "updates.json").read_text())
L = C["legal"]
E = html.escape
ITEMS = {i["id"]: i for i in C["items"]}
ARTS, DRAW, HERO, BG = C["arts"], C["drawing"], C["hero"], C["backgrounds"]
HERO = dict(HERO, **{"med-walk": "groundFeel"})   # Mindful moving: a seated picture, not only standing bare feet (web only)
STATS = {s["id"]: s for s in C["stats"]}
TODAY = datetime.date.today().isoformat()

# Kai chat on the website. False = no Kai bubble, panel or scripts on any page (safety stopgap,
# 5 Nov 2026, while the build 31 crisis check is ported and Finn signs it off). The Help pill,
# help strips, 000 and Lifeline 13 11 14 buttons and Quick exit are not affected.
# Set to True and rebuild to turn Kai back on.
KAI_ON = True
KAI_INTRO = '<div class="card sage mt kai-intro"><img src="assets/kai.png" alt="" width="72" height="72"><div><h2 class="mt0">Meet Kai, your recovery buddy</h2><p>Kai is the round button in the corner of every page. Tell Kai how you\'re feeling and it can suggest a breathing practice, a short meditation or a walk, or point you to a meeting or a helpline. Replies are written in this browser from saved rules. No network and no AI service. Kai isn\'t AI, and isn\'t a person, counsellor, doctor or sponsor. Nothing you type leaves your browser.</p></div></div>' if KAI_ON else ""
KAI_FAQ = "<h3>Is Kai on the website?</h3><p>Yes. Kai, your recovery buddy, is the round button in the corner of every page. Kai isn't AI, and isn't a person, counsellor, doctor or sponsor. Replies are put together in your browser from saved rules, the same ones the app uses. Kai makes no network calls, and nothing you type leaves your browser. If you type something that may mean you're in danger, Kai tries to show help numbers, but it can miss things. If you're not safe, tap I'm not safe or call 000. You can minimise Kai, drag it to the other side, or clear the chat. Kai hides while a breathing guide or meditation is playing.</p>" if KAI_ON else '<h3>Is Kai on the website?</h3><p>Not right now. Kai, your recovery buddy, is taking a short break from the website while we update it. If you\'re unsafe, call <a href="tel:000">000</a> or Lifeline on <a href="tel:131114">13 11 14</a>, or use the Help button in the top corner of every page.</p>'

# Words that only make sense inside the iPhone app, changed for the web. Listed in the report.
WEB_EDITS = {
    "When it eases, jot what helped. That note stays on this phone.": "When it eases, jot down what helped.",
    "Angry: is something unnamed? You can tell a sponsor or write it here, on this phone.": "Angry: is something unnamed? You can tell a sponsor or write it down.",
    "This practice is off until you turn it on in Profile. If focusing inward brings up distress, stop.": "This practice stays hidden until you choose to show it. If focusing inward brings up distress, stop.",
    "The out-breath is the long part. The hold is optional in spirit: skip this practice if holds are off in Health safety.": "The out-breath is the long part. Skip this practice if breath holds aren't right for you (see the safety note above).",
    "Use it when the other counts are hidden by your health notes, or whenever you prefer it.": "Use it if breath holds aren't right for you, or whenever you prefer it.",
    "Kai leads a short sit with the wave of an urge.": "A short guided sit with the wave of an urge.",
    "Use the official site, or find a meeting in the app.": "Use the official site, or find a meeting with the HomeCircle meeting finder.",
    "Use AA Australia's website, or find a meeting in the app.": "Use AA Australia's website, or find a meeting with the HomeCircle meeting finder.",
    "Use NA Australia's website, or find a meeting in the app.": "Use NA Australia's website, or find a meeting with the HomeCircle meeting finder.",
}
# Accessibility options (10 Nov 2026): shared practice copy, written once for AU and US (tools/access_copy.py).
import sys as _sys0; _sys0.path.insert(0, str(ROOT / "tools")); import access_copy as AC
A = AC.copy("AU")
def web(t):
    t = WEB_EDITS.get(t, t)
    t = t[5:] if t.startswith("Kai: ") else t
    return AC.edit(A, t)
def title_of(i):
    return A["MOVING"]["title"] if i["id"] == "med-walk" else i["title"]

PAGES = [("index.html", "Home"), ("library.html", "Library"), ("twelve-steps.html", "12 Steps"),
         ("meditations.html", "Meditations & breathing"), ("meetings.html", "Meetings"),
         ("help.html", "Help"), ("families/index.html", "For families & partners"), ("your-circle.html", "Your circle"), ("support.html", "Support")]
PRIVACY = L["privacyURL"]
TERMS = L["termsURL"]
H = C["helplines"]
import hashlib as _h
RA_V = _h.sha256((ROOT / "assets" / "readaloud.js").read_bytes()).hexdigest()[:10]
CSS_V = _h.sha1((ROOT / "assets" / "site.css").read_bytes()).hexdigest()[:8]
# One shared cache-busting tag for the three Kai scripts, from their contents (deterministic): changes whenever any of them changes.
KAI_V = _h.sha256(b"".join((ROOT / "assets" / f).read_bytes() for f in ("kai.js", "kai-crisis.js", "kai-engine.js"))).hexdigest()[:10]
SITE_URL = "https://homecircle.au"

# Published HTML paths on each site. hreflang tags are generated from the intersection.
AU_SITE_PATHS = {
    'events.html',
    'families/child.html',
    'families/family.html',
    'families/friend.html',
    'families/index.html',
    'families/kids.html',
    'families/overdose.html',
    'families/partner.html',
    'families/safety.html',
    'families/withdrawal.html',
    'help.html',
    'index.html',
    'library.html',
    'library/24-hour-plan.html',
    'library/4-7-8-breathing.html',
    'library/alcohol-and-the-body.html',
    'library/alcoholics-anonymous.html',
    'library/body-and-recovery-stages.html',
    'library/body-scan.html',
    'library/box-breathing.html',
    'library/breathing-anchor.html',
    'library/cannabis-and-the-body.html',
    'library/gambling-support.html',
    'library/grounding-5-4-3-2-1.html',
    'library/halt.html',
    'library/mindful-eating.html',
    'library/mindful-walking.html',
    'library/narcotics-anonymous.html',
    'library/one-thing-focus.html',
    'library/opioids-and-the-body.html',
    'library/pornography-addiction-support.html',
    'library/recovery-books.html',
    'library/slow-out-breath.html',
    'library/stimulants-and-the-body.html',
    'library/stress-and-anxiety.html',
    'library/urge-surfing-meditation.html',
    'library/urge-surfing.html',
    'meditations.html',
    'meetings.html',
    'support.html',
    'twelve-steps.html',
    'your-circle.html',
}
US_SITE_PATHS = {
    'health-privacy.html',
    'help.html',
    'index.html',
    'library.html',
    'library/24-hour-plan.html',
    'library/4-7-8-breathing.html',
    'library/alcoholics-anonymous.html',
    'library/body-scan.html',
    'library/box-breathing.html',
    'library/breathing-anchor.html',
    'library/gamblers-anonymous.html',
    'library/grounding-5-4-3-2-1.html',
    'library/halt.html',
    'library/mindful-eating.html',
    'library/mindful-walking.html',
    'library/narcotics-anonymous.html',
    'library/one-thing-focus.html',
    'library/pornography-addiction-support.html',
    'library/recovery-books.html',
    'library/slow-out-breath.html',
    'library/stress-and-anxiety.html',
    'library/urge-surfing-meditation.html',
    'library/urge-surfing.html',
    'meditations.html',
    'overdose.html',
    'privacy.html',
    'support.html',
    'terms.html',
    'twelve-steps.html',
}

AU_ORIGIN = "https://homecircle.au"
US_ORIGIN = "https://homecirclerecovery.com"

def page_abs_url(origin, path):
    return origin + "/" + ("" if path == "index.html" else path)

def hreflang_tags(path):
    """Alternate language tags for paths that exist on both sites. x-default is the AU URL."""
    if path not in (AU_SITE_PATHS & US_SITE_PATHS):
        return ""
    au = page_abs_url(AU_ORIGIN, path)
    us = page_abs_url(US_ORIGIN, path)
    return (
        f'<link rel="alternate" hreflang="en-AU" href="{au}">\n'
        f'<link rel="alternate" hreflang="en-US" href="{us}">\n'
        f'<link rel="alternate" hreflang="x-default" href="{au}">\n'
    )
APP_STORE_URL = "https://apps.apple.com/au/app/homecircle/id6819366068"
APP_STORE_ID = "6819366068"
OG_IMAGE = f"{SITE_URL}/assets/og-homecircle.png"
BUILT_PAGES = []  # filled by page(); used for sitemap.xml
# Raven titles/descriptions (seo-basics-v2). Exact strings; do not keyword-stuff.
SEO_META = json.loads((ROOT / "tools" / "seo_meta.json").read_text())
SEO_META["library/mindful-walking.html"] = {"title": A["MOVING"]["seoTitle"], "description": A["MOVING"]["seoDesc"]}   # Mindful moving, same URL

def kai_data_v():
    """kai-data.js is generated by build_kai_data(), which runs before the pages are written."""
    return _h.sha256((ROOT / "assets" / "kai-data.js").read_bytes()).hexdigest()[:10]
HL = {v["id"]: v for v in H["lines"].values()}
RA_SAVE = 'Read aloud downloads that page\'s recordings from this website. <a href="{u}#website">More in the privacy policy</a>.'.format(u=PRIVACY)
BROWSER_ONLY = "Site features that save anything (your day count, journal, health notes and Kai chat) keep it only in this browser's local storage. Nothing is sent to HomeCircle."
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

HEART = '<svg class="heart" aria-hidden="true" focusable="false" viewBox="0 0 24 24" width="20" height="20"><path fill="currentColor" d="M12 21.2l-1.4-1.3C5.4 15.3 2 12.2 2 8.4 2 5.3 4.4 3 7.4 3c1.7 0 3.4.8 4.6 2.1C13.2 3.8 14.9 3 16.6 3 19.6 3 22 5.3 22 8.4c0 3.8-3.4 6.9-8.6 11.5L12 21.2z"/></svg>'

def tel(line, label=None):
    """A call button for one HelpDirectory line, exactly as the app shows it."""
    return f'<a class="btn ghost" href="tel:{line["dial"]}">{E(label or "Call " + line["displayNumber"])}</a>'

def canonical_url(path):
    if not path or path == "index.html":
        return SITE_URL + "/"
    return SITE_URL + "/" + path

def seo_head(title, desc, path):
    """Canonical, Open Graph, Twitter and JSON-LD. No noindex. CSP unchanged."""
    import json as _json
    canon = canonical_url(path)
    org = {
        "@type": "Organization",
        "name": "HomeCircle",
        "legalName": "Luke Endrody",
        "url": SITE_URL,
        "email": "support@homecircle.au",
        "logo": OG_IMAGE,
        "sameAs": [APP_STORE_URL],
        "description": "HomeCircle offers free addiction recovery support in Australia. Support, not medical care.",
    }
    app = {
        "@type": "MobileApplication",
        "name": "HomeCircle",
        "softwareVersion": UPDATES["version"],
        "operatingSystem": "iOS",
        "applicationCategory": "HealthApplication",
        "url": SITE_URL,
        "downloadUrl": APP_STORE_URL,
        "installUrl": APP_STORE_URL,
        "identifier": APP_STORE_ID,
        "offers": {"@type": "Offer", "price": "0", "priceCurrency": "AUD"},
        "description": "Free addiction recovery support in Australia: meetings finder, breathing tools, day counter and helplines. Not affiliated with AA, NA, GA or PA. Support, not medical care.",
        "author": {"@type": "Organization", "name": "HomeCircle"},
    }
    webpage = {
        "@type": "WebPage",
        "name": title,
        "description": desc,
        "url": canon,
        "isPartOf": {"@type": "WebSite", "name": "HomeCircle", "url": SITE_URL},
        "inLanguage": "en-AU",
    }
    ld = {"@context": "https://schema.org", "@graph": [org, app, webpage]}
    ld_json = _json.dumps(ld, ensure_ascii=False, separators=(",", ":"))
    ld_json = ld_json.replace("</", r"<\/")
    return f"""<link rel="canonical" href="{canon}">
{hreflang_tags(path)}<meta property="og:type" content="website">
<meta property="og:site_name" content="HomeCircle">
<meta property="og:locale" content="en_AU">
<meta property="og:url" content="{canon}">
<meta property="og:title" content="{E(title)}">
<meta property="og:description" content="{E(desc)}">
<meta property="og:image" content="{OG_IMAGE}">
<meta property="og:image:width" content="1200">
<meta property="og:image:height" content="630">
<meta property="og:image:alt" content="HomeCircle: free recovery support in Australia">
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:title" content="{E(title)}">
<meta name="twitter:description" content="{E(desc)}">
<meta name="twitter:image" content="{OG_IMAGE}">
<script type="application/ld+json">{ld_json}</script>
"""

def head(title, desc, r, path=""):
    return f"""<!DOCTYPE html>
<html lang="en-AU" class="no-js">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<meta http-equiv="Content-Security-Policy" content="default-src 'self'; script-src 'self'; style-src 'self'; img-src 'self'; media-src 'self' blob: data:; connect-src 'self' https://lendrody28-spec.github.io; base-uri 'self'; form-action 'self'; object-src 'none'">
<meta name="referrer" content="no-referrer">
<title>{E(title)}</title>
<meta name="description" content="{E(desc)}">
{seo_head(title, desc, path)}<link rel="icon" href="{r}favicon.png" type="image/png">
<link rel="apple-touch-icon" href="{r}assets/logo-192.png">
<link rel="stylesheet" href="{r}assets/site.css?v={CSS_V}">
<script src="{r}assets/site.js" defer></script>
<script src="{r}assets/readaloud.js?v={RA_V}" defer></script>
<script src="{r}assets/kai-data.js?v={kai_data_v()}" defer></script>
<script src="{r}assets/kai-crisis.js?v={KAI_V}" defer></script>
<script src="{r}assets/kai-engine.js?v={KAI_V}" defer></script>
<script src="{r}assets/kai.js?v={KAI_V}" defer></script>
</head>
<body>
<a class="skip" href="#main">Skip to content</a>"""

def header(active, r):
    lis = "".join(f'<li><a href="{r}{h}"{" aria-current=\"page\"" if h == active else ""}>{E(t)}</a></li>' for h, t in PAGES)
    return f"""
<header class="site-head"><div class="wrap">
  <a class="brand" href="{r}index.html"><img src="{r}assets/logo-96.png" alt="" width="46" height="46"><span><b>HomeCircle</b><span class="au-badge" title="HomeCircle Australia"><span class="sr-only">, Australia</span><span aria-hidden="true">AU</span></span><small>Support for your recovery journey</small></span></a>
  <a class="region-switch region-switch-header" href="https://homecirclerecovery.com/">In the US? Go to HomeCircle US</a>
  <button class="btn ghost menu-btn" id="menu-btn" type="button" aria-expanded="false" aria-controls="site-nav" hidden>Menu</button>
  <nav class="nav" id="site-nav" aria-label="Main"><ul>{lis}<li class="region-switch-item"><a class="region-switch region-switch-menu" href="https://homecirclerecovery.com/">In the US? Go to HomeCircle US</a></li></ul></nav>
</div></header>
<a class="help-pill" id="help-pill" href="{r}help.html#now" aria-label="{E(C["crisis"]["accessibilityLabel"])}" aria-describedby="help-pill-hint" aria-controls="help-dialog">{HEART}<span aria-hidden="true">Help</span></a>
<a class="fam-link" href="{r}families/index.html">For families &amp; partners</a>
<span class="sr-only" id="help-pill-hint">{E(C["crisis"]["accessibilityHint"])}</span>"""

def kai_copy():
    """Buttons-first panel strings live in one block in assets/kai-engine.js (HALE-REVIEW-START/END)."""
    import json as _json
    js = (ROOT / "assets/kai-engine.js").read_text()
    m = re.search(r"HALE-REVIEW-START.*?\*/\s*var BUTTON_COPY = (\{.*?\});\s*(?:/\* footLine:.*?\*/\s*)?/\* ===== HALE-REVIEW-END", js, re.S)
    return _json.loads(m.group(1))

def kai_tels(c):
    return "".join(f'<a class="btn{" danger" if t["kind"] == "emergency" else ""}" href="{t["href"]}"{(' aria-label="' + E(t["aria"]) + '"') if t.get("aria") else ""}>{E(t["label"])}</a>' for t in c["tels"])

# kai-foot uses BUTTON_COPY.footLine. Its "isn't AI" claim is only valid while web Kai is rule-based and runs in the browser.
def kai_panel(r):
    c = kai_copy()
    return f"""
<div class="kai" id="kai" data-root="{r}" hidden>
  <section class="kai-panel" id="kai-panel" role="dialog" aria-labelledby="kai-title" hidden>
    <div class="kai-head">
      <img src="{r}assets/kai.png" alt="" width="44" height="44">
      <div><h2 id="kai-title">Kai</h2><p>Recovery Buddy</p></div>
      <button class="btn ghost kai-small" type="button" id="kai-clear">Clear</button>
      <button class="btn ghost kai-small" type="button" id="kai-min" aria-label="Minimise Kai">Minimise</button>
    </div>
    <div class="kai-confirm card" id="kai-confirm" role="alertdialog" aria-labelledby="kai-confirm-h" hidden>
      <p id="kai-confirm-h"><strong>Clear this chat?</strong> This removes the messages in this browser. The Help button in the top corner still calls 000 or Lifeline 13 11 14, and the Help page lists every line.</p>
      <div class="btn-row"><button class="btn danger" type="button" data-yes>Clear chat</button><button class="btn ghost" type="button" data-no>Cancel</button></div>
    </div>
    <div class="kai-crisis kai-pinned" id="kai-crisis" role="region" aria-label="{E(c["panelLabel"])}"><button class="kai-notsafe" id="kai-notsafe" type="button" aria-label="{E(c["notSafe"]["aria"])}"><svg aria-hidden="true" focusable="false" width="22" height="22" viewBox="0 0 24 24"><circle cx="12" cy="12" r="9" fill="none" stroke="currentColor" stroke-width="3"/><circle cx="12" cy="12" r="3.5" fill="currentColor"/></svg><span>{E(c["notSafe"]["label"])}</span></button>{kai_tels(c)}</div>
    <div class="kai-scroll">
      <p class="kai-firstopen" id="kai-firstopen">{E(c["firstOpen"])}</p>
      <div class="kai-start" id="kai-start" role="group" aria-labelledby="kai-start-h"><h3 id="kai-start-h">{E(c["heading"])}</h3><button class="kai-big" type="button" data-kai-button="struggling">{E(c["struggling"]["label"])}</button><button class="kai-big" type="button" data-kai-button="cravings">{E(c["cravings"]["label"])}</button><button class="kai-big" type="button" data-kai-button="meeting">{E(c["meeting"]["label"])}</button><p class="kai-typehint">{E(c["typeHint"])}</p></div>
      <p class="kai-note"><strong>Kai isn't AI, and isn't a person, counsellor, doctor or sponsor.</strong> Replies are written in this browser from saved rules. No network and no AI service: nothing you type leaves your browser.</p>
      <p class="kai-note">Kai is a recovery buddy, not a counsellor. HomeCircle doesn't give medical advice. In an emergency call 000, or Lifeline on 13 11 14.</p>
      <p class="kai-empty" id="kai-empty">Kai is here. Pick a chip, or write a line.</p>
      <div class="kai-log" id="kai-log"></div>
      <div class="kai-after" id="kai-after"></div>
    </div>
    <p class="sr-only" id="kai-live" aria-live="polite"></p>
    <div class="kai-chips" id="kai-chips" role="group" aria-label="Quick replies"></div>
    <form class="kai-form" id="kai-form" autocomplete="off">
      <label class="sr-only" for="kai-input">Message Kai</label>
      <textarea id="kai-input" rows="1" maxlength="500" placeholder="Write a line"></textarea>
      <button class="btn" type="submit">Send</button>
    </form>
    <p class="kai-foot">{E(c["footLine"])} <button class="linkish" type="button" id="kai-move">Move Kai to the left</button></p>
  </section>
  <button class="kai-bubble" id="kai-bubble" type="button" aria-expanded="false" aria-controls="kai-panel" aria-label="Kai, Recovery Buddy. Not AI and not a person."><img src="{r}assets/kai.png" alt="" width="64" height="64" draggable="false"></button>
</div>
<div class="kai-fallback" id="kai-fallback" role="region" aria-label="{E(c["panelLabel"])}"><strong>{E(c["fallbackLead"])}</strong> {kai_tels(c)}
</div>"""

def footer(r):
    s_ = C["crisis"]
    em, ll = HL["000"], HL["lifeline"]
    return f"""
<footer class="site-foot"><div class="wrap"><p class="region-switch-footer-slot"><a class="region-switch region-switch-footer" href="https://homecirclerecovery.com/">In the US? Go to HomeCircle US</a></p></div>
<div class="wrap cols">
  <div>
    <h2>HomeCircle</h2>
    <p>Support for your recovery journey. Free, with no accounts, no sign-in, no cookies, no ads, no trackers and no analytics.</p>
    <p>{E(L["gpLine"])} {E(L["notMedicalDevice"])} In an emergency call <a href="tel:000">000</a>. Lifeline <a href="tel:131114">13 11 14</a>.</p>
    <p>{E(L["notAffiliated"])}</p>
    <p><a href="https://www.facebook.com/61595778045748" rel="noopener">Follow HomeCircle on Facebook</a></p>
  </div>
  <div><h2>Explore</h2><ul>{"".join(f'<li><a href="{r}{h}">{E(t)}</a></li>' for h, t in PAGES)}<li><a href="{r}find-treatment.html">Find treatment near you</a></li><li><a href="{r}before-you-drive.html">Before you drive</a></li></ul></div>
  <div><h2>About</h2><ul>
    <li><a href="{PRIVACY}">Privacy Policy</a></li>
    <li><a href="{TERMS}">Terms of Use</a></li>
    <li><a href="{r}support.html#website">About this website</a></li>
    <li><a href="mailto:support@homecircle.au">Contact</a></li>
    <li><a href="mailto:{L["supportEmail"]}">{L["supportEmail"]}</a> (not a crisis line)</li>
  </ul><p class="small">{E(BROWSER_ONLY)} {RA_SAVE}</p></div>
</div><div class="wrap"><p class="fine-print">© 2026 {E(L["owner"])} (sole trader), {E(L["ownerPlace"])}. ABN 53 687 374 897.</p></div></footer>
<dialog class="help" id="help-dialog" aria-labelledby="help-title">
  <div class="help-in">
    <button class="close-x" type="button" data-close aria-label="Close">×</button>
    <h2 id="help-title">{E(s_["sheetTitle"])}</h2>
    <ul class="help-lines">
      <li><a class="first" href="tel:{em["dial"]}">Call 000<small>{E(em["detail"])}</small></a></li>
      <li><a class="second" href="tel:{ll["dial"]}">Call Lifeline {E(ll["displayNumber"])}<small>{E(ll["detail"])}</small></a></li>
    </ul>
    <p>{E(s_["sheetIntro"])}</p>
    <a class="btn ghost wide" href="{r}help.html">More helplines on the Help page</a>
    <button class="btn ghost wide plain" type="button" data-close>Close</button>
  </div>
</dialog>{kai_panel(r)}
</body>
</html>
"""

# ---------- read aloud (tools/ra.py; clips are DRAFTS until Hale approves) ----------
import sys as _sys; _sys.path.insert(0, str(ROOT / "tools")); import ra as RA
REGION = "AU"
RA_KAI = RA.kai_lines(REGION)
RA_HELP_BODY = None
RA_PAGE_SIZES = {}
RA_NOTE = "Read aloud plays recordings stored on this website, or your device's own voice. Nothing you read or type is sent anywhere."  # Hale approved, 5 Nov 2026; kept 10 Nov 2026: device-voice fallback uses only SpeechSynthesisVoice.localService === true; if none, text only (buttons hidden / line skipped). No online voice path.
RA_BAR = f'<div class="ra-bar ra-skip"><p class="ra-note small">{RA_NOTE}</p><p class="ra-note ra-transcript small">{E(A["SITE"]["transcript"])}</p></div>\n'
def ra_read_page(path):
    return path in ("help.html", "twelve-steps.html", "support.html") or (path.startswith("families/") and path != "families/children-and-parental-aod.html")
def ra_insert_bar(path, body):
    # After the top call buttons (they come before the h1); on Support, after the crisis notice with the call links.
    if path == "support.html":
        m = re.search(r'<div class="notice">.*?tel:.*?</div>\n', body)
        if m: return body[:m.end()] + RA_BAR + body[m.end():]
    i = body.find("<h1")
    return body[:i] + RA_BAR + body[i:] if i >= 0 else RA_BAR + body

SHARE_ICON = '<svg aria-hidden="true" focusable="false" width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="18" cy="5" r="3"/><circle cx="6" cy="12" r="3"/><circle cx="18" cy="19" r="3"/><line x1="8.59" y1="13.51" x2="15.42" y2="17.49"/><line x1="15.41" y1="6.51" x2="8.59" y2="10.49"/></svg>'
SHARE_HOME = """<div class="card share-card mt ra-skip"><div><p class="eyebrow">Share HomeCircle</p><h2 class="mt0">Know someone who'd find this useful?</h2>
<p>Share HomeCircle with a friend, family member or client, or post it to Facebook, Instagram or X. It opens the share options on your phone, or copies the link on a computer. HomeCircle doesn't track shares.</p></div>
<div class="share-actions"><button class="btn" type="button" id="hc-share">{icon}<span>Share HomeCircle</span></button><p class="small" id="hc-share-status" role="status"></p></div></div>
<script src="assets/share.js" defer></script>""".format(icon=SHARE_ICON)

def page(path, active, title, desc, body):
    global RA_HELP_BODY
    if path in SEO_META:
        title = SEO_META[path]["title"]
        desc = SEO_META[path]["description"]
    r = "../" * path.count("/")
    if ra_read_page(path): body = ra_insert_bar(path, body)
    if path == "help.html": RA_HELP_BODY = body
    out = head(title, desc, r, path) + header(active, r) + f'\n<main id="main"><div class="wrap">\n{body}\n</div></main>' + footer(r)
    if path.startswith("families/") or path == "before-you-drive.html" or not KAI_ON:  # no Kai chat on families or the drive page (or anywhere while KAI_ON is False)
        out = re.sub(r'<script src="[^"]*kai[^"]*" defer></script>\n', "", out)
        out = re.sub(r'\n<div class="kai" id="kai".*?\n</div>(?=\n</body>)', "", out, flags=re.S)
    kai_here = 'id="kai"' in out
    lines = ([l["text"] for l in RA_KAI] if kai_here else []) + (RA.page_chunks(body) if path == "help.html" else [])
    clips = RA.page_clips(lines, r)
    if clips: out = out.replace("\n</body>", "\n" + clips + "\n</body>", 1)
    RA_PAGE_SIZES[path] = RA.sizes(lines)
    (ROOT / path).parent.mkdir(parents=True, exist_ok=True)
    (ROOT / path).write_text(out)
    BUILT_PAGES.append(path)

def art_img(key, r, cls="", eager=False):
    a = ARTS[key]
    return f'<img src="{r}assets/art/{a["asset"]}.jpg" alt="{E(a["label"])}" width="1024" height="768"{"" if eager else " loading=\"lazy\""}{f" class=\"{cls}\"" if cls else ""}>'

def tile(href, title, summary, tag, artkey, r, mins=None, hold=False):
    pic = art_img(artkey, r) if artkey else f'<div class="icon-tile" aria-hidden="true">{E(title)}</div>'
    m = f" · {mins} min" if mins and mins > 1 else ""
    return f'<a class="card tile" href="{href}"{" data-breath-hold" if hold else ""}>{pic}<div class="tbody"><span class="tag">{E(tag)}{m}</span><h3>{E(title)}</h3><p>{E(summary)}</p></div></a>'

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
EV_ICON = '<svg class="ev-ico" aria-hidden="true" focusable="false" viewBox="0 0 64 64" width="64" height="64"><circle cx="32" cy="32" r="30" fill="#B9D3B0"/><rect x="17" y="20" width="30" height="26" rx="5" fill="#FBF6E8" stroke="#0D6968" stroke-width="3"/><path d="M17 28h30M25 15v9M39 15v9" stroke="#0D6968" stroke-width="3" stroke-linecap="round"/><circle cx="32" cy="37" r="4" fill="#F2A08B"/></svg>'
def ev_image(e, r):
    """Show a photo only with permission and a local file under assets/events/; never a remote URL."""
    img = e.get("image") or ""
    ok = e.get("image_permission") is True and img.startswith("assets/events/") and ".." not in img and (ROOT / img).is_file()
    credit = f'<figcaption class="small">{E(e["image_credit"])}</figcaption>' if ok and e.get("image_credit") else ""
    if ok:
        return f'<figure class="ev-pic"><img src="{r}{E(img)}" alt="{E(e.get("image_alt") or "")}" loading="lazy">{credit}</figure>'
    return f'<figure class="ev-pic ev-ph">{EV_ICON}</figure>'
def ev_card(e, r=""):
    end = e.get("end", e["start"])
    rng = fmt_date(e["start"]) + (f" to {fmt_date(end)}" if end != e["start"] else "")
    when = E(rng) + (f" · {E(e['time'])}" if e.get("time") else "")
    summary = e.get("summary") or f"A {e['fellowship']} event listed by {e['organiser']}."
    full = e.get("description") or "HomeCircle only shows what the official listing says. Times, costs and full details are on the organiser's page."
    return f"""<li class="ev-card" data-end="{end}"><article aria-labelledby="ev-{E(e['start'])}-{_h.sha1(e["source"].encode()).hexdigest()[:6]}">{ev_image(e, r)}
<div class="ev-body"><span class="pill">{E(e['fellowship'])}</span><h3 id="ev-{E(e['start'])}-{_h.sha1(e["source"].encode()).hexdigest()[:6]}">{E(e['title'])}</h3>
<p class="ev-meta"><span><b>When:</b> {when}</span><span><b>Where:</b> {E(e['place'])}, {E(e['state'])}</span></p>
<p class="ev-sum">{E(summary)}</p>
<details class="ev-more"><summary>More details</summary><p>{E(full)}</p><p><b>Organiser:</b> {E(e['organiser'])}</p><p><a href="{E(e['source'])}" rel="noopener">Official event page<span class="sr-only">: {E(e['title'])}</span></a></p></details></div></article></li>"""
def events_html(limit=4, r="", full=False):
    evs = sorted([e for e in EVENTS["events"] if e.get("end", e["start"]) >= TODAY], key=lambda e: e["start"])
    shown = evs if full else evs[:limit]
    cards = "".join(ev_card(e, r) for e in shown)
    see = "" if full else f'<p><a class="btn" href="{r}events.html">See all events</a></p>'
    return f"""
<section aria-labelledby="ev-h">
<h2 id="ev-h">Upcoming events</h2>
<p>Conventions, rallies, unity days and service events from the fellowships' own event pages, soonest first.</p>
<p class="note small">HomeCircle is independent and isn't affiliated with or endorsed by Alcoholics Anonymous or Narcotics Anonymous. Dates and details can change, so always check the official page.</p>
<ul class="ev-feed" id="events-list" data-limit="{0 if full else limit}">{cards}</ul>
<div class="card sage" id="events-empty"{" hidden" if evs else ""}><h3>No upcoming events listed right now</h3><p>Check <a href="https://members.aa.org.au/events/">AA Australia events</a> and <a href="https://www.na.org.au/multi/events/">NA Australia events</a>.</p></div>
{see}<p class="small">Event list checked on {fmt_date(EVENTS["updated"])}.</p>
</section>"""

def updates_html():
    """Public status from updates.json, written into the page. The browser does not fetch it."""
    here = UPDATES["whereWeAre"]
    paras = "".join("<p>" + E(p) + "</p>" for p in here["paragraphs"])
    return '<section class="card mt hc-updates" aria-labelledby="hc-where-h"><h2 id="hc-where-h" class="mt0">' + E(here["heading"]) + "</h2>" + paras + "</section>"

def support_faq():
    src = (ROOT / "tools" / "support-app-faq.html").read_text().lstrip("\n")
    src = re.sub(r'^<p class="small">.*?</p>\n\n', "", src, count=1, flags=re.S)
    return '<p class="small">' + E(UPDATES["supportLead"]) + "</p>\n\n" + src

# ---------- home ----------
def build_home():
    r = ""
    feats = [
        ("meetings.html", "Find a meeting", "AA and NA meetings across Australia. Search by suburb, postcode and day.", "Meetings", "groundSee"),
        ("meditations.html", "Breathe now", "An animated breathing guide: box, 4-7-8 or a slow out-breath.", "Breathing", "breatheIn"),
        ("library.html", "Library", "Guides, breathing, meditation, body and fellowships.", "Library", "oneThing"),
        ("twelve-steps.html", "The 12 Steps", C["twelveStepsCopy"]["summary"], "12 Steps", "dayPlan"),
    ]
    feats2 = [
        ("your-circle.html", "Your circle", "A day counter and a private journal, kept only in this browser.", "Your circle", "oneThing"),
        ("families/index.html", "For families & partners", "Worried about someone you love? What to say, warning signs and support for you.", "Families", "handOnChest"),
        ("help.html", "Helplines", "000, Lifeline and every helpline in the app, plus lines in your state.", "Help", "handOnChest"),
        ("before-you-drive.html", "Before you drive", "Other ways home, what alcohol and drugs can do, official figures, and limits pages for each state and territory.", "Safety", "groundSee"),
    ]
    tiles = "".join(tile(h, t, s, tg, a, r) for h, t, s, tg, a in feats)
    body = f"""
<section class="hero">
  <div>
    <p class="eyebrow">Free · Australian · No sign-in</p>
    <h1><span class="grad-text">Support for your recovery journey</span></h1>
    <p class="lede">HomeCircle is a free Australian recovery support app, and this website brings its no-account tools to your browser: find AA and NA meetings and add a reminder, breathe along with a guide, read plain-language guides and the 12 Steps, keep a day count and journal in your browser{", and chat with Kai" if KAI_ON else ""}.</p>
    <div class="btn-row"><a class="btn" href="meetings.html">Find a meeting</a><a class="btn ghost" href="meditations.html">Breathe now</a><a class="btn ghost" href="library.html">Open the Library</a></div>
    <p class="small">Everything here is free. No accounts, no cookies, no ads, no trackers and no analytics. Anything you save stays in this browser.</p>
  </div>
  <div class="hero-art"><img src="assets/logo-192.png" alt="HomeCircle logo: three people with arms raised inside a circle" width="260" height="260"><p>You're not alone.</p></div>
</section>
<div class="notice"><strong>Need help right now?</strong> {E(L["notMedicalDevice"])} In an emergency call <a href="tel:000">000</a>. For crisis support call Lifeline on <a href="tel:131114">13 11 14</a>.</div>
<h2>What you can do here</h2>
<div class="grid g4">{tiles}</div>
<div class="grid g4 mt">{"".join(tile(h, t, s, tg, a, r) for h, t, s, tg, a in feats2)}</div>
{KAI_INTRO}
<div class="card mt about-hc"><h2 class="mt0">{E("Support for your recovery journey, and for the people who love you")}</h2>
<p>{E("Whether you're in recovery, or you're a parent, partner, child or friend of someone with an addiction, HomeCircle is here for you. It's free for everyone. The app is for adults 18+. Our ")}<a href="families/index.html">{E("Families pages")}</a>{E(" are open to everyone, with Kids Helpline (")}<a href="tel:1800551800">1800 55 1800</a>{E(") for young people.")}</p>
<ul>
<li><strong>{E("Recovery support:")}</strong> {E("coping guides, plain-language reflections on the ")}<a href="twelve-steps.html">{E("12 Steps")}</a>{E(", an AA and NA ")}<a href="meetings.html">{E("meeting finder")}</a>{E(", plus links to Gamblers Anonymous and Porn Addicts Anonymous")}</li>
<li><strong>{E("Calm when you need it:")}</strong> <a href="meditations.html">{E("guided meditations")}</a>{E(" (4–5 min) and breathing exercises (1, 3 or 5 min)")}</li>
<li><strong>{E("Events:")}</strong> <a href="events.html">{E("upcoming AA and NA recovery events")}</a>{E(" around Australia")}</li>
<li><strong>{E("Families and friends:")}</strong> <a href="families/index.html">{E("ways to cope, what to say, and where to get support")}</a>{E(" when someone you love is struggling")}</li>
<li><strong>{E("Safety first:")}</strong> {E("a one-tap Quick exit on the families pages, and ")}<a href="families/safety.html">{E("domestic and family violence help")}</a>{E(", including 1800RESPECT (")}<a href="tel:1800737732">1800 737 732</a>{E(")")}</li>
<li><strong>{E("Checked sources:")}</strong> {E("linked to official and research sources, with the date each page was last checked")}</li>
</ul>
<p class="small">{E("HomeCircle is a support tool, not medical care. It isn't part of, affiliated with or endorsed by AA, NA, GA or PA. If you're in danger, call ")}<a href="tel:000">000</a>{E(". For crisis support, call Lifeline on ")}<a href="tel:131114">13 11 14</a>.</p></div>
{events_html()}
{SHARE_HOME}
<h2>The HomeCircle app</h2>
<div class="grid g2">
  <div class="card"><h3>In the iPhone app</h3><ul>
    <li><strong>Meetings near you</strong>, with a map.</li>
    <li><strong>A private journal and sober date</strong> that stay on your phone.</li>
    <li><strong>Kai, your recovery buddy</strong>: built-in templates on your phone for reflection and encouragement. It isn't AI, and nothing you type leaves your phone when you use the app.</li>
    <li><strong>Meeting reminders</strong> 2 hours before a meeting starts.</li>
    <li><strong>The same Library</strong>, breathing and meditation guides.</li>
  </ul><div class="btn-row"><a class="btn" href="https://apps.apple.com/au/app/homecircle/id6819366068">Get HomeCircle free on the App Store</a></div></div>
  <div class="card sage"><h3>Support, not medical care</h3><p>{E(L["gpLine"])}</p><p>{E(L["notAffiliated"])}</p><p>HomeCircle never reproduces the Big Book or NA literature. We link to the free official pages instead.</p></div>
</div>
{updates_html()}"""
    page("events.html", "", "Events – HomeCircle", "Upcoming AA and NA events from the fellowships' official pages.",
         events_html(full=True) + '<div class="btn-row"><a class="btn ghost" href="https://members.aa.org.au/events/">All AA Australia events</a><a class="btn ghost" href="https://www.na.org.au/multi/events/">All NA Australia events</a></div>')
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
            tiles.append(tile(item_href(i["id"]), title_of(i), web(i["summary"]), i["tag"], HERO.get(i["id"]), r, i["minutes"], i.get("breathHold")))
        out.append(f'<section data-cat="{k}" aria-labelledby="h-{k}"><h2 id="h-{k}">{t}</h2><div class="grid g4">{"".join(tiles)}</div></section>')
    body = f"""<h1>Library</h1>
<p class="lede">Resources and tools to support your growth: guides, breathing, meditation, body and fellowships. The same Library as the HomeCircle app, free to use here.</p>
{chips}
{HOLDS_NOTE}
{"".join(out)}
<p class="note small">{E(L["gpLine"])} {E(L["notAffiliated"])}</p>"""
    page("library.html", "library.html", "Library – HomeCircle", "Free recovery guides, breathing, meditation, body and fellowship pages from the HomeCircle app.", body)

HOLDS_NOTE = '<p class="note small" data-holds-hidden-note hidden>Breath holds are hidden in this browser, so box breathing and 4-7-8 breathing are left out. <a href="your-circle.html#health">Change this in Health safety</a>.</p>'

def holds_toggle(r):
    return f"""<div class="card sage holds" id="holds"><h2 class="mt0">Breath holds</h2>
<p>{E(L["breathHold"])}</p>
<label class="check"><input type="checkbox" data-health="hideHolds"> Hide breath holds in this browser</label>
<p class="small" data-holds-status aria-live="polite"></p>
<p class="small">This choice is kept only in this browser (local storage). More health notes are on <a href="{r}your-circle.html#health">Your circle</a>.</p></div>"""

# ---------- breathing widget ----------
def breath_widget(ids, r, default):
    opts = "".join(f'<option value="{i}"{" selected" if i == default else ""}>{E(ITEMS[i]["title"])}</option>' for i in ids)
    cues = "".join(f'<div data-cue-for="{i}"><p><strong>{E(ITEMS[i]["title"])}:</strong> {E(ITEMS[i]["summary"])}</p><ul>' + "".join(f'<li><strong>{E(s["title"])}</strong>: {E(s["cue"])}</li>' for s in ITEMS[i]["steps"]) + "</ul></div>" for i in ids)
    choose = f'<div><label for="b-pattern">Pattern</label><select id="b-pattern" data-pattern>{opts}</select></div>' if len(ids) > 1 else ""
    return f"""<div class="breath player" data-breath="{default}">
  <div class="breath-stage" aria-hidden="true"><div class="breath-ring"></div><div class="breath-ball"></div><div class="breath-label dark"><b data-phase>Ready</b><span data-count></span></div></div>
  <div>
    <div class="grid g2">{choose}<div><label for="b-min">Length</label><select id="b-min" data-minutes><option value="1">1 min</option><option value="3" selected>3 min</option><option value="5">5 min</option></select></div><div><label for="b-pace">{E(A["SITE"]["paceLabel"])}</label><select id="b-pace" data-pace><option value="1">{E(A["SITE"]["paceUsual"])}</option><option value="1.5">{E(A["SITE"]["paceSlower"])}</option></select></div></div>
    <label class="check breath-js" hidden><input type="checkbox" data-still> {E(A["SITE"]["still"])}</label>
    <div class="btn-row"><button class="btn" type="button" data-start aria-pressed="false">Start</button><button class="btn ghost" type="button" data-bpause aria-pressed="false" hidden>Pause</button><span class="status" data-left aria-hidden="true"></span></div>
    <p class="small">{E(A["SITE"]["pace"])} {E(A["SITE"]["stillNote"])}</p>
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
        lis.append(f'<li class="pstep" data-seconds="{s["seconds"]}"><div class="grid g2">{img}<div><h3>{E(A["TITLE_EDITS"].get(s["title"], s["title"]))}{secs}</h3><p>{E(web(s["cue"]))}</p></div></div></li>')
    return f"""<section class="player" data-player aria-labelledby="pl-h"><h2 id="pl-h" class="mt0">Step by step</h2>
<div class="pcontrols" hidden><div class="progress" aria-hidden="true"><i></i></div><p class="status" data-pos aria-live="polite"></p></div>
<ol class="steps-list">{"".join(lis)}</ol>
<div class="pcontrols btn-row" hidden><button class="btn ghost" type="button" data-prev>Back</button><button class="btn" type="button" data-play>Start</button><button class="btn ghost" type="button" data-next>Next</button><span class="count" data-pcount aria-hidden="true"></span></div>
{AC.pace_select(A, E, "pl")}
</section>"""

def build_item(i):
    path = item_href(i["id"])
    r = "../"
    hero = HERO.get(i["id"])
    parts = [f'<p class="crumbs"><a href="../library.html">Library</a> › {E(i["category"].title() if i["category"] != "guide" else "Guides")}</p>',
             f'<h1>{E(title_of(i))}</h1><p class="lede">{E(web(i["summary"]))}</p>']
    main = []
    if hero:
        main.append(f'<figure class="figure">{art_img(hero, r, eager=True)}</figure>')
    main.append(safety_notes(i))
    if i["id"] == "med-walk":
        main.append(moving_body(i, r))
        return finish_item(i, path, parts, main, r)
    if i["category"] == "body":
        main.append(f'<div class="notice"><strong>Safety.</strong> {E(C["stageCopy"]["safetyLine"])} {E(C["stageCopy"]["noDosing"])}</div>')
    paras = "".join(f"<p>{E(web(p))}</p>" for p in i["paragraphs"] + A["EXTRA_PARAS"].get(i["id"], []))
    if i["id"] == "med-scan":
        main.append(f'<div class="card sage" id="bodyscan-optin" hidden><h2 class="mt0">Body scan is off until you choose it</h2><p>It walks attention through the body. Skip it if that doesn\'t feel right. Nothing is saved.</p><button class="btn" type="button">Show the body scan</button></div><div id="bodyscan-content"><h2 tabindex="-1">About this practice</h2>{paras}{gentle_scan()}')
    else:
        main.append(f'<div>{paras}</div>')
    if i["kind"] == "breathing" and i.get("breathHold"):
        main.append(f'<div class="card sage" data-holds-hidden-note hidden><h2 class="mt0">Breath holds are hidden in this browser</h2><p>You chose to hide breath holds, or saved a health note that rules them out. Try the <a href="{item_href("breath-46", r)}">slow out-breath</a> instead, which has no hold.</p><div class="btn-row"><button class="btn ghost" type="button" data-show-holds>Show this practice anyway</button><a class="btn ghost" href="{r}your-circle.html#health">Health safety</a></div></div>')
        main.append(f'<div data-breath-hold><h2>Breathe along</h2>{breath_widget([i["id"]], r, i["id"])}</div>')
        main.append(holds_toggle(r))
    elif i["kind"] == "breathing":
        main.append(f'<h2>Breathe along</h2>{breath_widget([i["id"]], r, i["id"])}')
    elif i["steps"]:
        main.append(player(i, r))
    if i["id"] == "med-scan":
        main.append("</div>")
    bg = BG.get(i["id"])
    if bg:
        main.append(f'<div class="card"><h2 class="mt0">Where this comes from</h2><p>{E(bg["origin"])}</p><h2>Why it can help</h2><p>{E(web(bg["why"]))}</p>{src_list(bg["sources"])}</div>')
    links = [l for l in i["links"] if not l.get("inAppMeetings")]
    if any(l.get("inAppMeetings") for l in i["links"]):
        main.append('<p><a class="btn" href="../meetings.html">Find a meeting</a></p>')
    if links:
        main.append(src_list(links, "Official pages" if i["category"] == "fellowship" else "Read more"))
    if i.get("phoneDial"):
        main.append(f'<p><a class="btn ghost" href="tel:{i["phoneDial"]}">Call {E(i["phoneDisplay"])}</a></p>')
    if i["id"] == "guide-stress":
        main.append(stat_card(STATS["abs-anxiety"]))
    finish_item(i, path, parts, main, r)

def finish_item(i, path, parts, main, r):
    if i["id"] == "med-walk":
        bg = BG.get(i["id"])
        if bg:
            main.append(f'<div class="card"><h2 class="mt0">Where this comes from</h2><p>{E(bg["origin"])}</p><h2>Why it can help</h2><p>{E(web(bg["why"]))}</p>{src_list(bg["sources"])}</div>')
        links = [l for l in i["links"] if not l.get("inAppMeetings")]
        if links:
            main.append(src_list(links, "Read more"))
    main.append(f'<p class="small">{E(L["gpLine"])}</p>')
    body = "".join(parts) + f'<div class="layout"><div>{"".join(main)}</div>{aside(r)}</div>'
    page(path, "library.html", f'{title_of(i)} – HomeCircle Library', web(i["summary"]), body)

def moving_body(i, r):
    """Mindful moving (library/mindful-walking.html): walking, seated, wheelchair, lying-down and one-hand versions."""
    M = A["MOVING"]
    walk = [(s["title"], web(s["cue"]), s["seconds"], DRAW.get(s["drawing"])) for s in i["steps"]]
    intro = "".join(f"<p>{E(p)}</p>" for p in M["intro"])
    return (f'<div class="note"><strong>Stop if anything hurts.</strong> {E(M["safety"].split(". ", 1)[1])}</div><div>{intro}</div>'
            f'<h2 id="versions">{E(M["chooseHeading"])}</h2>'
            + AC.moving_versions(A, walk, web(i["paragraphs"][0]), art_img, r, E, lambda uid: AC.pace_select(A, E, uid)))

def gentle_scan():
    """Hale's gentler body-scan line, plus the breath-hold safety line."""
    S = A["SCAN"]; head, rest = S["gentle"].split(". ", 1)
    more = "".join(f"<li>{E(x)}</li>" for x in S["gentleMore"])
    return (f'<div class="note" id="gentler"><p class="mt0"><strong>{E(head)}.</strong> {E(rest)}</p>'
            f'<details class="more"><summary>{E(A["SITE"]["moreDetails"])}</summary><ul>{more}</ul></details>'
            f'<p><strong>Breath holds.</strong> {E(L["breathHold"])} {E(S["holdsNote"])}</p></div>')

def build_stages():
    r = "../"; S = C["stageCopy"]
    cards = []
    for s in C["stages"]:
        notes = "".join(f"<p>{E(n)}</p>" for n in s["notes"])
        st = stat_card(STATS[s["statID"]]) if s.get("statID") else ""
        tr = ""
        if s.get("practiceID"):
            it = ITEMS[s["practiceID"]]
            tr = f'<p><a href="{item_href(it["id"], r)}">{E(web(s["tryThis"]))} Open {E(title_of(it))}.</a></p>'
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
<div class="note"><strong>In HomeCircle's own plain-language words.</strong> These notes are HomeCircle's own summaries, not the official wording of AA or NA. For AA's own wording of the Twelve Steps, see <a href="{E(T["officialURL"])}" rel="noopener">aa.org</a>.</div>
<div class="btn-row"><a class="btn" href="{E(T["officialURL"])}" rel="noopener">{E(T["officialLinkTitle"])}</a><a class="btn ghost" href="{BOOKS_HREF}">Free recovery books</a></div>
<div class="twelve">{cards}</div>
<div class="card mt"><h2 class="mt0">Where this comes from</h2><p>The 12 Steps were first written down by Alcoholics Anonymous in the 1930s. Narcotics Anonymous and other fellowships adapted them. The notes on this page are HomeCircle's own plain-language summaries, not the official wording of AA or NA.</p>{src_list([{"title": "The Twelve Steps (opens aa.org)", "url": T["officialURL"]}])}</div>
<p class="small">{E(T["independence"])}</p>
</div><aside><figure class="figure">{art_img("dayPlan", r, eager=True)}</figure><div class="card sage"><h3>Find a meeting</h3><p>Many people work the Steps with a sponsor they meet at meetings.</p><p><a href="meetings.html">Search AA and NA meetings</a></p></div></aside></div>"""
    page("twelve-steps.html", "twelve-steps.html", "The 12 Steps – HomeCircle", T["summary"], body)

def build_meditations():
    r = ""
    br = ["breath-46", "breath-box", "breath-478"]
    meds = [i for i in C["items"] if i["category"] == "meditation"]
    tiles_b = "".join(tile(item_href(i), ITEMS[i]["title"], ITEMS[i]["summary"], "Breathing", HERO.get(i), r, ITEMS[i]["minutes"], ITEMS[i]["breathHold"]) for i in br)
    tiles_m = "".join(tile(item_href(i["id"]), title_of(i), web(i["summary"]), "Meditation", HERO.get(i["id"]), r, i["minutes"]) for i in meds)
    body = f"""<h1>Meditations and breathing</h1>
<p class="lede">Breathe along with the circle: it grows as you breathe in and shrinks as you breathe out. Then try a short guided meditation.</p>
<div class="note"><strong>Before you start.</strong> {E(L["beforeYouStart"])}</div>
<div class="notice"><strong>Breath holds.</strong> {E(L["breathHold"])} The slow out-breath has no hold.</div>
<h2>Breathing guide</h2>
{breath_widget(br, r, "breath-46")}
{holds_toggle(r)}
<h2>Breathing practices</h2>{HOLDS_NOTE}<div class="grid g3">{tiles_b}</div>
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
<div class="card" id="finder-nojs"><p>The meeting finder needs JavaScript. You can use AA's and NA's own meeting lists instead.</p></div>
<p class="status" id="f-status" role="status" aria-live="polite"></p>
<div class="results" id="results"></div>
<div class="btn-row"><button class="btn ghost" type="button" id="f-more" hidden>Show more</button></div>
<div class="grid g2 mt">
  <div class="card sage"><h2 class="mt0">About the list</h2><p id="feed-info">AA and NA meetings from public listings.</p><p>Listings come from public sources: AA Australia's Meeting Guide feed and NA Australia's BMLT meeting list. Times can change, so check with the group if you're unsure. Each meeting links to its official listing.</p><p class="small">Times show in the meeting's own time zone.</p></div>
  <div class="card"><h2 class="mt0">AA and NA meeting lists</h2><ul><li><a href="https://meetings.aa.org.au/">AA meetings list (AA Australia)</a></li><li><a href="https://www.na.org.au/multi/">NA Australia meetings</a></li><li><a href="https://www.gamblinghelponline.org.au/">Gambling Help Online</a> and <a href="https://www.gaaustralia.org.au/">Gamblers Anonymous</a></li></ul><p class="small">{E(L["notAffiliated"])} At meetings, please respect each group's own guidelines, and don't record or share what people say.</p></div>
</div>
<div class="card sage mt"><h2 class="mt0">Meeting reminders</h2><p>Choose <strong>Add reminder</strong> on a meeting, then <strong>Just this one</strong> or <strong>Every week</strong>. This downloads a calendar file (.ics) for your calendar app. Its alert is set for 2 hours before the meeting starts. HomeCircle sends no notifications, and nothing is sent to us.</p></div>
<p class="note small">{E(L["privateDetails"])}</p>
<script src="assets/meetings.js" defer></script>"""
    page("meetings.html", "meetings.html", "Find an AA or NA meeting – HomeCircle", "Search AA and NA meetings in Australia by suburb, postcode and day. Free, no sign-in.", body)

STATE_LINES = [  # helplines-verification-2026-11-04.md, section 4 (checked 4 Nov 2026)
    ("Queensland", [("Adis 24/7 Alcohol and Drug Support", "1800177833", "1800 177 833", "24/7. For Queenslanders and their family and friends.", "https://adis.health.qld.gov.au/")]),
    ("New South Wales", [("Alcohol and Drug Information Service (ADIS) NSW", "1800250015", "1800 250 015", "24/7. Sydney metro: 02 8382 1000. For NSW residents and their families.", "https://yourroom.health.nsw.gov.au/getting-help/Pages/adis.aspx")]),
    ("Victoria", [("DirectLine", "1800888236", "1800 888 236", "24/7 phone and online counselling. For Victorians, family members and others.", "https://www.directline.org.au/")]),
    ("South Australia", [("Alcohol and Drug Information Service (ADIS), DASSA", "1300131340", "1300 131 340", "Every day 8.30am to 10pm, not 24/7. Local call fee for SA callers. For the public, family and friends.", "https://www.sahealth.sa.gov.au/wps/wcm/connect/public+content/sa+health+internet/services/mental+health+and+drug+and+alcohol+services/drug+and+alcohol+services/dassa+services/alcohol+and+drug+information+service+adis")]),
    ("Western Australia", [("Alcohol and Drug Support Line", "0894425000", "(08) 9442 5000", "24/7. Country callers: 1800 198 024. For anyone worried about their own or someone else's alcohol or drug use.", "https://www.mhc.wa.gov.au/getting-help/helplines", ("1800198024", "1800 198 024")),
                           ("Parent and Family Drug Support Line", "0894425050", "(08) 9442 5050", "24/7. Country callers: 1800 653 203. For anyone worried about someone else's use.", "https://www.mhc.wa.gov.au/getting-help/helplines", ("1800653203", "1800 653 203"))]),
    ("Tasmania", [("Alcohol and Drug Information Service", "1800811994", "1800 811 994", "24 hours. For people who use drugs, and family members.", "https://www.health.tas.gov.au/health-topics/alcohol-and-drugs/learn-about-alcohol-and-drugs/alcohol-and-drug-treatment-and-support")]),
    ("Northern Territory", [("Alcohol and Drug Information Service (ADIS)", "1800131350", "1800 131 350", "Listed on the NT Government's 24-hour helplines page. For anyone in the NT with alcohol or drug concerns.", "https://nt.gov.au/wellbeing/mental-health/24-hour-mental-health-hotlines")]),
    ("Australian Capital Territory", [("Alcohol and Drug Service Intake, Canberra Health Services", "0251249977", "(02) 5124 9977", "Intake, weekdays 8am to 5pm (closes 3.30pm Wednesdays), excluding public holidays. Not a crisis line. After hours, call the National Alcohol and Other Drug Hotline on 1800 250 015.", "https://www.canberrahealthservices.act.gov.au/services-and-clinics/services/central-health-intake-chi")]),
]

# Helpline one-liners and "More info" lines. Checked against each service's own website on 4 Nov 2026.
# Keep to what the official page says. If something can't be verified, leave it out.
LINE_INFO = {
    "lifeline": ("24/7 crisis support for anyone in Australia who is feeling overwhelmed or finding it hard to cope.", [
        "Short-term, confidential support from a trained crisis supporter, including if you're thinking about suicide or worried about someone.",
        "Call 13 11 14, text 0477 13 11 14 or chat online. All three are open 24/7."], "https://www.lifeline.org.au/", "lifeline.org.au"),
    "beyond-blue": ("Free counselling for anxiety, depression or feeling overwhelmed, for anyone in Australia.", [
        "Counsellors listen and help you find the right mental health services. You can also call if you're supporting a partner, family member or friend.",
        "Call 1300 22 4636 or use webchat, both 24/7.",
        "Free and confidential. Local call costs apply on the phone. On webchat you don't have to give your real name."], "https://www.beyondblue.org.au/get-support/talk-to-a-counsellor", "beyondblue.org.au"),
    "suicide-call-back": ("Free 24/7 counselling for anyone affected by suicide, aged 15 and over.", [
        "For people feeling suicidal, worried about or caring for someone, or who have lost someone to suicide. Also for emotional or mental health issues.",
        "Phone and online chat are 24/7. Video chat is by appointment (18 and over).",
        "Free, for people living in Australia. No referral needed."], "https://www.suicidecallbackservice.org.au/phone-and-online-counselling/", "suicidecallbackservice.org.au"),
    "13yarn": ("Free 24/7 crisis support for Aboriginal and Torres Strait Islander people, from Aboriginal and Torres Strait Islander Crisis Supporters.", [
        "A confidential, culturally safe place to yarn if you're feeling worried or no good, or worried about someone you know.",
        "Call 13 92 76 24/7. Text 0447 13 92 76, or type to them online, 4pm to midnight every day.",
        "Free and confidential."], "https://www.13yarn.org.au/", "13yarn.org.au"),
    "qlife": ("Free, anonymous LGBTIQ+ peer support for talking about sexuality, gender, bodies, feelings or relationships.", [
        "Run by LGBTIQA+SB people. Family members, friends and others who support someone LGBTIQA+SB are welcome too.",
        "Phone or webchat, 3pm to 9pm your local time, every day including holidays. Last calls are taken by 8.40pm.",
        "Free and anonymous. Not a crisis line."], "https://qlife.org.au/", "qlife.org.au"),
    "national-aod": ("Free, confidential support for anyone worried about their own or someone else's alcohol or drug use.", [
        "Your call goes through to the alcohol and drug service in your state or territory.",
        "Open 24/7. From South Australia, the service runs 8.30am to 10pm.",
        "Free and confidential. Run by the Australian Government Department of Health, Disability and Ageing."], "https://www.health.gov.au/contacts/national-alcohol-and-other-drug-hotline", "health.gov.au"),
    "adis": ("24/7 confidential alcohol and drug support for Queenslanders and the people who care about them.", [
        "For people in Queensland with alcohol or drug concerns, their loved ones, and health professionals.",
        "Call 24/7, chat online with a counsellor, or request a call back. There's also an SMS support program."], "https://adis.health.qld.gov.au/", "adis.health.qld.gov.au"),
    "gambling": ("Free, confidential 24/7 support for anyone affected by gambling, yours or someone else's.", [
        "Talk to a trained counsellor any time, day or night, from anywhere in Australia.",
        "Gambling Help Online also has live chat and email support, free and confidential.",
        "Government funded. Not run by Gamblers Anonymous."], "https://www.gamblinghelponline.org.au/", "gamblinghelponline.org.au"),
    "aa-au": ("Talk to a sober member of Alcoholics Anonymous, any time, if drinking is a problem for you.", [
        "Call the 24-hour helpline to speak with a sober alcoholic.",
        "You can also chat live with a member on the AA website, or find an in-person or online meeting."], "https://www.aa.org.au/", "aa.org.au"),
    "na-au": ("Talk to a member of Narcotics Anonymous, or find a meeting near you.", [
        "Call 1300 652 820 to find someone to talk to. Hours aren't published.",
        "To find meetings, text your suburb or postcode and state (for example, Paddington QLD) to 0488 811 247 and you'll get a list of meetings nearby."], "https://www.na.org.au/", "na.org.au"),
    "al-anon": (None, [
        "Talk to an Al-Anon member in confidence on 1300 252 666. Hours aren't published.",
        "Support groups for family and friends of problem drinkers, plus Alateen groups for teens."], "https://al-anon.org.au/", "al-anon.org.au"),
    "fds": (None, [
        "A national support line for families and friends affected by someone's alcohol or other drug use.",
        "Open 24/7. FDS also runs support meetings in some states."], "https://www.fds.org.au/", "fds.org.au"),
}

# "More info" lines for the state and territory lines, keyed by name. Same rules as LINE_INFO.
STATE_INFO = {
    "Adis 24/7 Alcohol and Drug Support": ["Call 24/7, chat online with a counsellor, or request a call back."],
    "Alcohol and Drug Information Service (ADIS) NSW": [
        "Free, confidential counselling, information and referral from professional counsellors, for NSW residents worried about alcohol or drugs.",
        "Phone 24/7. Web chat is Monday to Friday, 8.30am to 5pm (including public holidays)."],
    "DirectLine": ["Free, confidential alcohol and drug counselling and referral in Victoria, for you or someone else.",
        "Phone or online, 24/7."],
    "Alcohol and Drug Information Service (ADIS), DASSA": [
        "Confidential telephone counselling, information and referral. Run by Drug and Alcohol Services South Australia.",
        "Every day, 8.30am to 10pm. Calling from outside SA: (08) 7087 1743, same hours."],
    "Alcohol and Drug Support Line": ["Confidential, free and anonymous, 24/7. Metro (08) 9442 5000, country 1800 198 024."],
    "Parent and Family Drug Support Line": ["For family and friends worried about someone else's alcohol or drug use.",
        "Confidential, free and anonymous, 24/7. Metro (08) 9442 5050, country 1800 653 203."],
    "Alcohol and Drug Information Service": ["24-hour phone information and counselling about the effects of alcohol and drugs, with referral to services.",
        "For people who use drugs and their family members."],
    "Alcohol and Drug Information Service (ADIS)": ["The NT Government lists this number on its 24-hour helplines page. It doesn't describe the service in more detail."],
    "Alcohol and Drug Service Intake, Canberra Health Services": ["An intake line, not a crisis line.",
        "After hours, the National Alcohol and Other Drug Hotline on 1800 250 015 is open 24/7."],
}

def domain_of(url):
    from urllib.parse import urlparse
    d = urlparse(url).netloc
    return d[4:] if d.startswith("www.") else d

def more_info(lines, url, label=None):
    items = "".join(f"<li>{E(x)}</li>" for x in lines)
    return f'<details class="more"><summary>More info</summary><ul>{items}</ul><p><a href="{E(url)}" rel="noopener">{E(label or domain_of(url))}</a></p></details>'

def line_card(line):
    note = f'<p class="small teal">{E(line["note"])}</p>' if line.get("note") else ""
    txt = f'<a class="btn ghost" href="sms:{line["textDial"]}">Text {E(line["textDisplay"])}</a>' if line.get("textDial") else ""
    one, extra, url, label = LINE_INFO[line["id"]]
    return f'<div class="card"><h3>{E(line["name"])}</h3><p class="one">{E(one)}</p><p>{E(line["detail"])}</p>{note}<div class="btn-row">{tel(line)}{txt}</div>{more_info(extra, url, label)}</div>'

# Accessibility options on Help (plan.md section 2). Each number and sentence was checked against the linked
# official page on 10 Nov 2026; statuses are in the PR. Hale checks every number before publish.
ACCESS_LINKS = {
    "triplezero": ("Triple Zero: other emergency numbers", "https://www.triplezero.gov.au/triple-zero/other-emergency-numbers"),
    "nrs-emergency": ("How to make an emergency call using the NRS", "https://www.accesshub.gov.au/about-the-nrs/how-to-make-an-emergency-call-using-the-nrs"),
    "nrs-numbers": ("NRS call numbers and links", "https://www.accesshub.gov.au/about-the-nrs/nrs-call-numbers-and-links"),
    "lifeline-access": ("Lifeline: language and accessibility support", "https://www.lifeline.org.au/get-help/services/crisis-support/language-translation-accessibility-support"),
}
AFFIL = "These are independent services. HomeCircle isn't affiliated with or endorsed by them. HomeCircle is support, not medical care."
def access_help():
    lk = lambda k: f'<a href="{E(ACCESS_LINKS[k][1])}" rel="noopener">{E(ACCESS_LINKS[k][0])}</a>'
    return f"""<div class="card sage mt" id="access"><h2 class="mt0">If you're Deaf, hard of hearing or have a speech difficulty</h2>
<p><strong>If you're Deaf, hard of hearing or have a speech communication difficulty and use a TTY, call 106 in an emergency to reach police, fire or ambulance through the National Relay Service.</strong> It's free and open 24/7. 106 works only from a TTY, not from an ordinary phone or by text message.</p>
<p>You cannot contact Triple Zero (000) by SMS. The National Relay Service has other ways to reach 000, including NRS Chat, SMS Relay, Voice Relay and NRS Captions.</p>
<div class="btn-row"><a class="btn" href="{E(ACCESS_LINKS["nrs-emergency"][1])}" rel="noopener">How to make an emergency call using the NRS</a></div>
<details class="more"><summary>More details</summary><ul>
<li>SMS Relay: text 0423 677 767. Start with 000, then say police, fire or ambulance, your name, where you are and what's happening, and end with GA. A relay officer connects you to emergency services. This is not the same as texting 000.</li>
<li>Voice Relay: call 1800 555 727, press 1, and ask for 000.</li>
<li>NRS Chat and NRS Captions have a Call 000 button.</li>
<li><strong>NRS Helpdesk</strong> (help with relay calls, not emergencies): call 1800 555 660, TTY 1800 555 630, SMS 0416 001 350, 8am to 6pm AEST, Monday to Friday.</li>
<li>Lifeline: text 0477 13 11 14, 24/7. Or use the National Relay Service and ask for 13 11 14. TTY users call 133 677, Voice Relay (Speak and Listen) users call 1300 555 727, and internet relay users connect to the NRS online.</li>
</ul>
<div class="btn-row"><a class="btn ghost" href="sms:0423677767">Text SMS Relay 0423 677 767</a><a class="btn ghost" href="tel:1800555727">Call Voice Relay 1800 555 727</a><a class="btn ghost" href="sms:0477131114">Text Lifeline 0477 13 11 14</a></div>
<ul class="plain-list link-list"><li>{lk("triplezero")}</li><li>{lk("nrs-numbers")}</li><li>{lk("lifeline-access")}</li></ul></details>
<p class="small">{AFFIL} Checked against official pages on 12 November 2026.</p></div>"""

DISABILITY_SERVICES = [  # (name, one-liner, detail, buttons [(href, label)])
    ("Disability Gateway", "Helps people with disability, their families and carers find information, services and support in Australia. Run by the Australian Government.",
     "Call 1800 643 787, Monday to Friday, 8am to 8pm AEDT/AEST. Not a crisis line.",
     [("tel:1800643787", "Call 1800 643 787"), ("https://www.disabilitygateway.gov.au/", "Open Disability Gateway")]),
    ("National Relay Service", "Phone calls for people who are deaf, hard of hearing or have a speech communication difficulty.",
     "Contact the NRS, then ask for the number you want to call. That includes any helpline on this page.",
     [("https://www.accesshub.gov.au/", "Open Access Hub"), ("https://www.accesshub.gov.au/about-the-nrs/nrs-call-numbers-and-links", "NRS call numbers")]),
    ("NDIS", "Information about the National Disability Insurance Scheme.",
     "Information only. Not a crisis line.",
     [("https://www.ndis.gov.au/", "Open ndis.gov.au")]),
    ("Blue Knot Helpline", "Trauma specialist support for adults affected by trauma or abuse in childhood, and the people supporting them.",
     "Call 1300 657 380 and press 1, 9am to 5pm AEST/AEDT, 7 days. Not a crisis service.",
     [("tel:1300657380", "Call 1300 657 380"), ("https://blueknot.org.au/survivors/blue-knot-helpline/", "Open Blue Knot")]),
]
def disability_services():
    cards = "".join(f'<div class="card"><h3>{E(n)}</h3><p class="one">{E(one)}</p><p>{E(d)}</p><div class="btn-row">'
                    + "".join(f'<a class="btn ghost" href="{E(h)}"{" rel=\"noopener\"" if h.startswith("http") else ""}>{E(l)}</a>' for h, l in b)
                    + "</div></div>" for n, one, d, b in DISABILITY_SERVICES)
    return f"""<h2 id="disability">Disability and other support</h2>
<p>For people with disability, families and carers. These aren't crisis lines. In an emergency, call 000.</p>
<div class="grid g2">{cards}</div>
<p class="small">{AFFIL} Checked against official pages on 12 November 2026. Hours and numbers can change, so check the service's own website.</p>"""

def build_help():
    lines = "".join(line_card(HL[i]) for i in H["primary"])
    al, fds, gam, ga = HL["al-anon"], HL["fds"], H["gamAnon"], H["ga"]
    def ga_contact(c):
        if c.get("phoneDial"):
            return f'<li><a href="tel:{c["phoneDial"]}">{E(c["label"])}: Call {E(c["phoneDisplay"])}</a></li>'
        return f'<li><a href="mailto:{E(c["email"])}">{E(c["label"])}: Email {E(c["email"])}</a></li>'
    ga_list = "".join(ga_contact(c) for c in ga["contacts"])
    def state_line(n, dial, disp, detail, url, *country):
        extra = f'<a class="btn ghost" href="tel:{country[0][0]}">Call {E(country[0][1])} (country)</a>' if country else ""
        return f'<div class="state-line"><h4>{E(n)}</h4><p>{E(detail)}</p><div class="btn-row"><a class="btn ghost" href="tel:{dial}">Call {E(disp)}</a>{extra}<a class="btn ghost" href="{E(url)}" rel="noopener">Open site</a></div>{more_info(STATE_INFO[n], url)}</div>'
    states = "".join(f'<details class="card state"><summary><h3>{E(st)}</h3></summary>{"".join(state_line(*l) for l in ls)}</details>' for st, ls in STATE_LINES)
    body = f"""<div id="now" class="btn-row"><a class="btn danger" href="tel:000">Call 000</a><a class="btn" href="tel:131114">Call Lifeline 13 11 14</a></div>
<h1>Get help</h1>
<p class="lede">We're here to support you. Help is always available. You're not alone.</p>
<p><strong>{E(L["notMedicalDevice"])}</strong></p>
<div class="notice"><strong>Call 000 immediately</strong> if a life is in danger. {E(HL["000"]["detail"])}</div>
{access_help()}
<h2>Helplines</h2>
<div class="grid g3">{lines}</div>
<p class="small">These are independent services. HomeCircle is not affiliated with them.</p>
{disability_services()}
<div class="card sage mt ra-skip" id="treatment"><h2 class="mt0">Looking for treatment or rehab?</h2><p>Official treatment finders, your state's alcohol and drug line, and what's free and what costs money.</p><a class="btn" href="find-treatment.html">Find treatment near you</a></div>
<div class="card sage mt ra-skip" id="before-you-drive"><h2 class="mt0">Before you drive</h2><p>Other ways home if you're not sure you're okay to drive, what alcohol and drugs can do, and official figures and limits pages.</p><a class="btn" href="before-you-drive.html">Before you drive</a></div>
<h2 id="family">Family &amp; Partners</h2>
<div class="note">This is not medical advice. For any major concern, see a local doctor or GP. If a life is in danger, call 000.</div>
<p>For partners, family members, and couples. These lines are beside someone in recovery.</p>
<div class="grid g2">
<div class="card"><h3>{E(al["name"])}</h3><p>For families and friends of someone with a drinking problem.</p><div class="btn-row">{tel(al)}<a class="btn ghost" href="https://al-anon.org.au/">Open site</a></div>{more_info(*LINE_INFO["al-anon"][1:])}</div>
<div class="card"><h3>Alateen</h3><p>Part of Al-Anon Australia, for ages about 13 to 18. Same Australian line. HomeCircle itself is an 18+ app.</p><div class="btn-row">{tel(al)}<a class="btn ghost" href="https://al-anon.org.au/">Open site</a></div></div>
<div class="card"><h3>{E(fds["name"])}</h3><p>{E(fds.get("note") or "")}</p><p class="small">{E(fds["detail"])}</p><div class="btn-row">{tel(fds)}<a class="btn ghost" href="{E(H["familyDrugSupportURL"])}">Open site</a><a class="btn ghost" href="https://www.fds.org.au/fds-meetings-events/support-meetings" rel="noopener">Find a family meeting</a></div>{more_info(*LINE_INFO["fds"][1:])}<p class="small">FDS lists no support meetings in WA, Tasmania or the NT. In WA, the Parent and Family Drug Support Line is listed under Western Australia below.</p></div>
<div class="card"><h3>{E(gam["name"])}</h3><p>{E(gam["body"])}</p><div class="btn-row"><a class="btn ghost" href="mailto:{E(gam["email"])}">Email {E(gam["email"])}</a><a class="btn ghost" href="{E(gam["url"])}">Open site</a></div></div>
</div>
<h2 id="ga">{E(ga["title"])}</h2>
<div class="card"><p>{E(ga["intro"])}</p><ul class="plain-list">{ga_list}</ul><a class="btn ghost" href="{E(ga["siteURL"])}">Open site</a></div>
<h2 id="states">Support by state and territory</h2>
<p>Alcohol and drug lines run by each state and territory. Keep 000 and Lifeline first: these lines are for advice and support, not emergencies. Checked against each service's own website on 4 November 2026.</p>
<div class="grid g2 states">{states}</div>
<div class="grid g2 mt">
<div class="card"><h3>SMART Recovery Australia</h3><p>Free weekly groups, online and in person, for any addictive behaviour, including alcohol, drugs and gambling. Run by a trained facilitator. Not a 12-step program, and not a support line.</p><a class="btn ghost" href="https://smartrecoveryaustralia.com.au/smart-recovery-meetings" rel="noopener">Find a SMART Recovery meeting</a></div>
<div class="card"><h3>Gambling help in every state</h3><p class="one">{E(LINE_INFO["gambling"][0])}</p><p>Every state and territory gambling service uses the National Gambling Helpline for 24/7 phone help.</p>{tel(HL["gambling"])}{more_info(*LINE_INFO["gambling"][1:])}</div>
</div>
<p class="small">These are independent services. HomeCircle is not affiliated with them. Hours and numbers can change, so check the service's own website.</p>
<h2>Self-help kit</h2>
<p>Tools to support you in the moment.</p>
<div class="grid g4">{tile(item_href("guide-urge"), "Urge plan", ITEMS["guide-urge"]["summary"], "Guide", "urgeWave", "")}{tile(item_href("guide-halt"), "HALT", ITEMS["guide-halt"]["summary"], "Guide", "haltPause", "")}{tile(item_href("guide-24h"), "24-hour plan", ITEMS["guide-24h"]["summary"], "Guide", "dayPlan", "")}{tile("meditations.html", "Breathe now", "An animated breathing guide.", "Breathing", "breatheOut", "")}</div>
<div class="grid g2 mt">
<div class="card"><h2 class="mt0">Keep your details private</h2><p>{E(L["privateDetails"])}</p></div>
<div class="card"><h2 class="mt0">Code of conduct</h2><p>{E(L["rulesBody"])}</p></div>
</div>
<div class="emergency-card mt"><h2 class="mt0">Call 000 immediately</h2><p>{E(HL["000"]["detail"])}</p><a class="btn" href="tel:000">Call 000</a></div>
<div class="card mt" id="overdose"><h2 class="mt0">What to do in an overdose</h2><p>Call 000 first. Then see the signs of overdose, the first aid steps, and where to get free naloxone.</p><a class="btn" href="families/overdose.html">What to do in an overdose</a></div>
<div class="card mt" id="read-to-you"><h2 class="mt0">Have this read to you</h2><p>Your phone can read any page out loud, including this one.</p><p><strong>iPhone or iPad:</strong> go to Settings &gt; Accessibility &gt; Read &amp; Speak (on older versions, Spoken Content) and turn on Speak Screen. Then swipe down with two fingers from the top of the screen, or say &ldquo;Siri, speak screen&rdquo;.</p><p><strong>Android:</strong> go to Settings &gt; Accessibility &gt; Select to Speak and turn on the Select to Speak shortcut. Tap the shortcut, then tap what you want read. If you can&rsquo;t find it, install Android Accessibility Suite from Google Play.</p></div>
<h2>More information</h2>
<p><a href="https://adf.org.au/">Alcohol and Drug Foundation</a> · <a href="https://www.healthdirect.gov.au/alcohol">Alcohol on Healthdirect</a> · <a href="https://www.gamblinghelponline.org.au/">Gambling Help Online</a></p>
<p class="small">{E(L["gpLine"])}</p>"""
    page("help.html", "help.html", "Get help – HomeCircle", "Helplines for Australia: 000, Lifeline 13 11 14, Beyond Blue, Suicide Call Back Service, 13YARN, QLife, alcohol and drug lines by state, gambling help, and family support.", body)

# ---------- find treatment near you (step 1: official finders + free vs paid explainer) ----------
# Every number, hour and claim below was checked against the linked official page on 10 Nov 2026
# (sources listed in the PR). No HomeCircle-held clinic list, no location access, no tracking.
# Step 2 (on-phone postcode search) is separate work.
COST_LABELS = ["No cost", "Medicare may cover this", "Fees apply", "Ask about costs"]  # Raven's labels, exact wording
TREAT_CHECKED = "10 November 2026"
# Hale, 10 Nov 2026: ACT hours differ across official pages. Help keeps its wording (read-aloud clip remapped help.56 -> help.64).
TREAT_DETAIL = {"Alcohol and Drug Service Intake, Canberra Health Services": "Intake line, weekdays during business hours. Check their website for current hours. Not a crisis line. After hours, call the National Alcohol and Other Drug Hotline on 1800 250 015."}
TREAT_NOTE = "HomeCircle doesn't rank, recommend or check any service, and none of them pay us. This is information only, not a referral. Costs, waitlists and services change, so confirm with the service before you go. While you wait, your state's alcohol and drug line can help. In an emergency, call 000."  # Hale's step 1 disclaimer (raven/find-treatment-page-draft.md)
# (name, who runs it, what it does, url, button label) – shown A to Z by name
TREAT_FINDERS = [
    ("Counselling Online", "Turning Point", "Free, confidential online chat counselling about alcohol and other drugs, 24/7, for you or someone you care about.", "https://www.counsellingonline.org.au/", "Open Counselling Online"),
    ("Gambling Help Online", "Gambling Help Online is funded as part of an agreement between all State and Territory Governments and the Australian Government.", "Free, confidential online counselling, live chat and email support for anyone affected by gambling, 24/7.", "https://www.gamblinghelponline.org.au/", "Open Gambling Help Online"),
    ("healthdirect Service Finder", "Healthdirect Australia", "A national directory of health services and professionals. Search by service and suburb or postcode, including for a GP who bulk-bills.", "https://www.healthdirect.gov.au/australian-health-services", "Open Service Finder"),
    ("Medicare Mental Health", "Australian Government", "Free mental health support in person, by phone or online. No referral needed. Phone 1800 595 212, weekdays 8.30am to 5pm, excluding public holidays.", "https://www.medicarementalhealth.gov.au/", "Open Medicare Mental Health"),
    ("Path2Help", "Alcohol and Drug Foundation", "Answer a few quick questions to be matched to drug and alcohol services and information for you, or someone you care about.", "https://adf.org.au/help-support/path2help/", "Open Path2Help"),
]
# (heading, label, paragraphs, links[(title, url)]) – shown A to Z by heading
TREAT_TYPES = [
    ("Community and peer groups", "No cost", [
        "Groups run by people in recovery, for people in recovery. AA says there are no dues or fees for membership; groups usually take a collection to cover costs like rent and coffee. SMART Recovery says its meetings are free.",
        "Find a group on the group's own website, or with the HomeCircle meeting finder. HomeCircle is independent and isn't affiliated with or endorsed by any of them."],
        [("Alcoholics Anonymous Australia", "https://aa.org.au/"), ("Gamblers Anonymous Australia", "https://www.gaaustralia.org.au/"), ("Narcotics Anonymous Australia", "https://www.na.org.au/multi/"), ("SMART Recovery Australia", "https://smartrecoveryaustralia.com.au/smart-recovery-meetings")]),
    ("Helplines and online counselling", "No cost", [
        "The National Alcohol and Other Drug Hotline, the National Gambling Helpline, Counselling Online and Gambling Help Online all say they're free and confidential. Many state and territory alcohol and drug lines say the same. South Australia's line charges a local call fee."],
        []),
    ("Private treatment and rehab", "Fees apply", [
        "Private residential rehabilitation services generally charge fees, which vary between providers. Some services may be partly covered by private health insurance, depending on your policy.",
        "Ask the service, and your insurer, about every cost before you start."],
        [("Drug and alcohol rehabilitation (healthdirect)", "https://www.healthdirect.gov.au/healthcare-and-services/roles-and-specialties/drug-and-alcohol-rehabilitation")]),
    ("Public and community treatment", "Ask about costs", [
        "Treatment run by state and territory health services, non-government organisations and charities. This includes counselling, withdrawal support (detox) and day programs while you live at home, and some residential programs. healthdirect says public alcohol and other drug services are usually free or low cost.",
        "Some have a waitlist. Your state's alcohol and drug line can tell you what's near you and how to get in."],
        [("Drug and alcohol rehabilitation (healthdirect)", "https://www.healthdirect.gov.au/healthcare-and-services/roles-and-specialties/drug-and-alcohol-rehabilitation")]),
    ("Your GP and Medicare", "Medicare may cover this", [
        "A GP is a good first step. They can check your health, talk through your options, and refer you to a service that suits your needs.",
        "If your GP bulk-bills, you don't pay for the visit. Not all GPs do, so ask when you book.",
        "If you also have a mental health condition, your GP, paediatrician or psychiatrist may write a mental health treatment plan. With a plan, Medicare can cover part of the cost of up to 10 individual and 10 group sessions a year with a mental health professional. They set their own fees, so Medicare usually covers only some of the cost. Checked against healthdirect on 10 November 2026."],
        [("Bulk billing (Services Australia)", "https://www.servicesaustralia.gov.au/bulk-billing"), ("Drug and alcohol rehabilitation (healthdirect)", "https://www.healthdirect.gov.au/healthcare-and-services/roles-and-specialties/drug-and-alcohol-rehabilitation"), ("Mental health treatment plan (healthdirect)", "https://www.healthdirect.gov.au/healthcare-and-services/mental-health/mental-health-treatment-plan")]),
]
TREAT_LABEL_MEANS = {
    "No cost": "The service's own website, or the government, says it's free.",
    "Medicare may cover this": "Medicare may pay some or all of it, for example a bulk-billed GP visit. Check before you go.",
    "Fees apply": "Expect to pay. Private health insurance may help, depending on your policy.",
    "Ask about costs": "Costs vary, or the source doesn't say. Ask the service before you start.",
}

def cost_tag(label):
    assert label in COST_LABELS, label
    return f'<span class="tag cost">{E(label)}</span>'

# "More details" on each card (LJ, 10 Nov 2026). Cleared card wording above stays as it is; new text is only inside
# <details class="more">. Every link was opened on 10 Nov 2026 (statuses in the PR). (lines, [(title, url)])
TREAT_MORE = {
    "Counselling Online": (["Counselling Online also links to each state and territory's alcohol and drug information."],
        [("Help in your state (Counselling Online)", "https://www.counsellingonline.org.au/help-in-your-state"), ("Self-assessment (Counselling Online)", "https://www.counsellingonline.org.au/find-support/self-assessment")]),
    "Gambling Help Online": (["For phone help, call the National Gambling Helpline on 1800 858 858, free and confidential, 24/7."],
        [("Local support services (Gambling Help Online)", "https://www.gamblinghelponline.org.au/local-support-services"), ("Assess your gambling (Gambling Help Online)", "https://www.gamblinghelponline.org.au/tools-resources/self-assessments/assess-your-gambling")]),
    "healthdirect Service Finder": (["You can also start with a guided search."],
        [("Find a GP near you (healthdirect)", "https://www.healthdirect.gov.au/australian-health-services/guided-search/general-practice"), ("Find an urgent care service near you (healthdirect)", "https://www.healthdirect.gov.au/australian-health-services/guided-search/urgent-care")]),
    "Medicare Mental Health": (["Medicare Mental Health Centres are local centres where you can talk with mental health professionals. You can walk in or make an appointment."],
        []),
    "Path2Help": (["The Alcohol and Drug Foundation's help and support page has more ways to get help."],
        [("Help and support (Alcohol and Drug Foundation)", "https://adf.org.au/help-support/")]),
    "Community and peer groups": (["Family and friends have their own groups too."],
        [("Al-Anon Family Groups Australia", "https://al-anon.org.au/"), ("Family Drug Support meetings", "https://www.fds.org.au/fds-meetings-events/support-meetings")]),
    "Helplines and online counselling": ([],
        [("National Alcohol and Other Drug Hotline (health.gov.au)", "https://www.health.gov.au/contacts/national-alcohol-and-other-drug-hotline"), ("Counselling Online", "https://www.counsellingonline.org.au/"), ("Gambling Help Online", "https://www.gamblinghelponline.org.au/")]),
    "Private treatment and rehab": ([],
        [("Private health insurance (healthdirect)", "https://www.healthdirect.gov.au/healthcare-and-services/costs-and-financial-support/private-health-insurance"), ("PrivateHealth.gov.au", "https://www.privatehealth.gov.au/")]),
    "Public and community treatment": ([],
        [("Addiction withdrawal (healthdirect)", "https://www.healthdirect.gov.au/healthy-living/addiction/addiction-withdrawal"), ("Help in your state (Counselling Online)", "https://www.counsellingonline.org.au/help-in-your-state")]),
    "Your GP and Medicare": ([],
        [("Talking to your doctor (GP) about mental health (healthdirect)", "https://www.healthdirect.gov.au/healthy-living/emotional-wellbeing/talking-to-your-doctor-gp-about-mental-health"), ("What is Medicare? (healthdirect)", "https://www.healthdirect.gov.au/healthcare-and-services/costs-and-financial-support/what-is-medicare")]),
}
def treat_more(name):
    lines, links = TREAT_MORE[name]
    ps = "".join(f"<p>{E(x)}</p>" for x in lines)
    ls = "".join(f'<li><a href="{E(u)}" rel="noopener">{E(t)}</a></li>' for t, u in links)
    return f'<details class="more"><summary>More details<span class="sr-only">: {E(name)}</span></summary>{ps}{f"<ul class=\"plain-list link-list\">{ls}</ul>" if ls else ""}</details>'

def build_treatment():
    finders = "".join(
        f'<div class="card finder"><h3 class="mt0">{E(n)}</h3>{f'<p class="small teal">{E(who)}</p>' if who else ''}<p>{E(what)}</p><a class="btn ghost" href="{E(u)}" rel="noopener">{E(btn)}</a>{treat_more(n)}</div>'
        for n, who, what, u, btn in sorted(TREAT_FINDERS, key=lambda f: f[0].lower()))
    def type_card(h, label, paras, links):
        ps = "".join(f"<p>{E(p)}</p>" for p in paras)
        ls = "".join(f'<li><a href="{E(u)}" rel="noopener">{E(t)}</a></li>' for t, u in sorted(links, key=lambda l: l[0].lower()))
        extra = '<div class="btn-row"><a class="btn ghost" href="meetings.html">HomeCircle meeting finder</a></div>' if h == "Community and peer groups" else ""
        return f'<div class="card">{cost_tag(label)}<h3 class="mt0">{E(h)}</h3>{ps}{f'<ul class="plain-list link-list">{ls}</ul>' if ls else ""}{extra}{treat_more(h)}</div>'
    types = "".join(type_card(*t) for t in sorted(TREAT_TYPES, key=lambda t: t[0].lower()))
    legend = "".join(f"<li>{cost_tag(l)} {E(TREAT_LABEL_MEANS[l])}</li>" for l in COST_LABELS)
    def st_line(n, dial, disp, detail, url, *country):
        extra = f'<a class="btn ghost" href="tel:{country[0][0]}">Call {E(country[0][1])} (country)</a>' if country else ""
        detail = TREAT_DETAIL.get(n, detail)
        return f'<div class="state-line"><h4>{E(n)}</h4><p>{E(detail)}</p><div class="btn-row"><a class="btn ghost" href="tel:{dial}">Call {E(disp)}</a>{extra}<a class="btn ghost" href="{E(url)}" rel="noopener">Open site<span class="sr-only">: {E(n)}</span></a></div></div>'
    states = "".join(f'<details class="card state"><summary><h3>{E(st)}</h3></summary>{"".join(st_line(*l) for l in sorted(ls, key=lambda l: l[0].lower()))}</details>'
                     for st, ls in sorted(STATE_LINES, key=lambda s: s[0]))
    aod, gam = HL["national-aod"], HL["gambling"]
    body = f"""<div id="now" class="btn-row"><a class="btn danger" href="tel:000">Call 000</a><a class="btn" href="tel:131114">Call Lifeline 13 11 14</a></div>
<h1>Find treatment near you</h1>
<p class="lede">You don't have to work this out alone. Here's where to find alcohol, drug and gambling treatment in Australia, and what it might cost.</p>
<p><strong>{E(L["notMedicalDevice"])}</strong> {E(L["gpLine"])}</p>
<div class="notice"><strong>In an emergency, call <a href="tel:000">000</a>.</strong> If you need to talk to someone now, call Lifeline on <a href="tel:131114">13 11 14</a>, 24 hours a day.</div>
<div class="card sage mt" id="hotline"><h2 class="mt0">Not sure where to start?</h2>
<p>Call the National Alcohol and Other Drug Hotline on <strong>{E(aod["displayNumber"])}</strong>. It's free and confidential, 24 hours a day, 7 days a week, and puts you through to the alcohol and drug service in your state or territory. If you call from South Australia, it's answered from 8.30am to 10pm.</p>
<div class="btn-row"><a class="btn" href="tel:{aod["dial"]}">Call {E(aod["displayNumber"])}</a></div>
<p class="small">For gambling, call the National Gambling Helpline on <a href="tel:{gam["dial"]}">{E(gam["displayNumber"])}</a>, free and confidential, 24/7.</p></div>
<h2 id="finders">Official finders</h2>
<p>HomeCircle doesn't keep its own list of clinics. These official services help you find treatment and support near you. Each one is free to use. The services they list may charge, so check with them.</p>
<div class="grid g3">{finders}</div>
<h2 id="costs">Free or paid? What help costs</h2>
<p>Some help is free, some is covered by Medicare, and some charges fees. We use these labels. We don't show prices, because they change and we can't check them.</p>
<div class="card"><ul class="plain-list cost-legend">{legend}</ul></div>
<div class="grid g2 mt">{types}</div>
<h2 id="states">Alcohol and drug lines by state and territory</h2>
<p>Free advice, counselling and referral to treatment in your state or territory. They're not emergency services. Keep 000 and Lifeline first.</p>
<div class="grid g2 states">{states}</div>
<p class="small">More lines, including family support, are on the <a href="help.html">Help page</a>.</p>
<div class="card mt"><h2 class="mt0">Please note</h2><p>{E(TREAT_NOTE)}</p><p>The services and finders on this page are run by others. HomeCircle isn't affiliated with or endorsed by any of them.</p><p class="small">Checked against each service's own website on {TREAT_CHECKED}. Hours and numbers can change, so check the service's own website.</p></div>
<div class="emergency-card mt"><h2 class="mt0">Call 000 immediately</h2><p>{E(HL["000"]["detail"])}</p><a class="btn" href="tel:000">Call 000</a></div>"""
    page("find-treatment.html", "", "Find treatment near you – HomeCircle",
         "Free and fee-based alcohol, drug and gambling help in Australia, with official treatment finders and every state and territory line.", body)

def build_support():
    src = support_faq()
    body = f"""<h1>HomeCircle Support</h1>
<p class="lede">Help with the HomeCircle website and app, and how to contact us.</p>
<div class="notice"><strong>In crisis or need help now?</strong> HomeCircle is not an emergency service. Call <a href="tel:000">000</a> in an emergency, or Lifeline on <a href="tel:131114">13 11 14</a>. <a href="help.html">More helplines</a>.</div>
<h2>Contact us</h2>
<div class="card"><p>Email: <a href="mailto:{L["supportEmail"]}">{L["supportEmail"]}</a></p><p>Please include whether you're using the website or the app, your device, and a short description of the issue. We aim to reply within 24 hours. This is a goal, not a guarantee. This email is not a crisis line.</p></div>
<h2 id="website">About this website</h2>
<h3>Do I need an account?</h3><p>No. The website has no accounts and no sign-in, and everything on it is free.</p>
<h3>Does the website collect my data?</h3><p>No. There are no cookies, no ads, no trackers, no analytics and no third-party scripts or fonts. Nothing you type or save is sent to HomeCircle.</p>
<h3>What does the website save, and where?</h3><p>Only what you choose to save: your day count, journal notes, health safety answers, the breath-hold setting, Kai's chat and where you put Kai on the screen. These are kept only in this browser's local storage, on this device. They aren't sent to us, and they aren't shared with the app or your other devices. Private browsing, clearing your browser data or using another browser removes them or starts fresh. You can delete everything on <a href="your-circle.html#delete">Your circle</a>. If you use <strong>Read aloud</strong>, your device downloads that page's recordings from this website (the Help page is about 8 MB). See the <a href="{PRIVACY}">privacy policy</a>.</p><p>If you tell Kai whether a breathing exercise or other tool helped, that answer is kept only in this browser. It isn't sent to us or anyone else. You can delete it by clearing this site's data in your browser.</p>
<h3>How does the meeting finder work?</h3><p>Your browser downloads the same public meeting list the app uses, from GitHub Pages, and searches it on your computer. What you type isn't sent anywhere. <strong>Near me</strong> only asks for your location when you press it, and your location stays on the page. The site and the list are hosted on GitHub Pages, which, like any web host, receives normal web requests.</p>
{KAI_FAQ}
<h3 id="accessibility">Can I use the website with a screen reader, larger text or less motion?</h3><p>{E(A["SITE"]["safeLine"])} Email <a href="mailto:{L["supportEmail"]}">{L["supportEmail"]}</a>. You don't need to tell us anything about your health or disability. Breathing guides have a pause button, a slower pace and a text count instead of the moving circle. Practices like <a href="library/mindful-walking.html">mindful moving</a> have seated, wheelchair and lying-down versions anyone can choose.</p>
<h3>How do meeting reminders work on the website?</h3><p>On a meeting, choose <strong>Add reminder</strong>, then <strong>Just this one</strong> or <strong>Every week</strong>. Your browser downloads a calendar file (.ics). Open it with your calendar app to add the meeting, with an alert set for 2 hours before it starts. The website sends no notifications and keeps no list of your reminders; to remove one, delete it in your calendar.</p>
<h3>Spotted a wrong meeting or event?</h3><p>Meetings and events come from AA and NA's own public listings. Please tell the group or the fellowship, and email us too so we know.</p>
<h2>The iPhone app</h2>
{updates_html()}
{src}
<h2>Privacy and terms</h2><p>Read the <a href="{PRIVACY}">App Privacy Policy</a> and <a href="{TERMS}">Terms of Use</a>. {E(BROWSER_ONLY)}</p>"""
    page("support.html", "support.html", "Support – HomeCircle", "Get help with HomeCircle: contact, FAQs about the website and app, and crisis support.", body)


# ---------- your circle (browser-only day count, journal, health safety) ----------
HEALTH_TOGGLES = [("heartOrBloodPressure", "Heart condition or blood pressure"), ("asthmaOrLung", "Asthma or a lung condition"),
                  ("epilepsy", "Epilepsy or seizures"), ("pregnancy", "Pregnancy"), ("panicAttacks", "Panic attacks"),
                  ("traumaOrPTSD", "Trauma or PTSD"), ("recentDetox", "Recent detox or withdrawal")]
JOURNAL_PROMPTS = ["What helped today?", "What am I grateful for?", "What was hard, and who can I tell?", "One thing for the next 24 hours."]
MOODS = ["Grateful", "Steady", "Heavy", "Hopeful"]

def build_circle():
    r = ""
    toggles = "".join(f'<label class="check"><input type="checkbox" data-health="{k}"> {E(t)}</label>' for k, t in HEALTH_TOGGLES)
    prompts = "".join(f'<option>{E(x)}</option>' for x in JOURNAL_PROMPTS)
    moods = "".join(f'<option>{E(x)}</option>' for x in MOODS)
    body = f"""<h1>Your circle</h1>
<p class="lede">A day counter, a private journal and health safety notes, if you'd like them. All optional.</p>
<div class="notice"><strong>Stored only in this browser.</strong> Anything you save on this page stays in this browser's local storage, on this device. It isn't sent to HomeCircle or anyone else, and it isn't shared with the app or your other devices. Private browsing or clearing your browser data removes it. On a shared or public computer, anyone using this browser could read it, including your journal and health answers. Use private browsing, or tap Clear everything on this browser when you're done.</div>
<p class="notice" data-storage-check hidden>This browser isn't letting the site save anything (it may be in private mode or have storage turned off). You can still use the page, but nothing will be kept.</p>
<div class="grid g2">
<section class="card" aria-labelledby="days-h"><h2 class="mt0" id="days-h">Day count</h2>
<p class="day-count" id="day-count" aria-live="polite">Set a sober date when you want a day count.</p>
<form id="sober-form" class="form-row"><div><label for="sober-date">Sober date</label><input type="date" id="sober-date" required></div><div class="btn-row"><button class="btn" type="submit">Save date</button><button class="btn ghost" type="button" id="sober-clear" hidden>Remove date</button></div></form>
<p class="small">Day 1 is your sober date itself, as in the app. The day count is kept in this browser only.</p></section>
<section class="card sage" id="health" aria-labelledby="health-h"><h2 class="mt0" id="health-h">Health safety</h2>
<p>Always talk to your doctor. This is not medical advice. Answers stay in this browser.</p>
<fieldset><legend class="sr-only">Health notes</legend>{toggles}</fieldset>
<label class="check strong"><input type="checkbox" data-health="hideHolds"> Hide breath holds</label>
<p class="small" data-holds-status aria-live="polite"></p>
<p class="small">{E(L["breathHold"])} If you tick heart or blood pressure, a lung condition, pregnancy or panic attacks, HomeCircle hides breath holds and offers the slow out-breath instead, as the app does.</p></section>
</div>
<section aria-labelledby="journal-h"><h2 id="journal-h">A private journal, just for you</h2>
<form class="card" id="journal-form">
<div class="form-row"><div><label for="j-prompt">Prompt</label><select id="j-prompt" name="prompt"><option value="">No prompt</option>{prompts}</select></div>
<div><label for="j-mood">Mood (optional)</label><select id="j-mood" name="mood"><option value="">None</option>{moods}</select></div></div>
<label for="j-title">Title (optional)</label><input type="text" id="j-title" name="title" maxlength="120">
<label for="j-body">Your note</label><textarea id="j-body" name="body" rows="5" maxlength="5000" required></textarea>
<div class="btn-row"><button class="btn" type="submit">Save in this browser</button></div>
<p class="small" id="journal-status" role="status"></p>
<p class="small">{E(L["privateDetails"])}</p>
</form>
<p id="journal-empty">No notes yet.</p>
<ul class="journal-list" id="journal-list"></ul></section>
<section class="card mt" id="delete" aria-labelledby="del-h"><h2 class="mt0" id="del-h">Delete your data in this browser</h2>
<p>This removes your journal, sober date, health answers, Kai chat and Kai's position from this browser. It can't be undone, and HomeCircle doesn't hold a copy.</p>
<button class="btn danger" type="button" id="delete-all">Clear everything on this browser</button></section>
<p class="small mt">{E(L["gpLine"])} In an emergency call <a href="tel:000">000</a>, or Lifeline on <a href="tel:131114">13 11 14</a>.</p>"""
    page("your-circle.html", "your-circle.html", "Your circle – HomeCircle", "An optional day counter, private journal and health safety notes, stored only in your browser.", body)

# ---------- Kai data for the in-browser engine ----------
def build_kai_data():
    import json as _j
    pages = {i["id"]: f"library/{SLUG[i['id']]}.html" for i in C["items"] if i["id"] in SLUG}
    pages.update({"page-twelve-steps": "twelve-steps.html", "page-body-stages": STAGES_HREF, "page-recovery-books": BOOKS_HREF})
    data = {
        "items": {i["id"]: {"title": i["title"], "kind": i["kind"]} for i in C["items"]},
        "steps": {str(t["number"]): {"theme": t["theme"], "note": t["note"]} for t in C["twelveSteps"]},
        "stages": [{"days": st["days"], "kaiLine": st["kaiLine"], "statID": st.get("statID")} for st in C["stages"]],
        "stats": {st["id"]: {"text": st["text"], "sourceTitle": st["sourceTitle"], "sourceURL": st["sourceURL"]} for st in C["stats"]},
        "safetyLine": C["stageCopy"]["safetyLine"],
        "privateDetails": L["privateDetails"],
        "pages": pages,
    }
    (ROOT / "assets" / "kai-data.js").write_text("/* Generated by tools/build.py from the app's content. Do not edit. */\nself.HCKaiData = " + _j.dumps(data, ensure_ascii=False, separators=(",", ":")) + ";\n")


# ---------- before you drive ----------
DRIVE = json.loads((ROOT / "before-you-drive.json").read_text())
DRIVE_LIMITS = [  # official limits and drug-driving pages; link only, do not restate as advice
    ("Australian Capital Territory — drink and drug driving", "https://www.cityservices.act.gov.au/roads-and-paths/road-safety/drink-and-drug-driving"),
    ("New South Wales — alcohol limits, drugs and medicines", "https://www.nsw.gov.au/driving-boating-and-transport/roads-safety-and-rules/safe-driving/alcohol-and-drugs"),
    ("New South Wales — alcohol and driving (Transport for NSW)", "https://www.transport.nsw.gov.au/roadsafety/topics-tips/alcohol"),
    ("Northern Territory — alcohol, drugs and driving", "https://nt.gov.au/driving/safety/alcohol-drugs-and-driving"),
    ("Queensland — alcohol limits", "https://www.qld.gov.au/transport/safety/road-safety/drink-driving/blood-alcohol"),
    ("Queensland — drugs and driving", "https://www.qld.gov.au/transport/safety/road-safety/drink-driving/drugs"),
    ("South Australia — Driver's Handbook, alcohol and drugs", "https://www.mylicence.sa.gov.au/road-rules/the-drivers-handbook/alcohol-drugs"),
    ("Tasmania — driving under the influence", "https://rsac.tas.gov.au/driving-under-the-influence/"),
    ("Victoria — alcohol and driving laws", "https://transport.vic.gov.au/road-and-active-transport/road-rules-and-safety/alcohol-drugs-and-driving/alcohol-and-driving-laws"),
    ("Victoria — drugs and driving laws", "https://transport.vic.gov.au/road-rules-and-safety/alcohol-drugs-and-driving/drugs-and-driving-laws"),
    ("Western Australia — drink and drug driving", "https://www.wa.gov.au/organisation/road-safety-commission/drink-and-drug-driving"),
]
DRIVE_AFFIL = "These are independent official pages. HomeCircle is not affiliated with them."

def drive_figures():
    cards = []
    for fig in DRIVE["figures"]:
        words = "".join(f"<p>{E(w)}</p>" for w in fig["wording"])
        note = f'<p class="small">{E(fig["note"])}</p>' if fig.get("note") else ""
        period = f'<p class="small">{E("Period: " + fig["period"])}</p>' if fig.get("period") else ""
        cards.append(
            f'<div class="card" id="{E(fig["id"])}"><h3 class="mt0">{E(fig["title"])}</h3>{words}{note}{period}'
            f'<p class="small">{E("Source: " + fig["source"])} <a href="{E(fig["url"])}" rel="noopener">Open the official page</a>. '
            f'{E("Checked on " + fig["checkedOn"] + ".")}</p></div>'
        )
    return '<div class="grid g2">' + "".join(cards) + "</div>"

def build_drive():
    limits = "".join(
        f'<li><a href="{E(u)}" rel="noopener">{E(n)}</a></li>'
        for n, u in sorted(DRIVE_LIMITS, key=lambda x: x[0].lower())
    )
    body = f"""<div id="now" class="btn-row"><a class="btn danger" href="tel:000">Call 000</a><a class="btn" href="tel:131114">Call Lifeline 13 11 14</a></div>
<h1>Before you drive</h1>
<p class="lede">If you're not sure you're okay to drive, pause and use another way home. Feeling fine is not the same as being safe to drive.</p>
<div class="card sage" id="alternatives"><h2 class="mt0">Other ways home</h2>
<p>If you're not sure, you don't have to drive.</p>
<ul>
<li>A taxi or rideshare</li>
<li>Call someone</li>
<li>Wait until you're sure, or don't drive today</li>
<li>Public transport</li>
</ul></div>
<h2>What alcohol and drugs can do</h2>
<p>Alcohol affects judgement, vision, coordination and reflexes, and increases the risk of crashing. Drinking slows your reaction time, blurs your vision and makes it hard to judge things like speed and distance. It can also slow your brain so that you can't respond to situations, make decisions or react quickly, reduce your ability to judge your speed or distance from other objects, give you a false sense of confidence, make it harder to do more than one thing at a time, make you drowsy, and affect your sense of balance.</p>
<p>Different people process alcohol differently. You can still be over the limit the next morning. Being under the limit doesn't mean you're safe to drive. As there's no easy way to know that you are okay to drive after drinking, the only way to be sure is to not drink alcohol if you are going to drive.</p>
<p>Drugs can affect your judgement, vision, coordination and reflexes—all of which increase your risk of having a crash. Official pages also list a reduced ability to judge distance and speed, reduced coordination and concentration, and blurred vision.</p>
<p class="small">This wording comes from official Australian road-safety pages: <a href="https://streetsmarts.initiatives.qld.gov.au/drink-driving/get-the-facts/" rel="noopener">Queensland StreetSmarts on drink driving</a>, <a href="https://streetsmarts.initiatives.qld.gov.au/drug-driving/" rel="noopener">Queensland StreetSmarts on drug driving</a>, <a href="https://www.qld.gov.au/transport/safety/road-safety/drink-driving/drugs" rel="noopener">Queensland's drugs and driving page</a>, <a href="https://www.transport.nsw.gov.au/roadsafety/topics-tips/alcohol" rel="noopener">Transport for NSW</a> and <a href="https://transport.vic.gov.au/road-and-active-transport/road-rules-and-safety/alcohol-drugs-and-driving/alcohol-and-driving-laws" rel="noopener">Transport Victoria</a>.</p>
<h2>The figures</h2>
<p>These figures are worded as their official sources word them. They were checked on 12 November 2026. They are not a complete picture for every state and territory.</p>
{drive_figures()}
<p class="small">{DRIVE_AFFIL}</p>
<h2>Questions to ask yourself</h2>
<p>If you're deciding whether to drive, you might ask yourself:</p>
<ul>
<li>Do I feel fine, or am I actually fine to drive?</li>
<li>Would I be happy for someone I care about to be in the car with me right now?</li>
<li>Is there another way home tonight?</li>
<li>If something happened on the drive, would it be worth having on my conscience?</li>
</ul>
<h2>Medicines</h2>
<p>Some prescription and over-the-counter medicines can affect driving. Ask your doctor or pharmacist if you're unsure.</p>
<p class="small">From <a href="https://www.healthdirect.gov.au/medicines-and-driving" rel="noopener">healthdirect, Medicines and driving</a>. Checked on 12 November 2026. This is an independent official page.</p>
<h2>Official limits and drug-driving pages</h2>
<p>Limits and rules differ across Australia, and they can change. Check the official page for your state or territory. HomeCircle doesn't restate these as advice.</p>
<ul class="plain-list link-list">{limits}</ul>
<p class="small">{DRIVE_AFFIL}</p>
<div class="card sage" id="support-not-medical"><h2 class="mt0">Support, not medical care</h2>
<p>{E(L["gpLine"])} {E(L["notMedicalDevice"])}</p>
<p>For alcohol or other drug support, call the National Alcohol and Other Drug Hotline on <a href="tel:1800250015">1800 250 015</a>. In an emergency, call <a href="tel:000">000</a>. For crisis support, call Lifeline on <a href="tel:131114">13 11 14</a>.</p></div>"""
    page("before-you-drive.html", "", "Before you drive – HomeCircle",
         "If you're not sure you're okay to drive, here are other ways home, what alcohol and drugs can do, official figures, and limits pages for each state and territory.",
         body)


build_kai_data(); build_circle()
build_home(); build_library(); build_steps(); build_meditations(); build_meetings(); build_help(); build_treatment(); build_drive(); build_support()
for i in C["items"]:
    build_item(i)
build_stages(); build_books()
import sys; sys.path.insert(0, str(ROOT / "tools")); import families; families.build(page, E)
_ra_missing = RA.check(REGION, RA.current_lines(REGION, RA_HELP_BODY))   # fails the build on any text/clip mismatch
import subprocess as _sp
if _sp.run([sys.executable, str(ROOT / 'tools' / 'ra_loudness.py')]).returncode: sys.exit('read-aloud loudness check FAILED')
if _ra_missing: print("read aloud: lines without a clip:", ", ".join(_ra_missing))

def write_robots_and_sitemap():
    """Public SEO files. Allow crawlers; disallow tools/ and README.md. Never add noindex."""
    (ROOT / "robots.txt").write_text(
        "User-agent: *\nAllow: /\nDisallow: /tools/\nDisallow: /README.md\n\nSitemap: https://homecircle.au/sitemap.xml\n",
        encoding="utf-8",
    )
    import datetime as _dt
    today = _dt.date.today().isoformat()
    urls = sorted(set(BUILT_PAGES))
    body = "".join(
        f"  <url>\n    <loc>{canonical_url(p)}</loc>\n    <lastmod>{today}</lastmod>\n  </url>\n"
        for p in urls
    )
    (ROOT / "sitemap.xml").write_text(
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
        + body
        + "</urlset>\n",
        encoding="utf-8",
    )

write_robots_and_sitemap()
print("built", len(set(BUILT_PAGES)), "pages; robots.txt + sitemap.xml")
