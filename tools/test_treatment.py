#!/usr/bin/env python3
"""Find treatment near you (step 1). python3 tools/test_treatment.py
Checks the built page has 000, Lifeline, the National AOD Hotline and Raven's four cost labels,
that every finder and outside link is https, lists are A to Z, there are no prices, rankings,
location access, trackers or third-party scripts, and that Help and every footer link to it."""
import glob, os, re, sys
from html import unescape as html_unescape
from html.parser import HTMLParser

root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.chdir(root)
fails = 0
def ok(cond, msg):
    global fails
    print(("ok " if cond else "FAIL ") + msg)
    if not cond: fails += 1

class P(HTMLParser):
    def __init__(s):
        super().__init__(); s.links = []; s.scripts = []; s.text = []; s.skip = 0; s.stack = []
        s.finders = []; s.in_finder = 0; s.h3 = None; s.types = []; s.states = []; s.tags = []; s._tag = None; s.in_states = False
    def handle_starttag(s, t, a):
        a = dict(a); cls = (a.get("class") or "").split()
        if t in ("script", "style"): s.skip += 1
        if t == "script": s.scripts.append(a.get("src"))
        if t == "a" and a.get("href"): s.links.append((a["href"], cls))
        if t == "div" and "finder" in cls: s.in_finder = 1
        if t == "div" and "states" in cls: s.in_states = True
        if t == "span" and "cost" in cls: s._tag = ""
        if t in ("h3",): s.h3 = ""
    def handle_endtag(s, t):
        if t in ("script", "style") and s.skip: s.skip -= 1
        if t == "span" and s._tag is not None: s.tags.append(s._tag.strip()); s._tag = None
        if t == "h3" and s.h3 is not None:
            h = s.h3.strip(); s.h3 = None
            if s.in_finder: s.finders.append(h); s.in_finder = 0
            elif s.in_states: s.states.append(h)
            elif s.tags and len(s.types) < len(s.tags): s.types.append(h)
        if t == "h2": s.in_states = False
    def handle_data(s, d):
        if s.skip: return
        s.text.append(d)
        if s._tag is not None: s._tag += d
        if s.h3 is not None: s.h3 += d

src = open("find-treatment.html", encoding="utf-8").read()
p = P(); p.feed(src)
main = src[src.find('<main id="main">'):src.find("</main>")]
m = P(); m.feed(main)
text = re.sub(r"\s+", " ", "".join(m.text))
hrefs = [h for h, _ in m.links]

# crisis and hotline
ok("tel:000" in hrefs and "Call 000" in text, "Call 000 button")
ok("tel:131114" in hrefs and "Lifeline" in text and "13 11 14" in text, "Lifeline 13 11 14 button")
ok("tel:1800250015" in hrefs and "National Alcohol and Other Drug Hotline" in text and "1800 250 015" in text, "National Alcohol and Other Drug Hotline 1800 250 015")
ok(main.find("tel:000") < main.find("<h1"), "000 and Lifeline come before the heading")
ok("HomeCircle is support, not medical care." in text, "support, not medical care")
ok("isn't affiliated with or endorsed by" in text, "no implied affiliation line")
ok('id="help-pill"' in src and src.find('id="help-pill"') < src.find('<main id="main">'), "Help pill on the page, before main")

# Raven's four cost labels, exact wording
LABELS = ["No cost", "Medicare may cover this", "Fees apply", "Ask about costs"]
for l in LABELS: ok(l in m.tags, f"cost label present: {l}")
ok(set(m.tags) <= set(LABELS), f"only Raven's cost labels are used ({sorted(set(m.tags) - set(LABELS))})")
ok(not re.search(r"\$\s?\d|\bAUD\b|\bper (night|week|day)\b", text), "no specific prices")
ok(not re.search(r"\b(best|top[- ]rated|accredited)\b|#1\b", text, re.I), "no 'best' rankings (no best/top-rated/accredited/#1)")
ok(not re.search(r"\bPaid\b", text), "never 'Paid' as a label")

