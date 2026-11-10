// Read-aloud browser tests. Serves a copy of the built AU site on :8764 (SITE env).
let pw; try { pw = require('playwright-core'); } catch (e) { pw = require('/workspace/kaipw/node_modules/playwright-core'); }
const { chromium } = pw;
const fs = require('fs');
const exe = fs.readdirSync(process.env.HOME + '/.cache/ms-playwright').find(d => d.startsWith('chromium-'));
const BASE = process.env.RA_BASE || 'http://localhost:8764/';
process.env.SITE = process.env.SITE || require('path').resolve(__dirname, '..');   /* serve a copy: cd SITE && python3 -m http.server 8764 */
let n = 0, f = 0; const ok = (c, m) => { n++; if (!c) { f++; console.log('FAIL ' + m); } };
/* page.waitForFunction evals in the page and the site CSP blocks it. Poll with evaluate instead. */
async function until(p, pred, arg, timeout) {
  const t0 = Date.now();
  while (Date.now() - t0 < timeout) {
    if (await p.evaluate(pred, arg)) return true;
    await p.waitForTimeout(40);
  }
  return false;
}
// Mock speechSynthesis + media playback. mode: 'local' | 'network' | 'none'
const mock = mode => `(() => {
  const voices = ${JSON.stringify({ local: [{ name: 'Karen', lang: 'en-AU', localService: true, default: true }, { name: 'Lee', lang: 'en-AU', localService: true }, { name: 'Google UK English Female', lang: 'en-GB', localService: false }], network: [{ name: 'Google UK English Female', lang: 'en-GB', localService: false }, { name: 'Google US English', lang: 'en-US', localService: false }], none: [] })}[${JSON.stringify(mode)}];
  window.__spoken = []; window.__played = []; window.__cancel = 0;
  const ss = new EventTarget(); let late = voices; let ready = false;
  ss.getVoices = () => ready ? late : [];
  ss.speak = u => { window.__spoken.push({ text: u.text, voice: u.voice && u.voice.name, local: u.voice && u.voice.localService }); setTimeout(() => u.onend && u.onend(), window.__fast ? 5 : 400); };
  ss.cancel = () => { window.__cancel++; };
  ss.pause = () => { window.__ssPause = (window.__ssPause || 0) + 1; }; ss.resume = () => { window.__ssResume = (window.__ssResume || 0) + 1; };
  Object.defineProperty(window, 'speechSynthesis', { value: ss });
  window.SpeechSynthesisUtterance = function (t) { this.text = t; };
  setTimeout(() => { ready = true; ss.dispatchEvent(new Event('voiceschanged')); }, 300);  /* late voiceschanged */
  HTMLMediaElement.prototype.play = function () { if (String(this.src).startsWith('data:')) { window.__primed = (window.__primed || 0) + 1; return Promise.resolve(); } window.__played.push(this.src); window.__playing = this; const a = this; a.__t = setTimeout(() => a.onended && a.onended(), window.__fast ? 5 : 1500); return Promise.resolve(); };
  Object.defineProperty(HTMLMediaElement.prototype, 'onerror', { set() {}, get() { return null; }, configurable: true });  /* headless Chromium has no AAC decoder */
  HTMLMediaElement.prototype.pause = function () { clearTimeout(this.__t); window.__paused = (window.__paused || 0) + 1; };
})();`;
async function open(b, path, mode, vp, opts = {}) {
  const ctx = await b.newContext({ viewport: vp || { width: 1280, height: 800 } });
  await ctx.addInitScript(mock(mode));
  const p = await ctx.newPage(); p.errs = []; p.on('pageerror', e => p.errs.push(e.message));
  p.audioReqs = []; p.on('request', r => { if (/assets\/audio\/.*\.(m4a|mp3)/.test(r.url())) p.audioReqs.push(r.url().split('/').pop()); });
  p.offsite = []; p.on('request', r => { if (!r.url().startsWith(BASE) && !r.url().startsWith('data:') && !r.url().startsWith('blob:')) p.offsite.push(r.url()); });
  if (opts.block) await p.route(opts.block, r => r.abort());
  await p.goto(BASE + path); await p.waitForTimeout(500);
  return { ctx, p };
}
const manifest = JSON.parse(fs.readFileSync(process.env.SITE + '/tools/audio-manifest.json'));
const shared = new Set(); manifest.lines.forEach(l => { for (const v in l.clips) if (l.clips[v].sharedFrom) shared.add(l.clips[v].file); });
const fileVoice = {}; manifest.lines.forEach(l => { for (const v in l.clips) if (!l.clips[v].sharedFrom) fileVoice[l.clips[v].file] = v; });
(async () => {
  const b = await chromium.launch({ executablePath: process.env.HOME + '/.cache/ms-playwright/' + exe + '/chrome-linux64/chrome' });
  // 1. Help page: clips, network-only device voices (clips still work), order, preload, stop on call
  for (const vp of [{ width: 1280, height: 800 }, { width: 375, height: 667 }, { width: 320, height: 640 }]) {
    if (vp.width === 1280) { const o = await open(b, 'help.html', 'network', vp);   // 3 cards held back pending a human listen have no clip, so Help needs a device voice
      ok(!(await o.p.locator('.ra-bar .ra-btn').isVisible()), 'help: read button hidden when cards lack clips and device voices are network-only'); await o.ctx.close(); }
    const { ctx, p } = await open(b, 'help.html', 'local', vp); const t = `help @${vp.width}`;
    const btn = p.locator('.ra-bar .ra-btn');
    ok(await btn.isVisible(), `${t}: read button visible`);
    ok(await p.$eval('.ra-note', e => e.textContent) === "Read aloud plays recordings stored on this website, or your device's own voice. Nothing you read or type is sent anywhere.", `${t}: Hale note`);
    const box = await btn.boundingBox(); ok(box.height >= 44 && box.width >= 44, `${t}: 44px read button ${box.width}x${box.height}`);
    ok(await p.locator('.ra-bar .ra-voice,.ra-bar .ra-sample').count() === 0 && !(await p.locator('.ra-bar .ra-voices').isVisible()), `${t}: no voice picker`);
    ok(await p.evaluate(() => document.documentElement.scrollWidth <= window.innerWidth), `${t}: no horizontal scroll`);
    // DOM / tab order: every call link in #now precedes the read button
    ok(await p.evaluate(() => { const r = document.querySelector('.ra-bar .ra-btn'); return [...document.querySelectorAll('#now a[href^="tel:"]')].every(a => a.compareDocumentPosition(r) & Node.DOCUMENT_POSITION_FOLLOWING); }), `${t}: call buttons before read button in DOM`);
    const order = []; await p.focus('body'); for (let i = 0; i < 40; i++) { await p.keyboard.press('Tab'); const d = await p.evaluate(() => { const a = document.activeElement; return a.classList.contains('ra-btn') ? 'READ' : (a.getAttribute('href') || '').startsWith('tel:') ? 'TEL' : ''; }); if (d) order.push(d); if (d === 'READ') break; }
    ok(order.indexOf('TEL') > -1 && order.indexOf('TEL') < order.indexOf('READ'), `${t}: tab order ${order}`);
    ok(p.audioReqs.length === 0, `${t}: no clip loaded before a tap`);
    if (vp.width === 1280) {   // page chunks: browser chunksOf() == tools/ra.py page_chunks() (same text, same keys)
      const js = await p.evaluate(() => HCReadAloud.chunksOf(document.querySelector('main .wrap')));
      const py = JSON.parse(require('child_process').execFileSync('python3', ['-c', "import sys,json;sys.path.insert(0,'tools');import ra;t=open('help.html').read();a=t.index('<main id=\"main\"><div class=\"wrap\">\\n')+len('<main id=\"main\"><div class=\"wrap\">\\n');b=t.index('\\n</div></main>');print(json.dumps(ra.page_chunks(t[a:b])))"], { cwd: process.env.SITE }).toString());
      ok(JSON.stringify(js) === JSON.stringify(py), `${t}: browser chunks match python (${js.length} vs ${py.length})`);
      const sp = await p.evaluate(x => x.map(HCReadAloud.speakable), js);
      ok(sp.every(x => !/·/.test(x)) && !js.some(x => /\bGuide\b(?! to)/.test(x.split('.')[0] || '')) , `${t}: no separators or Guide labels read aloud ${JSON.stringify(sp.filter(x => /·/.test(x) || /\bGuide\b(?! to)/.test(x.split('.')[0] || '')).map(x=>x.slice(0,80)))}`);
    }
    await btn.click(); await p.waitForTimeout(800);
    ok(await btn.getAttribute('aria-pressed') === 'true' && /Stop/.test(await btn.innerText()) && await btn.getAttribute('aria-label') === 'Stop reading', `${t}: toggles to Stop`);
    const vB = p.audioReqs.map(f => fileVoice[f]);
    ok(p.audioReqs.length > 20 && vB.every(v => v === 'B'), `${t}: first tap preloads all Voice B clips in one go (${p.audioReqs.length})`);
    ok((await p.evaluate(() => window.__played.length)) >= 1 && (await p.evaluate(() => window.__spoken.length)) === 0, `${t}: plays a clip, no device speech`);
    // Pause / Play: one normal button under Stop, 44px, text label, keyboard, no focus trap
    { const pb = p.locator('.ra-pause');
      ok(await pb.isVisible(), `${t}: Pause button shown while reading`);
      const pbb = await pb.boundingBox(); ok(pbb.height >= 44 && pbb.width >= 44, `${t}: Pause 44px ${pbb.width}x${pbb.height}`);
      ok(await pb.innerText() === 'Pause' && await pb.getAttribute('aria-pressed') === 'false' && await pb.getAttribute('aria-label') === 'Pause reading', `${t}: Pause label`);
      ok(await pb.evaluate(e => e.tagName === 'BUTTON' && e.getAttribute('type') === 'button' && !e.closest('dialog')), `${t}: Pause is a normal button`);
      { const pos = await p.evaluate(() => { const b = document.querySelector('.ra-pause'); const stop = document.querySelector('.ra-bar .ra-btn'); return { inMain: !!b.closest('main'), afterStop: !!(b.compareDocumentPosition(stop) & Node.DOCUMENT_POSITION_PRECEDING) }; }); ok(pos.inMain && pos.afterStop, `${t}: Pause sits with Stop ${JSON.stringify(pos)}`); }
      if (vp.width <= 375) {
        const lay = await p.evaluate(() => {
          const rect = e => e && e.getBoundingClientRect();
          const pb = rect(document.querySelector('.ra-pause'));
          const stop = rect(document.querySelector('.ra-bar .ra-btn'));
          const hit = (a, b) => a && b && a.width > 0 && b.width > 0 && a.left < b.right - 0.5 && b.left < a.right - 0.5 && a.top < b.bottom - 0.5 && b.top < a.bottom - 0.5;
          const crisis = [...document.querySelectorAll('#now a[href^="tel:"], #help-pill, #kai-notsafe')].map(rect);
          return { sw: document.documentElement.scrollWidth <= window.innerWidth, under: !!(pb && stop && pb.top >= stop.bottom - 1), overlap: crisis.some(c => hit(pb, c)), h: pb && Math.round(pb.height) };
        });
        ok(lay.sw && lay.under && !lay.overlap, `${t}: Pause under Stop, no horizontal scroll, crisis controls not covered ${JSON.stringify(lay)}`);
      }
      const playing = await p.evaluate(() => window.__playing && window.__playing.src), n0 = await p.evaluate(() => window.__played.length), z0 = await p.evaluate(() => window.__paused || 0);
      await pb.click(); await p.waitForTimeout(100);
      ok(await pb.innerText() === 'Play' && await pb.getAttribute('aria-pressed') === 'true' && await pb.getAttribute('aria-label') === 'Play reading', `${t}: toggles to Play`);
      ok((await p.evaluate(() => window.__paused || 0)) > z0 && await btn.getAttribute('aria-pressed') === 'true', `${t}: paused, Stop still there`);
      await p.waitForTimeout(1700);
      ok((await p.evaluate(() => window.__played.length)) === n0, `${t}: nothing new plays while paused`);
      await pb.focus(); await p.keyboard.press('Tab');
      ok(await p.evaluate(() => !document.activeElement.classList.contains('ra-pause')), `${t}: Tab leaves Pause (no focus trap)`);
      await pb.focus(); await p.keyboard.press('Enter'); await p.waitForTimeout(100);
      const pl = await p.evaluate(() => window.__played);
      ok(await pb.innerText() === 'Pause' && await pb.getAttribute('aria-pressed') === 'false' && pl.length === n0 + 1 && pl[pl.length - 1] === playing, `${t}: Enter resumes the same clip (keeps the place)`);
      if (vp.width <= 375) ok(await p.evaluate(() => document.documentElement.scrollWidth <= window.innerWidth), `${t}: no horizontal scroll with Pause`); }
    // call link stays clickable while audio plays, and stops it
    await p.evaluate(() => { document.querySelectorAll('a[href^="tel:"]').forEach(a => a.addEventListener('click', e => e.preventDefault())); });
    const c0 = await p.evaluate(() => window.__paused || 0);
    await p.click('#now a[href="tel:000"]'); await p.waitForTimeout(200);
    ok(await btn.getAttribute('aria-pressed') === 'false' && (await p.evaluate(() => window.__paused || 0)) > c0, `${t}: tapping Call 000 stops reading`);
    ok(await p.locator('.ra-pause').isHidden(), `${t}: Pause hidden after a call link stops reading`);
    if (vp.width <= 375) {
      await p.click('#help-pill');
      const dlg = await p.evaluate(() => { const d = document.getElementById('help-dialog'); return { open: !!d.open, t: d.innerText, sw: document.documentElement.scrollWidth <= window.innerWidth }; });
      ok(dlg.open && /Call 000/.test(dlg.t) && /Lifeline/.test(dlg.t) && /13 11 14/.test(dlg.t) && dlg.sw, `${t}: Help opens Call 000 and Lifeline 13 11 14`);
      await p.keyboard.press('Escape');
    }
    ok(p.offsite.length === 0, `${t}: no off-site requests ${p.offsite}`);
    ok(p.errs.length === 0, `${t}: no errors ${p.errs}`);
    if (vp.width !== 320) await p.screenshot({ path: `/workspace/shots/readaloud-help-${vp.width}.png` });
    await ctx.close();
  }
  // 2. Voice B only: no picker; a stored Voice A preference is cleared and ignored
  { const ctx = await b.newContext({ viewport: { width: 1280, height: 800 } });
    await ctx.addInitScript(() => { localStorage.setItem('hc.ra.voice.v1', 'A'); });
    await ctx.addInitScript(mock('local'));
    const p = await ctx.newPage(); p.audioReqs = []; p.on('request', r => { if (/assets\/audio\/.*\.(m4a|mp3)/.test(r.url())) p.audioReqs.push(r.url().split('/').pop()); });
    await p.goto(BASE + 'help.html'); await p.waitForTimeout(500);
    ok(await p.locator('.ra-bar .ra-voice,.ra-bar .ra-sample').count() === 0 && !(await p.locator('.ra-bar .ra-voices').isVisible()), 'no voice picker on the page');
    ok(await p.evaluate(() => localStorage.getItem('hc.ra.voice.v1')) === null, 'stored Voice A preference cleared');
    ok(await p.evaluate(() => document.cookie === ''), 'no cookie');
    await p.click('.ra-bar .ra-btn'); await p.waitForTimeout(800);
    ok(p.audioReqs.length > 20 && p.audioReqs.every(f => fileVoice[f] === 'B' || shared.has(f)), 'first tap loads Voice B only even after a stored A preference');
    await ctx.close(); }
  // 3. Crisis reply plays Voice B clip; call / I'm not safe still stop
  { const emB = manifest.lines.find(l => l.id === 'kai.crisis.emergency').clips.B.file;
    const { ctx, p } = await open(b, 'index.html', 'none');
    await p.click('#kai-bubble'); await p.waitForSelector('#kai-panel:not([hidden])');
    await p.click('#kai-notsafe');
    const r = await p.evaluate(() => ({ live: document.getElementById('kai-live').textContent, cls: document.activeElement.className, name: document.activeElement.getAttribute('aria-label') }));
    ok(/from-kai/.test(r.cls) && r.name === "Kai's reply" && r.live === 'Get help now: call 000 or Lifeline 13 11 14', `Kai crisis reply focus and live region unchanged ${JSON.stringify(r)}`);
    ok(p.audioReqs.length === 0, 'no clip loads from pressing I\'m not safe (no autoplay)');
    const rb = p.locator('#kai-after .ra-btn');
    ok(await rb.isVisible(), 'reply read button shown');
    ok(await p.evaluate(() => { const r = document.querySelector('#kai-after .ra-btn'); const tels = [...document.querySelectorAll('#kai-notsafe, #kai-crisis a[href^="tel:"], #kai-after a[href^="tel:"]')]; return tels.length >= 3 && tels.every(a => a.compareDocumentPosition(r) & Node.DOCUMENT_POSITION_FOLLOWING); }), 'reply read button after I\'m not safe and every call button');
    const bb = await rb.boundingBox(); ok(bb.height >= 44 && bb.width >= 44, 'reply read button 44px');
    await rb.click(); await p.waitForTimeout(900);
    const played = await p.evaluate(() => window.__played);
    ok(played.length === 1 && played[0].startsWith('blob:') && (await p.evaluate(() => window.__primed)) >= 1, 'crisis reply plays a Voice B clip through the element primed in the tap ' + played);
    ok(p.audioReqs.includes(emB) && p.audioReqs.every(f => fileVoice[f] === 'B' || shared.has(f)), 'crisis preload is Voice B only (' + p.audioReqs.length + ')');
    ok((await p.evaluate(() => window.__spoken.length)) === 0, 'no device speech needed');
    ok(await p.locator('#kai-notsafe').isEnabled(), 'I\'m not safe still clickable while playing');
    ok(await p.evaluate(() => { const b = document.querySelector('#kai-after .ra-pause'); return !!b && !b.hidden && b.previousElementSibling === document.querySelector('#kai-after .ra-btn'); }), 'Kai: Pause under the reply, after its read button');
    await p.click('#kai-notsafe'); await p.waitForTimeout(200);
    ok(await p.$eval('#kai-after .ra-btn', e => e.getAttribute('aria-pressed')) === 'false' || (await p.evaluate(() => window.__paused || 0)) > 0, 'I\'m not safe stops reading');
    ok(await p.evaluate(() => { const b = document.querySelector('.ra-pause'); return !b || b.hidden; }), 'I\'m not safe hides Pause (playback fully stopped)');
    const fo = p.locator('.kai-ra .ra-btn'); ok(await fo.count() === 1, 'first-open line has a read button');
    ok(p.errs.length === 0, 'Kai: no errors ' + p.errs);
    await ctx.close(); }
  // 4. Page with no clips (twelve steps): on-device fallback only
  { const { ctx, p } = await open(b, 'twelve-steps.html', 'network');
    ok(!(await p.locator('.ra-bar .ra-btn').isVisible()), 'twelve steps: hidden when only network voices');
    ok(!(await p.evaluate(() => document.documentElement.classList.contains('ra-on'))) || !(await p.locator('.ra-bar .ra-btn').isVisible()), 'twelve steps: ra-on off');
    await ctx.close(); }
  { const { ctx, p } = await open(b, 'twelve-steps.html', 'local');
    const btn = p.locator('.ra-bar .ra-btn'); ok(await btn.isVisible(), 'twelve steps: shown with a local voice (after late voiceschanged)');
    await btn.click(); await p.waitForTimeout(150);
    const sp = await p.evaluate(() => window.__spoken);
    ok(sp.length >= 1 && sp.every(s => s.local === true && s.voice === 'Lee'), 'device fallback uses local en-AU male voice (Voice B style) ' + JSON.stringify(sp[0]));
    ok(p.audioReqs.length === 0, 'twelve steps loads no clips');
    await p.click('.ra-pause', { timeout: 3000 }); await p.waitForTimeout(50);
    ok((await p.evaluate(() => window.__ssPause)) >= 1 && await p.locator('.ra-pause').innerText() === 'Play' && await p.locator('.ra-pause').getAttribute('aria-label') === 'Play reading' && await p.locator('.ra-pause').getAttribute('aria-pressed') === 'true', 'device voice: speechSynthesis.pause() labels Play');
    await p.click('.ra-pause'); await p.waitForTimeout(50);
    ok((await p.evaluate(() => window.__ssResume)) >= 1 && await p.locator('.ra-pause').innerText() === 'Pause', 'device voice: speechSynthesis.resume()');
    await ctx.close(); }
  { const { ctx, p } = await open(b, 'twelve-steps.html', 'none');
    ok(!(await p.locator('.ra-bar .ra-btn').isVisible()), 'twelve steps: hidden with no voices'); await ctx.close(); }
  // 5. Families pages: bar after the call strip; overdose: after the Call 000 section
  for (const pg of ['families/index.html', 'families/overdose.html', 'families/kids.html', 'support.html']) {
    if (!fs.existsSync(process.env.SITE + '/' + pg)) { ok(false, pg + ' missing'); continue; }
    const { ctx, p } = await open(b, pg, 'local', { width: 375, height: 667 });
    ok(await p.evaluate(() => { const r = document.querySelector('.ra-bar'); const tels = [...document.querySelectorAll('main a[href^="tel:"]')]; const first = tels[0]; return !!r && (!first || (first.compareDocumentPosition(r) & Node.DOCUMENT_POSITION_FOLLOWING)); }), pg + ': read bar after the first call link');
    ok(await p.locator('.ra-bar .ra-btn').isVisible(), pg + ': read button (device voice)');
    ok(await p.evaluate(() => document.documentElement.scrollWidth <= window.innerWidth), pg + ': no horizontal scroll at 375');
    ok(p.errs.length === 0, pg + ': no errors');
    if (pg === 'families/overdose.html') await p.screenshot({ path: '/workspace/shots/readaloud-overdose-375.png' });
    await ctx.close(); }
  // Kai at 375 / 320: Pause never covers the start buttons or the 000 strip
  for (const vp of [{ width: 375, height: 667 }, { width: 320, height: 640 }]) {
    const { ctx, p } = await open(b, 'index.html', 'network', vp);
    await p.click('#kai-bubble'); await p.waitForSelector('#kai-panel:not([hidden])');
    await p.click('.kai-ra .ra-btn'); await p.waitForTimeout(600);
    const lay = await p.evaluate(() => { const r = e => e && e.getBoundingClientRect(); const pb = r(document.querySelector('.ra-pause')); const stop = r(document.querySelector('.ra-btn[aria-pressed="true"]')); const hit = (a, b) => a && b && b.width && a.left < b.right && b.left < a.right && a.top < b.bottom && b.top < a.bottom;
      const others = [...document.querySelectorAll('#kai-start button, #kai-start a, #kai-crisis a, #kai-notsafe, #help-pill')].map(r);
      return { shown: !!pb && pb.width > 0, overlap: others.some(o => hit(pb, o)), under: !!(pb && stop && pb.top >= stop.bottom - 1), h: pb && pb.height, sw: document.documentElement.scrollWidth <= window.innerWidth }; });
    ok(lay.shown && !lay.overlap && lay.under && lay.h >= 44 && lay.sw, `Kai intro Pause @${vp.width}: under Stop, no overlap with Help / I'm not safe / 000 strip ${JSON.stringify(lay)}`);
    await p.screenshot({ path: `/workspace/shots/readaloud-kai-pause-${vp.width}.png` });
    await ctx.close(); }
  // Kai screenshots
  for (const vp of [{ width: 375, height: 667 }, { width: 1280, height: 800 }]) {
    const { ctx, p } = await open(b, 'index.html', 'network', vp);
    await p.click('#kai-bubble'); await p.waitForSelector('#kai-panel:not([hidden])');
    await p.screenshot({ path: `/workspace/shots/readaloud-kai-open-${vp.width}.png` });
    await p.click('#kai-notsafe'); await p.waitForTimeout(300);
    await p.locator('#kai-after .ra-btn').scrollIntoViewIfNeeded();
    await p.screenshot({ path: `/workspace/shots/readaloud-kai-crisis-${vp.width}.png` });
    await ctx.close(); }
  // Held back pending human listen: help.22/37/56 have no clips and fall back to the device's own voice
  { const held = manifest.lines.filter(l => l.clipsHeld && !Object.keys(l.clips).length);
    const ca = manifest.lines.find(l => l.id === 'kai.crisis.childAbuse');
    const ctx = await b.newContext({ viewport: { width: 375, height: 667 } });
    await ctx.addInitScript(() => { window.__fast = 1; localStorage.setItem('hc.ra.voice.v1', 'A'); }); await ctx.addInitScript(mock('local'));
    const p = await ctx.newPage(); const reqs = []; p.on('request', r => { if (/assets\/audio\//.test(r.url())) reqs.push(r.url().split('/').pop()); });
    await p.goto(BASE + 'help.html'); await p.waitForTimeout(500);
    const map = await p.evaluate(() => JSON.parse(document.getElementById('ra-clips').textContent));
    ok(!map.clips.A || !Object.keys(map.clips.A).length, 'page map has no Voice A clips');
    for (const l of held) {
      const k = await p.evaluate(t => HCReadAloud.key(t), l.text);
      ok(!map.clips.B[k], `held ${l.id}: no clip in page map`);
    }
    const kc = await p.evaluate(t => HCReadAloud.key(t), ca.text);
    ok(map.clips.B[kc] === ca.clips.B.file, `childAbuse: Voice B recording kept (${map.clips.B[kc]})`);
    await p.locator('.ra-bar .ra-btn').click();
    await until(p, n => window.__spoken.length >= n, held.length, 60000);
    await p.waitForTimeout(300);
    const spoken = await p.evaluate(() => window.__spoken);
    for (const l of held) { const s = spoken.find(x => x.text === l.spoken || x.text === l.text);
      ok(s && s.local, `held ${l.id}: read by device voice (${s && s.voice})`); }
    const heldFiles = held.flatMap(l => Object.values(l.clipsHeld).map(c => c.file));
    ok(!reqs.some(f => heldFiles.includes(f)), 'held: no held recording fetched');
    ok(spoken.length === held.length, `held: only held cards use device voice (${spoken.length})`);
    await ctx.close(); }
  // Real playback (no media mock): the clip must play under the site's CSP, one batch for the chosen voice only, no fallback
  { const man = JSON.parse(require('fs').readFileSync(require('path').join(process.env.SITE, 'tools/audio-manifest.json')));
    for (const [pg, sel] of [['help.html', '.ra-bar .ra-btn'], ['index.html', '.kai-ra .ra-btn']]) {
      const want = new Set(man.lines.map(l => l.clips.B && l.clips.B.file).filter(Boolean));
      const ctx = await b.newContext({ viewport: { width: 375, height: 667 } });
      await ctx.addInitScript(() => { localStorage.setItem('hc.ra.voice.v1', 'A');   // leftover A preference must be ignored; media is real
        const ss = new EventTarget(); ss.getVoices = () => [{ name: 'Lee', lang: 'en-AU', localService: true, default: true }]; ss.speak = () => {}; ss.cancel = () => {}; ss.pause = () => {}; ss.resume = () => {};
        Object.defineProperty(window, 'speechSynthesis', { value: ss }); window.SpeechSynthesisUtterance = function (t) { this.text = t; }; setTimeout(() => ss.dispatchEvent(new Event('voiceschanged')), 100); });
      const p = await ctx.newPage(); const csp = [], reqs = [], off = [];
      p.on('console', m => { if (/Content Security Policy/.test(m.text())) csp.push(m.text().slice(0, 120)); });
      p.on('request', r => { const u = r.url(); if (/assets\/audio\/.*\.mp3/.test(u)) reqs.push(u.split('/').pop()); if (!u.startsWith(BASE) && !/^(data|blob):/.test(u)) off.push(u); });
      await p.goto(BASE + pg); await p.waitForTimeout(500);
      if (sel.startsWith('.kai')) { await p.click('#kai-bubble'); await p.waitForTimeout(200); }
      await p.locator(sel).first().click(); await p.waitForTimeout(2500);
      ok(csp.length === 0, `real playback ${pg}: no CSP blocks ${csp}`);
      ok(reqs.length > 0 && reqs.every(f => want.has(f)), `real playback ${pg}: only Voice B batch fetched (${reqs.length} clips)`);
      ok(await p.locator('.ra-pause').isVisible(), `real playback ${pg}: still playing after 2.5 s (Pause shown)`);
      ok(off.length === 0, `real playback ${pg}: no off-site requests`);
      await ctx.close(); } }
  // A finished clip does not restart, and Play resumes from the paused position.
  for (const vp of [{ width: 375, height: 667 }, { width: 320, height: 640 }]) {
    const ctx = await b.newContext({ viewport: vp });
    await ctx.addInitScript(() => {
      window.__spoken = []; window.__played = []; window.__starts = []; window.__seeked = 0;
      const ss = new EventTarget();
      ss.getVoices = () => [{ name: 'Lee', lang: 'en-AU', localService: true, default: true }];
      ss.speak = u => { window.__spoken.push(u.text); setTimeout(() => u.onend && u.onend(), 5); };
      ss.cancel = () => {}; ss.pause = () => {}; ss.resume = () => {};
      Object.defineProperty(window, 'speechSynthesis', { value: ss });
      window.SpeechSynthesisUtterance = function (t) { this.text = t; };
      setTimeout(() => ss.dispatchEvent(new Event('voiceschanged')), 40);
      HTMLMediaElement.prototype.play = function () {
        if (String(this.src).startsWith('data:')) return Promise.resolve();
        const a = this;
        window.__played.push(a.src);
        window.__playing = a;
        window.__starts.push(a.__pos || 0);
        a.__tick = setInterval(() => { a.__pos = (a.__pos || 0) + 0.25; }, 30);
        return new Promise((res, rej) => { a.__rej = rej; a.__res = res; });
      };
      HTMLMediaElement.prototype.pause = function () { clearInterval(this.__tick); window.__paused = (window.__paused || 0) + 1; if (this.__rej) { const r = this.__rej; this.__rej = null; r(new Error('abort')); } };
      Object.defineProperty(HTMLMediaElement.prototype, 'currentTime', { configurable: true, get() { return this.__pos || 0; }, set(v) { this.__pos = v; window.__seeked++; } });
    });
    const p = await ctx.newPage(); p.errs = []; p.on('pageerror', e => p.errs.push(e.message));
    const off = []; p.on('request', r => { const u = r.url(); if (!u.startsWith(BASE) && !u.startsWith('data:') && !u.startsWith('blob:')) off.push(u); });
    await p.goto(BASE + 'index.html'); await p.waitForTimeout(400);
    await p.click('#kai-bubble'); await p.waitForSelector('#kai-panel:not([hidden])');
    await p.click('.kai-ra .ra-btn');
    await until(p, () => window.__played && window.__played.length >= 1 && window.__playing && window.__playing.currentTime > 0, null, 10000);
    const seek0 = await p.evaluate(() => window.__seeked || 0);
    await p.click('.ra-pause'); await p.waitForTimeout(80);
    const pausedAt = await p.evaluate(() => ({ t: window.__playing.currentTime, src: window.__playing.getAttribute('src'), label: document.querySelector('.ra-pause').textContent, pressed: document.querySelector('.ra-pause').getAttribute('aria-pressed'), name: document.querySelector('.ra-pause').getAttribute('aria-label'), seeked: window.__seeked || 0 }));
    ok(pausedAt.t > 0 && !!pausedAt.src && pausedAt.label === 'Play' && pausedAt.pressed === 'true' && pausedAt.name === 'Play reading' && pausedAt.seeked === seek0, `pause keeps position @${vp.width} ${JSON.stringify(pausedAt)}`);
    const nPlay = await p.evaluate(() => window.__played.length);
    await p.click('.ra-pause'); await p.waitForTimeout(40);
    const resumed = await p.evaluate(() => ({ starts: window.__starts.slice(), label: document.querySelector('.ra-pause').textContent, pressed: document.querySelector('.ra-pause').getAttribute('aria-pressed'), n: window.__played.length }));
    ok(resumed.label === 'Pause' && resumed.pressed === 'false' && resumed.n === nPlay + 1 && resumed.starts[0] === 0 && resumed.starts.length === 2 && resumed.starts[1] === pausedAt.t, `Play resumes from the paused position @${vp.width} ${JSON.stringify(resumed)} pausedAt ${pausedAt.t}`);
    const beforeEnd = await p.evaluate(() => window.__played.length);
    await p.evaluate(() => { const a = window.__playing; if (a && a.onended) a.onended(); });
    await p.waitForTimeout(50);
    const ended = await p.evaluate(() => { const a = window.__playing; return { attr: a ? a.getAttribute('src') : 'missing', loop: a ? a.loop : null, spoken: window.__spoken.length, played: window.__played.length, starts: window.__starts.length }; });
    ok(ended.attr == null && ended.loop === false && ended.spoken === 0 && ended.played === beforeEnd && ended.starts === resumed.starts.length, `clip ends without restarting @${vp.width} ${JSON.stringify(ended)}`);
    await p.evaluate(() => { const a = window.__playing; if (!a) return; const end = a.onended, err = a.onerror, rej = a.__rej; if (end) end(); if (err) err(); if (rej) rej(new Error('late')); if (a.getAttribute('src')) a.play(); });
    await p.waitForTimeout(40);
    const after = await p.evaluate(() => ({ spoken: window.__spoken.length, starts: window.__starts.length, played: window.__played.length }));
    ok(after.spoken === 0 && after.starts === resumed.starts.length && after.played === beforeEnd, `second ended/error does not read the line again @${vp.width} ${JSON.stringify(after)}`);
    ok(await p.evaluate(() => document.documentElement.scrollWidth <= window.innerWidth), `index @${vp.width}: no horizontal scroll`);
    ok(!off.some(u => /updates\.json|google-analytics|googletagmanager/.test(u)) && off.length === 0, `index @${vp.width}: no off-site or updates.json request ${off}`);
    ok(p.errs.length === 0, `end/pause @${vp.width}: no errors ${p.errs}`);
    await ctx.close();
  }
  for (const vp of [{ width: 320, height: 640 }, { width: 375, height: 667 }]) {
    for (const pg of ['index.html', 'support.html']) {
      const { ctx, p } = await open(b, pg, 'local', vp);
      ok(await p.evaluate(() => document.documentElement.scrollWidth <= window.innerWidth), `${pg} @${vp.width}: no horizontal scroll`);
      ok(await p.evaluate(() => !performance.getEntriesByType('resource').some(e => /updates\.json/.test(e.name))), `${pg}: updates.json is not fetched`);
      ok(await p.evaluate(() => document.body.innerText.includes("Where we're at") && document.body.innerText.includes('homecirclerecovery.com') && document.body.innerText.includes('Where HomeCircle is going')), `${pg}: status wording on the page`);
      ok(await p.evaluate(() => { const sec = document.querySelector('section.hc-updates'); return !!sec && sec.innerText.includes('homecirclerecovery.com') && !sec.querySelector('a[href*="homecirclerecovery.com"]'); }), `${pg}: US domain in the status section is not a link`);
      await p.click('#help-pill');
      const dlg = await p.evaluate(() => { const d = document.getElementById('help-dialog'); return { open: !!d.open, t: d.innerText }; });
      ok(dlg.open && /Call 000/.test(dlg.t) && /Lifeline/.test(dlg.t) && /13 11 14/.test(dlg.t), `${pg} @${vp.width}: Help opens Call 000 and Lifeline`);
      ok(p.offsite.length === 0, `${pg}: no off-site requests`);
      await ctx.close();
    }
  }
  await b.close(); console.log(`readaloud browser: ${n - f}/${n} passed`); process.exit(f ? 1 : 0);
})().catch(err => { console.error(err); process.exit(1); });
