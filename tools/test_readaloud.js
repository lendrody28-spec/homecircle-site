// Unit tests for assets/readaloud.js (node tools/test_readaloud.js)
const R = require("../assets/readaloud.js");
const { execFileSync } = require("child_process");
let n = 0, f = 0; const ok = (c, m) => { n++; if (!c) { f++; console.log("FAIL " + m); } };
const S = R.speakable;
ok(S("Call 000 now.") === "Call triple zero now.", "000");
ok(S("Lifeline is 13 11 14, any time.") === "Lifeline, thirteen eleven fourteen, any time.", "Lifeline");
ok(S("1800RESPECT is 1800 737 732") === "one eight hundred respect is one eight hundred, seven three seven, seven three two", "1800 groups");
ok(S("Kids Helpline (1800 55 1800)") === "Kids Helpline (one eight hundred, five five, one eight hundred)", "1800 55 1800");
ok(S("1300 766 491") === "one three hundred, seven six six, four nine one", "1300");
ok(S("text 0477 13 11 14") === "text zero four seven seven, thirteen eleven fourteen", "mobile + 13");
ok(S("(08) 8212 6933") === "zero eight, eight two one two, six nine three three", "landline");
ok(S("Settings > Accessibility") === "Settings, then Accessibility", "> path");
ok(S("Call 000 now") !== "Call 000 now" && !/\d/.test(S("Call 000 or Lifeline on 13 11 14")), "no digits left in crisis line");
// on-device voices only
const net = [{ name: "Google UK English Female", lang: "en-GB", localService: false }, { name: "Google US English", lang: "en-US", localService: false }];
ok(R.pickVoice(net, "en-AU", "A") === null, "network-only voices -> null (buttons hidden)");
ok(R.pickVoice([], "en-AU", "A") === null, "no voices -> null");
const loc = [{ name: "Daniel", lang: "en-GB", localService: true }, { name: "Karen", lang: "en-AU", localService: true }, { name: "Lee", lang: "en-AU", localService: true }, { name: "Google AU", lang: "en-AU", localService: false }, { name: "Amelie", lang: "fr-FR", localService: true }];
ok(R.pickVoice(loc, "en-AU", "A").name === "Karen", "A prefers local en-AU female");
ok(R.pickVoice(loc, "en-AU", "B").name === "Lee", "B prefers local en-AU male");
ok(R.pickVoice([{ name: "Amelie", lang: "fr-FR", localService: true }], "en-AU", "A") === null, "non-English local only -> null");
ok(R.pickVoice([{ name: "Moira", lang: "en-IE", localService: true }], "en-AU", "B").name === "Moira", "B with only a female local voice -> any local voice");
ok(!R.pickVoice(loc, "en-AU", "A").name.startsWith("Google"), "never a network voice");
// key() matches tools/ra.py key()
const texts = ["Call 000 now if you or anyone else is in danger.", "Kai is a recovery buddy, not a person.", "It’s “quoted” – dash", "  spaced\n text  "];
const py = JSON.parse(execFileSync("python3", ["-c", "import sys,json;sys.path.insert(0,'tools');import ra;print(json.dumps([ra.key(t) for t in json.load(sys.stdin)]))"], { input: JSON.stringify(texts), cwd: __dirname + "/.." }).toString());
texts.forEach((t, i) => ok(R.key(t) === py[i], "key matches python for " + JSON.stringify(t)));
// manifest: every spoken script equals speakable(text); no cross-country numbers
const m = require("./audio-manifest.json");
m.lines.forEach(l => ok(l.spoken === S(l.text), "spoken script current: " + l.id));
m.lines.forEach(l => ok(!/\b(911|988)\b|nine one one|nine eight eight/.test(l.text + l.spoken), "no US numbers: " + l.id));
m.lines.forEach(l => ok(l.clips.A && l.clips.B, "both voices: " + l.id));
console.log(`readaloud unit: ${n - f}/${n} passed`); process.exit(f ? 1 : 0);