# links
ext = [h for h in hrefs if h.startswith("http")]
ok(len(ext) >= 10, f"outside links found ({len(ext)})")
ok(all(h.startswith("https://") for h in hrefs if re.match(r"^[a-z]+:", h) and not h.startswith(("tel:", "sms:", "mailto:"))), "every outside link in the page is https")
finder_links = [h for h, c in m.links if "btn" in c and h.startswith("http")]
ok(finder_links and all(h.startswith("https://") for h in finder_links), "every finder button is https")
ok(not any(h.startswith("http://") for h, _ in p.links), "no http:// links anywhere on the page")

# A to Z
ok(len(m.finders) >= 5 and m.finders == sorted(m.finders, key=str.lower), f"finders A to Z: {m.finders}")
ok(m.types == sorted(m.types, key=str.lower) and len(m.types) == len(m.tags) - 4, f"cost types A to Z: {m.types}")
ok(len(m.states) == 8 and m.states == sorted(m.states), f"states A to Z: {m.states}")

# privacy: no tracking, third-party scripts or location
ok(all(s and not s.startswith(("http:", "https:", "//")) for s in p.scripts if s is not None), "no third-party scripts")
ok("geolocation" not in src and "navigator.geolocation" not in src, "no location access")
ok(not re.search(r"googletagmanager|google-analytics|gtag\(|fbq\(|plausible|matomo|hotjar", src, re.I), "no trackers")
ok(not re.search(r"<iframe|maps\.google|api\.mapbox", src, re.I), "no embedded maps or iframes")

# linked from Help and every page's footer
helpsrc = open("help.html", encoding="utf-8").read()
ok('href="find-treatment.html"' in helpsrc, "Help page links to Find treatment near you")
pages = sorted(glob.glob("*.html") + glob.glob("library/*.html") + glob.glob("families/*.html"))
missing = [f for f in pages if not re.search(r'href="(\.\./)?find-treatment\.html">Find treatment near you<', open(f, encoding="utf-8").read())]
ok(not missing, f"footer link on every page ({len(pages)} pages; missing: {missing})")
ok("https://homecircle.au/find-treatment.html" in open("sitemap.xml").read(), "in sitemap.xml")

# Hale/Iris edits, 10 Nov 2026
ACT = "Intake line, weekdays during business hours. Check their website for current hours. Not a crisis line. After hours, call the National Alcohol and Other Drug Hotline on 1800 250 015."
ok(ACT in text, "ACT line uses Hale's hours wording")
note = re.search(r'<h2 class="mt0">Please note</h2>(.*?)</div>', main, re.S)
note_t = re.sub(r"\s+", " ", html_unescape(re.sub(r"<[^>]+>", " ", note.group(1)))) if note else ""
AFF = "The services and finders on this page are run by others. HomeCircle isn't affiliated with or endorsed by any of them."
ok(AFF in note_t and note_t.count("affiliated") == 1, "Please note has exactly one affiliation sentence (Hale's)")
ok("none of them pay us" in note_t and "doesn't rank, recommend or check any service" in note_t, "Please note keeps Hale's step 1 disclaimer")
ok("Porn" not in text and "These are independent services" not in note_t, "no PAA mention or old affiliation line in the page body")
ok("Gambling Help Online is funded as part of an agreement between all State and Territory Governments and the Australian Government." in text and "Linked by the Department" not in text, "Gambling Help Online funding line quoted from its own About us page")
DESC = "Free and fee-based alcohol, drug and gambling help in Australia, with official treatment finders and every state and territory line."
ok(all(f'{k}="{n}" content="{DESC}"' in src for k, n in (("name", "description"), ("property", "og:description"), ("name", "twitter:description"))), "meta, og and twitter descriptions")
ok("act.gov.au/health/drugs-alcohol" not in src, "GP card uses national healthdirect source, not the ACT page")
ok("your GP, paediatrician or psychiatrist may write a mental health treatment plan" in src, "GP card: plan can be written by a GP, paediatrician or psychiatrist")
ok("Medicare can cover part of the cost of up to 10 individual and 10 group sessions a year" in src, "GP card: 10 individual and 10 group sessions")
ok("Checked against healthdirect on 10 November 2026." in src, "GP card: checked against healthdirect on 10 November 2026")

print(f"{'FAILED' if fails else 'passed'}: {fails} failure(s)")
sys.exit(1 if fails else 0)
