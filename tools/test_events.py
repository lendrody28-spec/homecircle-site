#!/usr/bin/env python3
"""Events page: A/An grammar, finished-event hiding, and card data attributes.
python3 tools/test_events.py
"""
import datetime, json, os, re, subprocess, sys
from html.parser import HTMLParser
from zoneinfo import ZoneInfo

root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.chdir(root)
sys.path.insert(0, os.path.join(root, "tools"))
import events_util as EVU

fails = 0

def ok(cond, msg):
    global fails
    print(("ok " if cond else "FAIL ") + msg)
    if not cond:
        fails += 1


# --- grammar ---
ok(EVU.ev_article("AA") == "An", "An AA")
ok(EVU.ev_article("NA") == "An", "An NA")
ok(EVU.ev_article("GA") == "A", "A GA")
ok(EVU.ev_article("PA") == "A", "A PA")
ok(EVU.ev_article("Al-Anon") == "An", "An Al-Anon")
ok(EVU.ev_article("Nar-Anon") == "A", "A Nar-Anon")
ok(EVU.ev_article("SMART") == "A", "A SMART")
ok(EVU.ev_article("") == "A", "empty fellowship uses A")


# --- Python hide logic (state time zones) ---
def at(iso_utc):
    return datetime.datetime.fromisoformat(iso_utc).replace(tzinfo=datetime.timezone.utc)

# Brisbane is UTC+10 year-round.
ok(not EVU.event_is_finished({"start": "2026-11-22", "end": "2026-11-22", "state": "QLD"}, at("2026-11-22T13:59:00")),
   "QLD event still on at 23:59 Brisbane")
ok(EVU.event_is_finished({"start": "2026-11-22", "end": "2026-11-22", "state": "QLD"}, at("2026-11-22T14:00:00")),
   "QLD event hidden at 00:00 the next day in Brisbane")

# Perth is UTC+8 year-round. 00:30 on 27 Nov in Brisbane is still 22:30 on 26 Nov in Perth.
ok(not EVU.event_is_finished({"start": "2026-11-26", "end": "2026-11-26", "state": "WA"}, at("2026-11-26T14:30:00")),
   "WA event still on at 22:30 Perth when Brisbane is already 27 Nov")
ok(EVU.event_is_finished({"start": "2026-11-26", "end": "2026-11-26", "state": "WA"}, at("2026-11-26T16:00:00")),
   "WA event hidden at 00:00 the next day in Perth")

# Sydney is on daylight saving (UTC+11) in November.
ok(not EVU.event_is_finished({"start": "2026-11-22", "end": "2026-11-22", "state": "NSW"}, at("2026-11-22T12:59:00")),
   "NSW event still on at 23:59 AEDT")
ok(EVU.event_is_finished({"start": "2026-11-22", "end": "2026-11-22", "state": "NSW"}, at("2026-11-22T13:00:00")),
   "NSW event hidden at 00:00 the next day in Sydney")

ok(not EVU.event_is_finished({"start": "2026-11-22", "state": "ACT"}, at("2026-11-22T12:59:00")),
   "missing end date falls back to start; ACT uses Sydney")
ok(EVU.event_is_finished({"start": "2026-11-22", "state": "ACT"}, at("2026-11-22T13:00:00")),
   "ACT event with no end date hides the day after start")


# --- built HTML ---
class Cards(HTMLParser):
    def __init__(self):
        super().__init__()
        self.cards = []
        self._cur = None
        self._in_sum = 0
        self.scripts = []
        self._sum = ""
    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        cls = (a.get("class") or "").split()
        if tag == "li" and "ev-card" in cls:
            self._cur = {"end": a.get("data-end"), "state": a.get("data-state"), "hidden": "hidden" in a, "sum": ""}
        if tag == "p" and "ev-sum" in (a.get("class") or "").split() and self._cur is not None:
            self._in_sum = 1
            self._sum = ""
        if tag == "script" and a.get("src"):
            self.scripts.append(a.get("src"))
    def handle_endtag(self, tag):
        if tag == "p" and self._in_sum:
            self._cur["sum"] = self._sum
            self._in_sum = 0
        if tag == "li" and self._cur is not None:
            self.cards.append(self._cur)
            self._cur = None
    def handle_data(self, data):
        if self._in_sum:
            self._sum += data


def parse_page(path):
    html = open(path, encoding="utf-8").read()
    p = Cards()
    p.feed(html)
    return html, p

