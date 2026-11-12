#!/usr/bin/env python3
"""Children and parental AOD. python3 tools/test_children_parental_aod.py
Every figure in children-and-parental-aod.json must have a link and a checked-on date.
The built page must use Hale's cleared wording, keep crisis lines above the h1,
and stay free of blame labels, fixed-outcome claims and the Kai bubble.
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

data = json.loads(Path("children-and-parental-aod.json").read_text(encoding="utf-8"))
figures = data["figures"]
ok(len(figures) >= 1, "at least one cleared figure")

class P(HTMLParser):
    def __init__(s):
        super().__init__(); s.text = []; s.skip = 0
    def handle_starttag(s, t, a):
        if t in ("script", "style"): s.skip += 1
    def handle_endtag(s, t):
        if t in ("script", "style") and s.skip: s.skip -= 1
    def handle_data(s, d):
        if not s.skip: s.text.append(d)

src = Path("families/children-and-parental-aod.html").read_text(encoding="utf-8")
main = src[src.find("<main"):src.find("</main>")]
p = P(); p.feed(main)
text = html_unescape(re.sub(r"\s+", " ", "".join(p.text)))

for fig in figures:
    ident = fig.get("id", "?")
    url = (fig.get("url") or fig.get("link") or "").strip()
    checked = (fig.get("checkedOn") or fig.get("checked-on") or fig.get("checked_on") or "").strip()
    ok(bool(url) and url.startswith("https://"), f"{ident}: has an https link")
    ok(bool(checked), f"{ident}: has a checked-on date")
    # Every figure used in the data file must be cited on the page
    ok(url in src, f"{ident}: link is on the page")
    ok(checked in src, f"{ident}: checked-on date is on the page")

# Required headline figure, worded as harm from others' drinking
headline = "one in six children (17.1%) have experienced harm from the alcohol use of adults around them"
ok(headline in src, "FARE / La Trobe 17.1% headline wording")
ok("2021" in src, "17.1% is given with the 2021 survey period")
ok("others' drinking" in src or "others’ drinking" in src, "framed as harm from others' drinking")
ok("not a count of children who live with a parent who drinks" in src.lower()
   and src.lower().count("live with a parent who drinks") == 1,
   "17.1% is explained as not a count of children who live with a parent who drinks")
# Do not present 17% and 17.1% as two different rates
ok(not re.search(r"(?<![.\d])17%(?![\d])", src) or "17.1%" in src and src.count("17%") == 0, "does not use a separate 17% rate")

# Raven order: warm line to the parent before the figure, after the crisis lines
pre, _, post = src.partition("<h1")
ok('href="tel:000"' in pre and ("Call 000" in pre or ">000<" in pre), "Call 000 is above the h1")
ok('href="tel:131114"' in pre, "Lifeline is above the h1")
ok('href="tel:1800551800"' in pre and "1800 55 1800" in pre, "Kids Helpline 1800 55 1800 is above the h1")
ok("5 to 25" in pre, "Kids Helpline age range 5 to 25 is above the h1")
ok("If a child is in danger, call" in pre and "000" in pre, "If a child is in danger, call 000 is above the h1")
ok("one in six" not in pre and "17.1%" not in pre, "does not open the crisis area with the one in six figure")
# After h1, warm line appears before the figure
h1_and_after = src[src.find("<h1"):]
# strip tags for order check inside main body
body_txt = html_unescape(re.sub(r"<[^>]+>", " ", h1_and_after))
body_txt = re.sub(r"\s+", " ", body_txt)
ok("one in six" not in body_txt[: body_txt.find("</h1>") if "</h1>" in body_txt else 80], "h1 does not open with the one in six figure")
warm_i = body_txt.find("Asking for help can help the whole family")
fig_i = body_txt.find("one in six children (17.1%)")
helps_i = body_txt.find("What helps")
ok(0 <= warm_i < fig_i, "warm, blame-free line to the parent comes before the FARE figure")
ok(0 <= fig_i < helps_i, "FARE figure comes before What helps")

# Protective factors and no-blame
ok("It's not your fault" in text or "it's not your fault" in text, "It's not your fault")
ok(re.search(r"steady|caring adult", src, re.I), "protective factor: a steady or caring adult")
ok(re.search(r"routine", src, re.I), "protective factor: routine")
ok("child-protection or reporting service" in src or "child protection or reporting service" in src, "not a child-protection or reporting service")
ok("a page for families and partners" in text.lower(), "families mentioned as a page for families and partners")
ok("These are independent organisations. HomeCircle isn't affiliated with or endorsed by them." in text, "not-affiliated line")
ok("FARE says children living in a home with heavy alcohol use face higher risks of experiencing poor mental health, school disengagement, and intergenerational harm." in text, "FARE risk sentence starts with FARE says")
ok("Source: FARE (2024), reporting La Trobe University's 2021 Australian Alcohol's Harm to Others study. Checked on 12 November 2026." in text, "exact FARE source note")
ok("HomeCircle doesn't track shares." in text, "share wording on this page")
ok("Nothing is tracked." not in text, "old share line gone from this page")
ok('href="kids.html"' in src and "HomeCircle" in src[src.find("kids.html")-80:src.find("kids.html")+120], "kids-and-teens link names HomeCircle")
ok('white-space:nowrap' in src and "1800 55 1800" in src, "Kids Helpline number is marked not to wrap")

# Support numbers each have a tel: link
numbers = {
    "000": "tel:000",
    "Lifeline 13 11 14": "tel:131114",
    "Kids Helpline 1800 55 1800": "tel:1800551800",
    "Family Drug Support 1300 368 186": "tel:1300368186",
    "1800RESPECT 1800 737 732": "tel:1800737732",
    "Al-Anon/Alateen 1300 252 666": "tel:1300252666",
}
for label, href in numbers.items():
    ok(href in src, f"tel: link present for {label} ({href})")

# If twice as likely is used, the 2012 international review must be named
if re.search(r"twice as likely", src, re.I):
    ok(re.search(r"2012", src) and re.search(r"international review", src, re.I),
       "twice as likely is attributed to a 2012 international review")
else:
    ok(True, "twice as likely is not used (more likely wording only)")

low = text.lower()
ok("children of alcoholics" not in low and "children of addicts" not in low, "no children of alcoholics label")
ok(not re.search(r"\baddicts\b", low), "no shame word addicts")
# 'causes' as a claim in the visible main text
ok(not re.search(r"\bcauses\b", low), "no 'causes' in the visible page wording")
ok("hosts meetings" not in low and "our meetings" not in low and "homecircle meeting" not in low, "does not imply HomeCircle hosts meetings")

# No photos of children: no content images in main (share/ui buttons are fine)
ok(not re.search(r"<img\b", main, re.I), "no images on the page body")
ok('id="kai"' not in src and "kai-bubble" not in src, "no Kai bubble")

ok("https://homecircle.au/families/children-and-parental-aod.html" in Path("sitemap.xml").read_text(), "in sitemap.xml")
ok("children-and-parental-aod.html" in Path("families/index.html").read_text(), "linked from the families and partners area")

# Not in the main nav
nav = re.search(r"<header class=\"site-head\">.*?</header>", src, re.S)
ok(nav and "children-and-parental-aod.html" not in nav.group(0), "not in the main nav")

if fails:
    sys.exit(f"children-parental-aod: {fails} failure(s)")
print("passed: 0 failure(s)")
