"""Accessibility options: shared practice copy for HomeCircle AU and US (written once, used by both sites).

The same file lives in lendrody28-spec/homecircle-site and lendrody28-spec/homecircle-us-site (tools/access_copy.py).
Write copy here in Australian English. us() turns it into US spelling and terms for the US site.
Rules (plan.md, Hale and Raven, 10 Nov 2026):
  - versions are choices anyone can pick; never ask anyone to tell us about a disability
  - say "people with disability" (US "people with disabilities") and "Deaf"
  - never: wheelchair-bound, confined to, suffers from, special needs, differently abled, inspiration tone
  - no "relieves pain", "helps you heal", "therapy", pain or paralysis claims; no Auslan / ASL video claims
  - support, not medical care
NEW READ-ALOUD: new or changed practice text has no Voice B clip yet. Practice pages are read by the device voice
(as before); clips for these lines are on the Thursday Voice B re-record list (see the PR).
"""
import html as _html
import re as _re

CHECKED = "10 November 2026"

# AU -> US words. Whole words only, applied in order. Keep this list short and test it (tools/test_access.py).
_US = [
    ("check with your doctor or physio", "check with your doctor or physical therapist"),
    ("your GP or physio", "your doctor or physical therapist"),
    ("a GP or physio", "a doctor or physical therapist"),
    ("practise", "practice"), ("practising", "practicing"),
    ("counsellor", "counselor"), ("colour", "color"), ("footpath", "sidewalk"),
    ("people with disability", "people with disabilities"),
    ("favourite", "favorite"), ("organisation", "organization"),
]

def us(s):
    for a, b in _US:
        s = _re.sub(r"\b" + _re.escape(a) + r"\b", b, s)
        s = _re.sub(r"\b" + _re.escape(a[0].upper() + a[1:]) + r"\b", b[0].upper() + b[1:], s)
    return s

def _region(obj, region):
    if region == "AU":
        return obj
    if isinstance(obj, str):
        return us(obj)
    if isinstance(obj, list):
        return [_region(x, region) for x in obj]
    if isinstance(obj, tuple):
        return tuple(_region(x, region) for x in obj)
    if isinstance(obj, dict):
        return {k: _region(v, region) for k, v in obj.items()}
    return obj

# ---------------------------------------------------------------- Mindful moving (was Mindful walking)
# Same URL: library/mindful-walking.html. The walking steps are the app's own, unchanged.
MOVING = {
    "title": "Mindful moving: walking, seated or lying down",
    "short": "Mindful moving",
    "summary": "A slow practice where you notice movement, breath and what's around you: walking, seated, in a wheelchair or lying down.",
    "seoTitle": "Mindful moving: walking, seated meditation or lying down – HomeCircle",
    "seoDesc": "A free mindful moving practice: walking, seated meditation, wheelchair mindfulness or lying down, and a gentler way to practise if you live with chronic pain. Stop any time. Support, not medical care.",
    "intro": [
        "Pick the version that suits you today. Anyone can use any version, and you can switch whenever you like.",
        "Eyes can stay open the whole time. Stop any time.",
    ],
    "safety": "Stop if anything hurts. If you have pain or an injury, check with your GP or physio before you try a new movement.",
    "chooseHeading": "Choose your version",
    "versions": [
        {"id": "walking", "name": "Walking", "intro": None, "steps": None},   # None = the app's own walking steps
        {"id": "seated", "name": "Seated", "intro": "On a chair, a couch or sitting up in bed. Sit in a way that feels supported and steady.", "steps": [
            ("Settle", "Sit still for a moment. Notice where your body meets the chair.", 30, "groundFeel"),
            ("Slow movement", "Slowly lift and lower one hand, or roll your shoulders. Move a little slower than usual and notice each movement.", 60, "scanHands"),
            ("Breath and movement", "Let the movement and your breathing find a rhythm. No counting needed.", 60, "breatheOut"),
            ("Look around", "Name a few things you can see, or notice what you can feel, like air on your skin.", 45, "groundSee"),
            ("Listen", "Notice the sounds, near and far. Then rest still for a breath.", 45, "groundHear"),
        ]},
        {"id": "wheelchair", "name": "In a wheelchair", "intro": "You can move or stay still. Both are fine.", "steps": [
            ("Settle", "Notice the chair supporting you: your back, your seat and your arms.", 30, "groundFeel"),
            ("Slow pushes", "If you're moving, go a little slower than usual, only where it's clear and safe, and notice your hands on the rims or controls. If you're staying still, rest a hand on a rim or your lap and notice how it feels.", 60, "scanHands"),
            ("Breath and movement", "Let your movement and your breathing find a rhythm. No counting needed.", 60, "breatheOut"),
            ("Look around", "Name a few things you can see, or notice what you can feel, like air on your skin.", 45, "groundSee"),
            ("Listen", "Notice the sounds, near and far. Then rest still for a breath.", 45, "groundHear"),
        ]},
        {"id": "lying-down", "name": "Lying down", "intro": "On your back or your side, whichever is comfortable. A pillow under your knees or head is fine.", "steps": [
            ("Settle", "Lie still for a moment. Notice where your body meets the bed or the floor.", 30, "groundFeel"),
            ("Small movement", "Slowly open and close one hand, or turn your head a little if that's comfortable. Notice each movement.", 60, "scanHands"),
            ("Breath and movement", "Let the movement and your breathing find a rhythm. No counting needed.", 60, "breatheOut"),
            ("Listen", "Notice the sounds, near and far. Then rest still for a breath.", 45, "groundHear"),
        ]},
        {"id": "one-hand", "name": "One hand, or just the breath", "intro": "For days when bigger movement isn't comfortable, or if it never is.", "steps": [
            ("Settle", "Rest one hand wherever it's comfortable. Just notice it.", 30, "scanHands"),
            ("Small movement", "Slowly press one fingertip down and lift it again. If moving isn't comfortable, notice the breath instead: the rise and fall of your chest or belly.", 60, "scanHands"),
            ("Out-breath", "Breathe out a little longer than you breathe in, if that feels okay.", 60, "breatheOut"),
            ("Notice", "Notice one sound, or one thing you can feel. Then rest for a breath.", 45, "groundHear"),
        ]},
    ],
    "tile": "Mindful moving: walking, seated or lying down",
}

