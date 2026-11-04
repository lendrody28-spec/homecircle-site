#!/usr/bin/env python3
"""Pull the website's wording straight out of the HomeCircle iOS source, so the
site says exactly what the app says. Usage:
  python3 tools/extract_app_content.py /path/to/homecircle-ios > tools/app-content.json
"""
import json, re, sys, pathlib

ROOT = pathlib.Path(sys.argv[1] if len(sys.argv) > 1 else "../homecircle-ios-repo")
CORE = ROOT / "HomeCircle" / "Core"

TOKEN = re.compile(r'''\s*(?:(?P<str>"(?:[^"\\]|\\.)*")|(?P<num>-?\d+(?:\.\d+)?(?:_\d+)*)|(?P<range>\.\.\.)|(?P<id>\.?[A-Za-z_][A-Za-z0-9_]*(?:\.[A-Za-z_][A-Za-z0-9_]*)*)|(?P<p>[()\[\]:,+]))''')

def tokens(src):
    pos, out = 0, []
    while pos < len(src):
        m = TOKEN.match(src, pos)
        if not m:
            if src[pos:].strip() == "":
                break
            raise ValueError("bad token near: " + src[pos:pos+40])
        pos = m.end()
        kind = m.lastgroup
        out.append((kind, m.group(kind)))
    return out

def unquote(s):
    return json.loads(s)

class P:
    def __init__(self, toks, consts):
        self.t, self.i, self.c = toks, 0, consts
    def peek(self):
        return self.t[self.i] if self.i < len(self.t) else (None, None)
    def take(self, v=None):
        tok = self.t[self.i]; self.i += 1
        if v is not None and tok[1] != v:
            raise ValueError(f"expected {v} got {tok}")
        return tok
    def value(self):
        k, v = self.take()
        if k == "str":
            val = unquote(v)
        elif k == "num":
            val = float(v.replace("_", "")) if "." in v else int(v.replace("_", ""))
            if self.peek()[0] == "range":
                self.take(); hi = self.take()[1]; val = [val, int(hi.replace("_", ""))]
        elif k == "p" and v == "[":
            val = []
            while self.peek()[1] != "]":
                val.append(self.value())
                if self.peek()[1] == ",": self.take()
            self.take("]")
        elif k == "id":
            if v in ("true", "false"): val = v == "true"
            elif v == "nil": val = None
            elif self.peek()[1] == "(":
                self.take("(")
                args = {"__call__": v}
                n = 0
                while self.peek()[1] != ")":
                    if self.t[self.i][0] == "id" and self.t[self.i+1][1] == ":":
                        key = self.take()[1]; self.take(":")
                    else:
                        key = f"_{n}"; n += 1
                    args[key] = self.value()
                    if self.peek()[1] == ",": self.take()
                self.take(")")
                val = args
            else:
                val = self.c.get(v, self.c.get(v.split(".")[-1], v))
        else:
            raise ValueError(f"unexpected {k} {v}")
        while self.peek()[1] == "+":
            self.take(); val = val + self.value()
        return val

def static_strings(text):
    out = {}
    for m in re.finditer(r'static let (\w+)\s*(?::\s*\w+)?\s*=\s*("(?:[^"\\]|\\.)*")', text):
        out[m.group(1)] = unquote(m.group(2))
    return out

def array_literal(text, name, consts):
    m = re.search(r'static let ' + name + r'\s*(?::\s*\[[\w ]+\])?\s*=\s*\[', text)
    if not m:
        raise ValueError("missing " + name)
    start = m.end() - 1
    depth, i = 0, start
    while True:
        ch = text[i]
        if ch == '"':
            i += 1
            while text[i] != '"':
                i += 2 if text[i] == "\\" else 1
        elif ch == "[": depth += 1
        elif ch == "]":
            depth -= 1
            if depth == 0: break
        i += 1
    return P(tokens(text[start:i+1]), consts).value()

def struct_literal(text, name, consts):
    m = re.search(r'static let ' + name + r'\s*=\s*(\w+\()', text)
    start = m.start(1)
    depth, i = 0, m.end() - 1
    while True:
        ch = text[i]
        if ch == '"':
            i += 1
            while text[i] != '"':
                i += 2 if text[i] == "\\" else 1
        elif ch == "(": depth += 1
        elif ch == ")":
            depth -= 1
            if depth == 0: break
        i += 1
    return P(tokens(text[start:i+1]), consts).value()

def clean(o):
    if isinstance(o, dict):
        return {k: clean(v) for k, v in o.items() if k != "__call__"}
    if isinstance(o, list):
        return [clean(v) for v in o]
    return o

def enum_block(text, name):
    """Source of one `enum Name { ... }` block (brace matched, strings skipped)."""
    m = re.search(r'enum ' + name + r'\s*\{', text)
    i, depth = m.end() - 1, 0
    while True:
        ch = text[i]
        if ch == '"':
            i += 1
            while text[i] != '"':
                i += 2 if text[i] == "\\" else 1
        elif ch == "{": depth += 1
        elif ch == "}":
            depth -= 1
            if depth == 0: return text[m.start():i+1]
        i += 1

