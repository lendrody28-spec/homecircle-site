#!/usr/bin/env python3
"""Before you drive. python3 tools/test_before_you_drive.py
Every figure in before-you-drive.json must have a link and a checked-on date.
The built page must use Hale's cleared wording, keep 000 and Lifeline above the h1,
and stay free of shame labels and brand names.
"""
import glob, json, os, re, sys
from html import unescape as html_unescape
from html.parser import HTMLParser
from pathlib import Path

root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.chdir(root)
fails = 0

def ok(cond, msg):
    global fails
    print(("ok " if cond else "FAIL ") + msg)
    if not cond:
        fails += 1

data = json.loads(Path("before-you-drive.json").read_text(encoding="utf-8"))
figures = data["figures"]
ok(len(figures) == 8, "eight cleared figures")

class P(HTMLParser):
    def __init__(s):
        super().__init__(); s.text = []; s.skip = 0; s.links = []
    def handle_starttag(s, t, a):
        a = dict(a)
        if t in ("script", "style"): s.skip += 1
        if t == "a" and a.get("href"): s.links.append(a["href"])
    def handle_endtag(s, t):
        if t in ("script", "style") and s.skip: s.skip -= 1
    def handle_data(s, d):
        if not s.skip: s.text.append(d)

src = Path("before-you-drive.html").read_text(encoding="utf-8")
p = P(); p.feed(src)
text = html_unescape(re.sub(r"\s+", " ", "".join(p.text)))
main = src[src.find("<main"):src.find("</main>")]
main_p = P(); main_p.feed(main)
main_text = html_unescape(re.sub(r"\s+", " ", "".join(main_p.text)))

for fig in figures:
    ident = fig.get("id", "?")
    url = (fig.get("url") or fig.get("link") or "").strip()
    checked = (fig.get("checkedOn") or fig.get("checked-on") or fig.get("checked_on") or "").strip()
    ok(bool(url) and url.startswith("https://"), f"{ident}: has an https link")
    ok(bool(checked), f"{ident}: has a checked-on date")
    ok(url in src, f"{ident}: link is on the page")
    ok(checked in src, f"{ident}: checked-on date is on the page")
    for w in fig.get("wording") or []:
        ok(w in src, f"{ident}: wording present: {w[:80]}")

# Crisis bar above the h1
pre = src.split("<h1", 1)[0]
ok('href="tel:000"' in pre and "Call 000" in pre, "Call 000 is above the h1")
ok('href="tel:131114"' in pre and "Call Lifeline 13 11 14" in pre, "Call Lifeline is above the h1")
ok(src.find('id="now"') < src.find("<h1"), "crisis bar precedes the h1")

ok("Some prescription and over-the-counter medicines can affect driving. Ask your doctor or pharmacist if you're unsure." in src, "healthdirect medicines line")
ok("If something happened on the drive, would it be worth having on my conscience?" in src, "Hale conscience question")
ok("Do I feel fine, or am I actually fine to drive?" in src, "feel-fine question")
ok("Would I be happy for someone I care about to be in the car with me right now?" in src, "care-about question")
ok("Is there another way home tonight?" in src, "other-way-home question")
ok("Wait until you're sure, or don't drive today" in src, "Hale wait-it-out wording")
ok("Call someone" in src and "Calling someone" not in src, "Call someone (imperative)")
ok("This is an independent official page" in src, "medicines source is an independent official page")
ok(main_text.count("HomeCircle is not affiliated with them") == 2, "affiliation line only after the figures and the limits list")
ok('id="kai"' not in src and "kai-bubble" not in src, "no Kai bubble on the drive page")
ok("1800 250 015" in src and "tel:1800250015" in src, "AOD hotline 1800 250 015")
ok("Support, not medical care" in src, "Support, not medical care")
ok("This is a risk comparison, not a safe limit or a target." in src, "Vic .05 doubling is not worded as a safe limit")
ok("Being under the limit is not the same as being safe to drive." in src, "under the limit is not the same as safe")

# Shame words and brand names are checked in <main> only (the site footer already
# names fellowships such as Porn Addicts Anonymous on every page).
low = main_text.lower()
ok("high-functioning" not in low and "high functioning" not in low, "no high-functioning label")
ok(not re.search(r"\bdrunks?\b|\baddicts?\b", low), "no shame words drunk or addict")
for brand in ("uber", "didi", "ola ", "13cabs", "13 cabs", "taxify", "lyft", "bolt"):
    ok(brand not in low, f"no brand name: {brand}")

limits = [
    "https://www.qld.gov.au/transport/safety/road-safety/drink-driving/blood-alcohol",
    "https://www.qld.gov.au/transport/safety/road-safety/drink-driving/drugs",
    "https://www.nsw.gov.au/driving-boating-and-transport/roads-safety-and-rules/safe-driving/alcohol-and-drugs",
    "https://www.transport.nsw.gov.au/roadsafety/topics-tips/alcohol",
    "https://transport.vic.gov.au/road-and-active-transport/road-rules-and-safety/alcohol-drugs-and-driving/alcohol-and-driving-laws",
    "https://transport.vic.gov.au/road-rules-and-safety/alcohol-drugs-and-driving/drugs-and-driving-laws",
    "https://www.wa.gov.au/organisation/road-safety-commission/drink-and-drug-driving",
    "https://www.mylicence.sa.gov.au/road-rules/the-drivers-handbook/alcohol-drugs",
    "https://rsac.tas.gov.au/driving-under-the-influence/",
    "https://nt.gov.au/driving/safety/alcohol-drugs-and-driving",
    "https://www.cityservices.act.gov.au/roads-and-paths/road-safety/drink-and-drug-driving",
    "https://www.healthdirect.gov.au/medicines-and-driving",
]
for u in limits:
    ok(u in src, f"official link present: {u}")

ok("https://homecircle.au/before-you-drive.html" in Path("sitemap.xml").read_text(), "in sitemap.xml")
ok('href="before-you-drive.html"' in Path("index.html").read_text(), "linked from the home page")
ok('href="before-you-drive.html"' in Path("help.html").read_text(), "linked from the Help page")
pages = sorted(glob.glob("*.html") + glob.glob("library/*.html") + glob.glob("families/*.html"))
missing = [f for f in pages if "before-you-drive.html" not in Path(f).read_text() or ">Before you drive<" not in Path(f).read_text()]
ok(not missing, f"footer link on every page ({len(pages)} pages; missing: {missing})")
# Not in the main nav
nav = re.search(r"<header class=\"site-head\">.*?</header>", src, re.S)
ok(nav and "before-you-drive.html" not in nav.group(0), "not in the main nav")

if fails:
    sys.exit(f"before-you-drive: {fails} failure(s)")
print("passed: 0 failure(s)")