# ---------------------------------------------------------------- Body scan: Hale's gentler version
SCAN = {
    "gentleTitle": "A gentler version",
    "gentle": "A gentler version if you live with pain or limited feeling. Skip any part, and check with your doctor or physio if you're unsure.",   # Hale's wording
    "gentleMore": [
        "If a part of your body hurts, has no feeling, or isn't there, skip it. Rest your attention on another part, on the breath, or on where your body meets the chair or bed.",
        "You can do this sitting, in a wheelchair or lying down, with your eyes open or closed.",
        "If paying attention to your body brings up pain or distress, open your eyes and stop. That's okay.",
    ],
    "holdsNote": "This practice doesn't ask you to hold your breath.",
}

# ---------------------------------------------------------------- word check: app cues and paragraphs, web only
# Keys are the app's text after web() (no "Kai: " prefix). Values replace them on the website only.
EDITS = {
    # mindful walking -> mindful moving (summary on the page, Library and Meditations tiles)
    "A slow walk where you notice your feet, breath and surroundings.": MOVING["summary"],
    # body scan
    "Opt-in. A short attention walk from feet upward.": "Opt-in. A short scan of attention through the body, from your feet up, or starting wherever feels okay.",
    "notice both feet. You can wiggle them.": "notice your feet, or wherever your body meets the chair or bed. You can wiggle your toes if that's comfortable.",
    "the weight of your legs on the chair.": "the weight of your legs, or of whatever is resting on the chair or bed. Skip this if it doesn't fit your body.",
    "warmth or coolness in the hands.": "warmth or coolness in your hands, or in one hand. Skip this if it doesn't fit your body.",
    "Moving attention slowly through the body can help you notice tension and let some of it go, and many people find it calming. Healthdirect lists scanning the body as one way to meditate. Turning attention inward is not comfortable for everyone, especially after trauma, so this stays off until you turn it on, and you can stop at any time.": "Moving attention slowly through the body may help you notice tension, and some people find it calming. Healthdirect lists scanning the body as one way to meditate. Turning attention inward is not comfortable for everyone, especially after trauma, so this stays off until you turn it on, and you can stop at any time.",
    "let the shoulders drop if they want to. Then open your eyes wide.": "let the shoulders drop if they want to. Then, if your eyes were closed, open them and notice the room.",
    # breathing anchor
    "name one ordinary object you can see.": "name one ordinary object you can see, or one sound you can hear.",
    "press your feet down. The practice can end here.": "press your feet down, or press your hands or back gently into the chair or bed. The practice can end here.",
    # urge surfing meditation
    "feet on the floor. You can keep your eyes open.": "feet on the floor, or notice wherever your body is supported. You can keep your eyes open.",
    # one-thing focus
    "Pick one small task. Dishes, a shower, a walk to the end of the street.": "Pick one small task. Dishes, a shower, a cup of tea, or a walk or wheel to the end of the street.",
    # stress and anxiety
    "Try one small thing: a longer out-breath, feet on the floor, or a quick HALT check. Moving your body, eating something and talking to someone can all help too.":
        "Try one small thing: a longer out-breath, feet on the floor or hands in your lap, or a quick HALT check. Moving your body in a way that suits you, eating something and talking to someone can all help too.",
    "Press your feet down and name three things you can see.": "Press your feet down, or your hands into your lap. Name three things you can see or hear.",
    # mindful eating
    "look at the food for a moment. Colour, shape, texture.": "look at the food for a moment, or hold it in your hand. Colour, shape, texture.",
    # body and recovery stages (AU)
    "A mindful walk is a gentle way to reset on a heavy day.": "Mindful moving (walking, seated or lying down) is a gentle way to reset on a heavy day.",
}
TITLE_EDITS = {"Feet on the floor": "Feet on the floor, or hands in your lap"}
EXTRA_PARAS = {
    "guide-54321": ["If you can't see or hear, use the senses you have, or skip that step. You can also count fewer things. There's no wrong way to do this."],
    "med-urge": ["You can do this sitting, in a wheelchair or lying down."],
    "med-breath": ["You can do this sitting, in a wheelchair or lying down."],
}