def helplines(legal_src, consts):
    """HelpDirectory, Gam-Anon and Gamblers Anonymous Australia, exactly as the app has them."""
    hd = enum_block(legal_src, "HelpDirectory")
    lines = {}
    for name in re.findall(r'static let (\w+) = Helpline\(', hd):
        lines[name] = clean(struct_literal(hd, name, consts))
    primary = array_literal(hd, "primary", {})
    ga = enum_block(legal_src, "GAAustralia")
    return {
        "lines": lines,
        "primary": [lines[n]["id"] for n in primary],
        "byName": {n: v["id"] for n, v in lines.items()},
        "familyDrugSupportURL": static_strings(hd)["familyDrugSupportURL"],
        "gamAnon": static_strings(enum_block(legal_src, "GamAnon")),
        "ga": {**static_strings(ga.split("static let contacts")[0]), "contacts": clean(array_literal(ga, "contacts", consts))},
    }

def main():
    legal = (CORE / "LegalCopy.swift").read_text()
    consts = static_strings(enum_block(legal, "LegalCopy"))
    steps_src = (CORE / "TwelveSteps.swift").read_text()
    consts.update(static_strings(steps_src))
    consts["TwelveSteps.officialURL"] = consts["officialURL"]
    lib = (CORE / "LibraryCatalog.swift").read_text()
    consts.update(static_strings(lib))
    lib_consts = dict(consts)
    lib_consts["LegalCopy.notAffiliated"] = consts["notAffiliated"]

    items = []
    for group in ["breathing", "guides", "stressGuides", "body", "meditations", "everydayMeditations", "fellowships"]:
        for raw in array_literal(lib, group, lib_consts):
            if raw.get("__call__") == "bodyItem":
                r = clean(raw)
                item = {
                    "id": r["id"], "title": r["title"], "summary": r["summary"], "category": "body",
                    "tag": "Body", "minutes": 4, "kind": "reading", "breathHold": False,
                    "traumaSensitive": False, "optInBodyScan": False,
                    "paragraphs": ["People often describe these rough stages. They are not a diagnosis and they are not a prediction for you.", consts["severeWarning"]] + r["stages"],
                    "steps": [],
                    "links": [{"id": r["id"] + "-hd", "title": r["linkTitle"], "url": r["link"]},
                              {"id": r["id"] + "-adf", "title": "Alcohol and Drug Foundation", "url": "https://adf.org.au/"}],
                    "phoneDisplay": None, "phoneDial": None,
                }
            else:
                item = clean(raw)
                item["category"] = item["category"].lstrip(".")
                item["kind"] = item["kind"].lstrip(".")
            items.append(item)

    tb = (CORE / "TechniqueBackground.swift").read_text()
    tb_consts = dict(consts); tb_consts.update(static_strings(tb))
    mapping = dict(re.findall(r'case ((?:"[\w-]+",?\s*)+):\s*return (\w+)', tb))
    backgrounds = {}
    for cases, var in mapping.items():
        bg = clean(struct_literal(tb, var, tb_consts))
        bg["sources"] = [{"title": s["_1"], "url": s["_2"]} for s in [ {k: v for k, v in x.items()} for x in bg["sources"]]]
        for cid in re.findall(r'"([\w-]+)"', cases):
            backgrounds[cid] = bg

    art = (CORE / "TechniqueArt.swift").read_text()
    arts = {m.group(1): {"asset": m.group(2), "label": m.group(3)} for m in re.finditer(r'static let (\w+) = TechniqueArt\(asset: "(\w+)", label: "([^"]+)"\)', art)}
    drawing = {}
    hero = {}
    fn_draw = art.split("static func art(forDrawing")[1].split("static func hero")[0]
    fn_hero = art.split("static func hero")[1].split("enum BreathPhase")[0]
    for cases, var in re.findall(r'case ((?:"[\w-]+",?\s*)+):\s*return (\w+)', fn_draw):
        for k in re.findall(r'"([\w-]+)"', cases): drawing[k] = var
    for cases, var in re.findall(r'case ((?:"[\w-]+",?\s*)+):\s*return (\w+)', fn_hero):
        for k in re.findall(r'"([\w-]+)"', cases): hero[k] = var

    stats_src = (CORE / "VerifiedStats.swift").read_text()
    stats = clean(array_literal(stats_src, "all", consts))
    stages_src = (CORE / "RecoveryStages.swift").read_text()
    st_consts = static_strings(stages_src)
    stages = clean(array_literal(stages_src, "all", consts))
    stage_sources = clean(array_literal(stages_src, "sources", consts))
    steps = clean(array_literal(steps_src, "all", consts))
    books = clean(array_literal(steps_src, "all", {**consts, "TwelveSteps.officialURL": consts["officialURL"]}) if False else None)
    books_src = steps_src.split("enum RecoveryBooks")[1]
    books = clean(array_literal(books_src, "all", {**consts, "TwelveSteps.officialURL": consts["officialURL"]}))
    books_consts = static_strings(books_src.split("static let all")[0])
    steps_consts = static_strings(steps_src.split("enum TwelveSteps")[1].split("static let all")[0])

    json.dump({
        "legal": static_strings(enum_block(legal, "LegalCopy")),
        "helplines": helplines(legal, {f"LegalCopy.{k}": v for k, v in static_strings(enum_block(legal, "LegalCopy")).items()}),
        "reminder": static_strings((CORE / "ReminderTiming.swift").read_text()),
        "helpButton": {"title": "Help", "fillHex": "#F2A08B", "foregroundHex": "#6B2416"},
        "items": items, "backgrounds": backgrounds, "arts": arts, "drawing": drawing, "hero": hero,
        "stats": stats, "stages": stages, "stageCopy": st_consts, "stageSources": stage_sources,
        "twelveSteps": steps, "twelveStepsCopy": steps_consts, "books": books, "booksCopy": books_consts,
        "crisis": static_strings((CORE / "CrisisAccess.swift").read_text()),
    }, sys.stdout, indent=1, ensure_ascii=False)

main()
