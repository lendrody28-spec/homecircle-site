// Unit tests for assets/readaloud.js (node tools/test_readaloud.js)
const R = require("../assets/readaloud.js");
const { execFileSync } = require("child_process");
let n = 0, f = 0; const ok = (c, m) => { n++; if (!c) { f++; console.log("FAIL " + m); } };
const S = R.speakable;
ok(S("Call 000 now.") === "Please call triple zero now.", "000: sentence-start Call becomes Please call");
ok(S("Danger? Call 000 now.") === "Danger? Please call triple zero now.", "Please call after a full stop");
ok(S("or call 000 now.") === "or call triple zero now.", "mid-sentence call 000 unchanged");
ok(S("Call 000 Call Lifeline 13 11 14") === "Please call triple zero. Call Lifeline thirteen eleven fourteen", "two call buttons -> two sentences");
ok(S("Lifeline is 13 11 14, any time.") === "Lifeline, thirteen eleven fourteen, any time.", "Lifeline");
ok(S("1800RESPECT is 1800 737 732") === "one eight hundred respect is one eight hundred, seven three seven, seven three two", "1800 groups");
ok(S("Kids Helpline (1800 55 1800) is for") === "Kids Helpline, on one eight hundred, five five, eighteen hundred, is for", "1800 55 1800 (digits + eighteen hundred, parens read as 'on')");
ok(S("call 1800 177 833") === "call one eight hundred, one seven seven, eight three three", "1800 177 833");
ok(S("1300 766 491") === "thirteen hundred, seven six six, four nine one", "1300");
ok(S("1300 22 4636") === "thirteen hundred, two two, four six three six", "1300 with 2-digit group read as digits");
ok(S("text 0477 13 11 14") === "text zero four seven seven, thirteen eleven fourteen", "mobile + 13");
ok(S("(08) 8212 6933") === "zero eight, eight two one two, six nine three three", "landline");
ok(S("Settings > Accessibility") === "Settings, then Accessibility", "> path");
ok(S("see a GP. GPs can help") === "see a G P. G Ps can help", "GP");
ok(S("Kai can miss things") === "Kye can miss things", "Kai -> Kye");
ok(S("Free · 24/7 · Phone") === "Free, twenty-four seven, Phone", "· not read");
ok(S("Call 000 now") !== "Call 000 now" && !/\d/.test(S("Call 000 or Lifeline on 13 11 14")), "no digits left in crisis line");
// textOf / chunksOf on a tiny fake DOM
function el(name, cls, kids) { const e = { nodeType: 1, nodeName: name, classList: { _c: (cls || "").split(" ").filter(Boolean), contains(c) { return this._c.includes(c); }, add(c) { this._c.push(c); }, remove(c) { this._c = this._c.filter(x => x !== c); } }, kids: kids || [] };
  e.kids.forEach((k, i) => { if (typeof k === "string") e.kids[i] = k = { nodeType: 3, nodeValue: k }; k.nextSibling = null; if (i) e.kids[i - 1].nextSibling = k; });
  e.firstChild = e.kids[0] || null; e.children = e.kids.filter(k => k.nodeType === 1); return e; }