# ---------------------------------------------------------------- site-wide accessibility wording
SITE = {
    "transcript": "The words on this page are the transcript. Read aloud reads the same words.",
    "safeLine": "We're working to make HomeCircle accessible. Tell us what isn't working.",   # Hale's safe line
    "paceLabel": "Pace",
    "paceUsual": "Usual pace",
    "paceSlower": "Slower pace",
    "pace": "Slower pace makes each step, and each breath in and out, last longer. Breath holds don't get longer.",
    "still": "Show a text count instead of the moving circle",
    "stillNote": "If your device is set to reduce motion, the text count is on already.",
    "pause": "Pause",
    "resume": "Resume",
    "moreDetails": "More details",
}

def copy(region):
    """All shared copy for one site ("AU" or "US")."""
    out = {"MOVING": _region(MOVING, region), "SCAN": _region(SCAN, region), "SITE": _region(SITE, region),
           "EDITS": {k if region == "AU" else us(k): _region(v, region) for k, v in EDITS.items()},
           "TITLE_EDITS": TITLE_EDITS, "EXTRA_PARAS": _region(EXTRA_PARAS, region), "CHECKED": CHECKED}
    if region == "US":
        # the US app text already says sidewalk/color/counselor; keys must match it
        out["EDITS"]["look at the food for a moment. Color, shape, texture."] = us(EDITS["look at the food for a moment. Colour, shape, texture."])
    return out

def edit(A, t):
    return A["EDITS"].get(t, t)

def moving_versions(A, walking_steps, walking_intro, art_img, r, E, pace_html):
    """<details class="more practice-version"> per version. Each has its own step player (data-player)."""
    M = A["MOVING"]
    out = []
    for v in M["versions"]:
        steps = walking_steps if v["steps"] is None else v["steps"]
        lis = []
        for title, cue, secs, art in steps:
            img = art_img(art, r) if art else ""
            s = f' <span class="small">({secs} seconds)</span>' if secs else ""
            lis.append(f'<li class="pstep" data-seconds="{secs}"><div class="grid g2">{img}<div><h3>{E(title)}{s}</h3><p>{E(cue)}</p></div></div></li>')
        it = walking_intro if v["steps"] is None else v.get("intro")
        intro = f'<p>{E(it)}</p>' if it else ""
        hid = f'pl-{v["id"]}'
        out.append(f"""<details class="more practice-version" id="{v["id"]}"><summary>{E(v["name"])}</summary>{intro}
<section class="player" data-player aria-labelledby="{hid}"><h2 id="{hid}" class="mt0">{E(v["name"])}: step by step</h2>
<div class="pcontrols" hidden><div class="progress" aria-hidden="true"><i></i></div><p class="status" data-pos aria-live="polite"></p></div>
<ol class="steps-list">{"".join(lis)}</ol>
<div class="pcontrols btn-row" hidden><button class="btn ghost" type="button" data-prev>Back</button><button class="btn" type="button" data-play>Start</button><button class="btn ghost" type="button" data-next>Next</button><span class="count" data-pcount aria-hidden="true"></span></div>
{pace_html(hid)}
</section></details>""")
    return "".join(out)

def pace_select(A, E, uid):
    S = A["SITE"]
    return (f'<div class="pace pcontrols" hidden><label for="pace-{uid}">{E(S["paceLabel"])}</label>'
            f'<select id="pace-{uid}" data-pace><option value="1">{E(S["paceUsual"])}</option><option value="1.5">{E(S["paceSlower"])}</option></select>'
            f'<p class="small">{E(S["pace"])}</p></div>')
