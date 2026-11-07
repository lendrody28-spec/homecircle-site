#!/usr/bin/env python3
"""Home and support status is rendered from updates.json. No stale review wording.
The US domain is plain text. python3 tools/test_updates.py
"""
import glob, json, os, re, sys
from html.parser import HTMLParser

root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.chdir(root)
updates = json.loads(open("updates.json", encoding="utf-8").read())
fails = 0

def ok(cond, msg):
    global fails
    if cond:
        print("ok", msg)
    else:
        fails += 1
        print("FAIL", msg)

WHERE = [
    "Where we're at",
    "HomeCircle was inspired by LJ's own experience in recovery.",
    "HomeCircle for iPhone is available on the App Store in Australia.",
    "The HomeCircle app works online and offline. Kai, practices, the journal and day count work offline. Current meeting listings and outside links need a connection.",
    "Where HomeCircle is going",
    "Coming next: A US version of the HomeCircle website (homecirclerecovery.com). It is not live yet.",
    "Planned: A New Zealand version of the website.",
    "Planned: A United Kingdom version of the website.",
    "Planned: Apps for those countries, subject to local support content and legal checks.",
]
LEAD = "Answers below are for HomeCircle 1.3.0 for iPhone. In the app, open Profile and scroll to About to check your version."

ok(updates["version"] == "1.3.0", "version is 1.3.0")
ok(updates["supportLead"] == LEAD, "support lead in updates.json is verbatim")
ok([updates["whereWeAre"]["heading"]] + updates["whereWeAre"]["paragraphs"] + [updates["whereGoing"]["heading"]] + updates["whereGoing"]["items"] == WHERE, "status wording in updates.json is verbatim")

class Text(HTMLParser):
    def __init__(self):
        super().__init__()
        self.parts = []
        self.skip = 0
    def handle_starttag(self, tag, attrs):
        if tag in ("script", "style"):
            self.skip += 1
    def handle_endtag(self, tag):
        if tag in ("script", "style") and self.skip:
            self.skip -= 1
    def handle_data(self, data):
        if not self.skip:
            self.parts.append(data)

def visible(html):
    p = Text()
    p.feed(html)
    return re.sub(r"\s+", " ", "".join(p.parts))

pages = sorted(glob.glob("*.html") + glob.glob("families/*.html") + glob.glob("library/*.html"))
for page in ("index.html", "support.html"):
    html = open(page, encoding="utf-8").read()
    m = re.search(r'<section class="card mt hc-updates".*?</section>', html, re.S)
    ok(bool(m), page + ": status section rendered")
    if not m:
        continue
    sec = m.group(0)
    vis = visible(sec)
    at = 0
    for line in WHERE:
        j = vis.find(line, at)
        ok(j >= 0, page + ": " + line[:48])
        if j >= 0:
            at = j + len(line)
    ok("<a" not in sec.lower(), page + ": status section has no links")
    ok("homecirclerecovery.com" in sec and not re.search(r'href=["\'][^"\']*homecirclerecovery\.com', html), page + ": US domain is plain text")
    ok("Android" not in sec and "Google Play" not in sec and "Play Store" not in sec, page + ": no other-country store mention")
    ok("updates.json" not in html, page + ": page does not request updates.json")

for page in pages:
    html = open(page, encoding="utf-8").read()
    blocks = re.findall(r'<script type="application/ld\+json">(.*?)</script>', html)
    ok(blocks, page + ": json-ld present")
    if not blocks:
        continue
    data = json.loads(blocks[0].replace(r"<\/", "</"))
    apps = [n for n in data.get("@graph", []) if n.get("@type") == "MobileApplication"]
    ok(len(apps) == 1 and apps[0].get("softwareVersion") == updates["version"], page + ": softwareVersion " + str(apps[0].get("softwareVersion") if apps else None))

faq = open("tools/support-app-faq.html", encoding="utf-8").read()
sup = open("support.html", encoding="utf-8").read()
for label, src in (("faq source", faq), ("support.html", sup), ("index.html", open("index.html", encoding="utf-8").read())):
    ok("with Apple for review" not in src, label + ": stale Apple-review sentence gone")
    ok("version on the App Store today" not in src, label + ": stale App Store today sentence gone")
    ok("will arrive as a free update" not in src, label + ": stale free-update sentence gone")
ok(LEAD in faq, "faq source has the new lead")
ok(visible(sup).count(LEAD) == 1, "built support page has the lead once")
ok("Still on 1.2.16?" in faq and "Still on 1.2.16?" in sup, "Still on 1.2.16? answers kept")

for path in glob.glob("assets/*.js"):
    ok("updates.json" not in open(path, encoding="utf-8").read(), os.path.basename(path) + ": does not fetch updates.json")

print("updates: %d failed" % fails)
sys.exit(1 if fails else 0)