const card = el("DIV", "card", [el("SPAN", "tag", ["Guide"]), el("H3", "", ["QLife"]), el("P", "", ["Free · peer support"]), el("DETAILS", "", [el("SUMMARY", "", ["More info"]), el("P", "", ["Hours 3pm to 9pm"])])]);
const wrap = el("DIV", "wrap", [el("DIV", "ra-bar", ["x"]), el("H1", "", ["Get help now"]), el("DIV", "grid", [card]), el("P", "ra-skip", ["skip"])]);
const ch = R.chunksOf(wrap);
ok(JSON.stringify(ch) === JSON.stringify(["Get help now.", "QLife. Free · peer support", "More info. Hours 3pm to 9pm"]), "chunksOf: heading full stop, no Guide label, card details split: " + JSON.stringify(ch));
ok(!/Guide/.test(ch.join(" ")) && !/·/.test(ch.map(S).join(" ")), "no Guide label or · in spoken text");
ok(R.textOf(el("H2", "", ["Done?"])) === "Done?", "heading with punctuation unchanged");
// player: audioSession -> playback + Web Audio, unlocked synchronously in the tap
(function () {
  const log = []; let ctxN = 0;
  function AC() { ctxN++; this.state = "suspended"; this.resume = () => { log.push("resume"); this.state = "running"; return Promise.resolve(); }; }
  const env = { navigator: { audioSession: { type: "auto" } }, AudioContext: AC, Audio: function () { log.push("audio-el"); } };
  const P = R.makePlayer(env);
  ok(P.unlock() === "webaudio", "audioSession present -> webaudio");
  ok(env.navigator.audioSession.type === "playback", "audioSession.type set to playback");
  ok(ctxN === 1 && log[0] === "resume", "AudioContext created and resumed synchronously in unlock");
  P.unlock(); ok(ctxN === 1, "one AudioContext reused");
  ok(!log.includes("audio-el"), "no audio element on the webaudio path");
})();
// player: no audioSession -> HTMLAudioElement primed synchronously with a silent clip, then reused
(function () {
  const els = [];
  function Audio() { this.src = ""; this.plays = []; this.play = () => { this.plays.push(this.src); return Promise.resolve(); }; this.pause = () => {}; els.push(this); }
  const env = { navigator: {}, AudioContext: function () { throw new Error("should not be used"); }, Audio, URL: { createObjectURL: () => "blob:x" } };
  const P = R.makePlayer(env);
  ok(P.unlock() === "element", "no audioSession -> element");
  ok(els.length === 1 && /^data:audio\/wav/.test(els[0].plays[0] || ""), "element primed with silent data:audio/wav inside the tap");
  P.play({}, () => {}, () => {});
  ok(els.length === 1 && els[0].plays[1] === "blob:x", "same primed element plays the clip");
})();
// pause/resume: Web Audio suspends and resumes the same context (keeps the place)
(function () {
  const log = [];
  function AC() { this.state = "suspended"; this.resume = () => { log.push("resume"); return Promise.resolve(); }; this.suspend = () => { log.push("suspend"); return Promise.resolve(); }; }
  const P = R.makePlayer({ navigator: { audioSession: {} }, AudioContext: AC });
  P.unlock(); log.length = 0; P.pause(); P.resume();
  ok(log.join() === "suspend,resume", "webaudio pause -> suspend, resume -> resume");
})();
// pause/resume: element pauses and plays again without changing src (keeps the place)
(function () {
  let el;
  function Audio() { el = this; this.src = ""; this.n = 0; this.paused = 0; this.play = () => { this.n++; return Promise.resolve(); }; this.pause = () => { this.paused++; }; }
  const P = R.makePlayer({ navigator: {}, Audio, URL: { createObjectURL: () => "blob:clip" } });
  P.unlock(); P.play({}, () => {}, () => {});
  const n = el.n; P.pause(); ok(el.paused >= 1 && el.src === "blob:clip", "element pause keeps src");
  P.resume(); ok(el.n === n + 1 && el.src === "blob:clip", "element resume plays the same src");
})();
// pause handler: speechSynthesis pause/resume and stop clears the pause
(function () {
  const src = require("fs").readFileSync(__dirname + "/../assets/readaloud.js", "utf8");
  ok(/synth\.pause\(\)/.test(src) && /synth\.resume\(\)/.test(src), "device voice uses speechSynthesis pause/resume");
  ok(/if \(t === pauseBtn\) \{ togglePause\(\); return; \}/.test(src), "pause toggle handled before any other read-aloud click");
  ok(/aria-pressed", paused/.test(src) && /"Resume" : "Pause"/.test(src), "pause button swaps label and aria-pressed");
  const safety = src.slice(src.indexOf("/* SAFETY"));
  ok(/tel:.*#kai-notsafe/.test(safety.split("\n")[1] + safety.split("\n")[2]) && /if \(a\) stop\(\)/.test(safety), "call links and I'm not safe still stop playback");
  ok(/function chosen\(\) \{ return "B"; \}/.test(src) && /localStorage\.removeItem\("hc\.ra\.voice\.v1"\)/.test(src), "chosen is always B; clears stored preference");
  ok(/function voicePicker\(\)/.test(src) && /g\.hidden = true/.test(src) && !/data-ra-voice/.test(src) && !/data-ra-sample/.test(src), "voice picker is a hidden stub; no A/B controls");
})();
// click handler calls P.unlock() before preload/fetch
(function () {
  const src = require("fs").readFileSync(__dirname + "/../assets/readaloud.js", "utf8");
  const h = src.slice(src.indexOf('document.addEventListener("click", function (e) {'));
  ok(h.indexOf("P.unlock()") > 0 && h.indexOf("P.unlock()") < h.indexOf("run(t"), "unlock() before run in the click handler");
})();
// python page_chunks mirrors chunksOf on help.html (text-level parity is also checked in the browser test)
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
const HELD = ["help.22", "help.37", "help.56"];
ok(Object.keys(m.voices).join() === "B" && !m.voices.A, "manifest ships Voice B only");
m.lines.forEach(l => ok(HELD.includes(l.id) ? !l.clips.B && l.clipsHeld && l.clipsHeld.B && !l.clipsHeld.A : !!(l.clips.B && !l.clips.A), "Voice B only (or held for a human listen): " + l.id));
const ca = m.lines.find(l => l.id === "kai.crisis.childAbuse");
ok(ca.clips.B.file === "1ef6b3b450e7.mp3" && !ca.clipsHeld, "childAbuse: own Voice B recording kept (human-listened OK by LJ)");
const fs = require("fs");
m.lines.forEach(l => Object.values(l.clipsHeld || {}).forEach(c => ok(!fs.existsSync(__dirname + "/../assets/audio/" + c.file), "held clip not in build: " + c.file)));
// no Voice A files shipped
ok(!fs.existsSync(__dirname + "/../assets/audio/licences/MeloTTS-MIT-LICENSE.txt"), "MeloTTS licence not shipped");
ok(fs.existsSync(__dirname + "/../assets/audio/licences/Kokoro-Apache-2.0-LICENSE.txt"), "Kokoro licence kept");
console.log(`readaloud unit: ${n - f}/${n} passed`); process.exit(f ? 1 : 0);