for path in ("events.html", "index.html"):
    html, p = parse_page(path)
    ok(any(re.search(r"assets/events-hide\.js\?v=", src) for src in p.scripts), path + ": events-hide.js included")
    ok("A AA event" not in html and "A NA event" not in html, path + ": no 'A AA' or 'A NA'")
    ok(p.cards, path + ": has event cards")
    for i, c in enumerate(p.cards):
        ok(bool(c["end"]) and re.fullmatch(r"\d{4}-\d{2}-\d{2}", c["end"] or ""),
           f"{path} card {i}: data-end is a date")
        ok(bool(c["state"]) and c["state"] in EVU.EVENT_ZONES,
           f"{path} card {i}: data-state is a known state ({c['state']})")
        if "event listed by" in c["sum"]:
            ok(not c["sum"].startswith("A AA") and not c["sum"].startswith("A NA"),
               f"{path} card {i}: summary article is not 'A AA/NA'")
            if c["sum"].startswith("An AA") or c["sum"].startswith("An NA") or c["sum"].startswith("A "):
                ok(True, f"{path} card {i}: summary uses an article")
    # Build-time filter: no card whose end has already passed in its state zone.
    now = datetime.datetime.now(datetime.timezone.utc)
    leftover = [c for c in p.cards if EVU.event_is_finished({"end": c["end"], "start": c["end"], "state": c["state"]}, now)]
    ok(not leftover, path + ": built page has no finished events " + str(leftover))

html, p = parse_page("events.html")
ok("An AA event listed by" in html, "events.html has 'An AA event'")
ok("An NA event listed by" in html, "events.html has 'An NA event'")
# Stale retreats that ended 20-22 Nov 2026 should be gone after a rebuild on/after 26 Nov.
ok("Sobriety Sisters" not in html, "finished 20-22 Nov QLD retreat left out of the rebuilt page")
ok("Sydney Combined Area Women’s Retreat" not in html and "Sydney Combined Area Women's Retreat" not in html,
   "finished 20-22 Nov NSW retreat left out of the rebuilt page")

# meetings page and kai/help copy were not used as a vehicle for this change
meet = open("meetings.html", encoding="utf-8").read()
ok("events-hide.js" not in meet, "meetings.html does not load the events hide script")


# --- JS hide logic, same cases as the Python tests ---
js = r"""
const ev = require("./assets/events-hide.js");
const cases = [
  ["2026-11-22", "QLD", "2026-11-22T13:59:00Z", false, "QLD still on at 23:59 Brisbane"],
  ["2026-11-22", "QLD", "2026-11-22T14:00:00Z", true, "QLD hidden at 00:00 next day Brisbane"],
  ["2026-11-26", "WA", "2026-11-26T14:30:00Z", false, "WA still on at 22:30 Perth"],
  ["2026-11-26", "WA", "2026-11-26T16:00:00Z", true, "WA hidden at 00:00 next day Perth"],
  ["2026-11-22", "NSW", "2026-11-22T12:59:00Z", false, "NSW still on at 23:59 AEDT"],
  ["2026-11-22", "NSW", "2026-11-22T13:00:00Z", true, "NSW hidden at 00:00 next day Sydney"],
  ["2026-11-22", "ACT", "2026-11-22T12:59:00Z", false, "ACT uses Sydney, still on"],
  ["2026-11-22", "ACT", "2026-11-22T13:00:00Z", true, "ACT uses Sydney, hidden next day"]
];
let fails = 0;
for (const [end, state, iso, want, msg] of cases) {
  const got = ev.isFinished(end, state, new Date(iso));
  if (got !== want) { console.log("FAIL " + msg + " (got " + got + ")"); fails++; }
  else console.log("ok " + msg);
}
const zones = ev.ZONES;
const expected = {
  QLD: "Australia/Brisbane", NSW: "Australia/Sydney", ACT: "Australia/Sydney",
  VIC: "Australia/Melbourne", SA: "Australia/Adelaide", WA: "Australia/Perth",
  TAS: "Australia/Hobart", NT: "Australia/Darwin"
};
if (JSON.stringify(zones) !== JSON.stringify(expected)) {
  console.log("FAIL JS zone map mismatch"); fails++;
} else console.log("ok JS zone map");
process.exit(fails ? 1 : 0);
"""
r = subprocess.run(["node", "-e", js], cwd=root, capture_output=True, text=True)
print(r.stdout, end="")
if r.stderr:
    print(r.stderr, end="")
ok(r.returncode == 0, "node hide-logic tests passed")

# JS and Python zone maps must stay in lockstep.
ok(EVU.EVENT_ZONES == {
    "QLD": "Australia/Brisbane",
    "NSW": "Australia/Sydney",
    "ACT": "Australia/Sydney",
    "VIC": "Australia/Melbourne",
    "SA": "Australia/Adelaide",
    "WA": "Australia/Perth",
    "TAS": "Australia/Hobart",
    "NT": "Australia/Darwin",
}, "Python zone map")
src = open("assets/events-hide.js", encoding="utf-8").read()
code = re.sub(r"/\*[\s\S]*?\*/", "", src)
code = re.sub(r"//.*", "", code)
ok("fetch(" not in code and "XMLHttpRequest" not in code and "localStorage" not in code
   and "document.cookie" not in code and "sendBeacon" not in code,
   "events-hide.js has no tracking or network calls")

print("events: %d failed" % fails)
sys.exit(1 if fails else 0)
