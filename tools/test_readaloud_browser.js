// Read-aloud browser tests. Serves a copy of the built AU site on :8764 (SITE env).
let pw; try { pw = require('playwright-core'); } catch (e) { pw = require('/workspace/kaipw/node_modules/playwright-core'); }
const { chromium } = pw;
const fs = require('fs');
const exe = fs.readdirSync(process.env.HOME + '/.cache/ms-playwright').find(d => d.startsWith('chromium-'));
const BASE = process.env.RA_BASE || 'http://localhost:8764/';
process.env.SITE = process.env.SITE || require('path').resolve(__dirname, '..');   /* serve a copy: cd SITE && python3 -m http.server 8764 */
let n = 0, f = 0; const ok = (c, m) => { n++; if (!c) { f++; console.log('FAIL ' + m); } };
// Mock speechSynthesis + media playback. mode: 'local' | 'network' | 'none'
const mock = mode => `(() => {
  const voices = ${JSON.stringify({ local: [{ name: 'Karen', lang: 'en-AU', localService: true, default: true }, { name: 'Lee', lang: 'en-AU', localService: true }, { name: 'Google UK English Female', lang: 'en-GB', localService: false }], network: [{ name: 'Google UK English Female', lang: 'en-GB', localService: false }, { name: 'Google US English', lang: 'en-US', localService: false }], none: [] })}[${JSON.stringify(mode)}];
  window.__spoken = []; window.__played = []; window.__cancel = 0;
  const ss = new EventTarget(); let late = voices; let ready = false;
  ss.getVoices = () => ready ? late : [];
  ss.speak = u => { window.__spoken.push({ text: u.text, voice: u.voice && u.voice.name, local: u.voice && u.voice.localService }); setTimeout(() => u.onend && u.onend(), 400); };
  ss.cancel = () => { window.__cancel++; };
  ss.pause = () => { window.__ssPause = (window.__ssPause || 0) + 1; }; ss.resume = () => { window.__ssResume = (window.__ssResume || 0) + 1; };
  Object.defineProperty(window, 'speechSynthesis', { value: ss });
  window.SpeechSynthesisUtterance = function (t) { this.text = t; };
  setTimeout(() => { ready = true; ss.dispatchEvent(new Event('voiceschanged')); }, 300);  /* late voiceschanged */
  HTMLMediaElement.prototype.play = function () { if (String(this.src).startsWith('data:')) { window.__primed = (window.__primed || 0) + 1; return Promise.resolve(); } window.__played.push(this.src); window.__playing = this; const a = this; a.__t = setTimeout(() => a.onended && a.onended(), 1500); return Promise.resolve(); };
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
const fileVoice = {}; manifest.lines.forEach(l => { for (const v in l.clips) fileVoice[l.clips[v].file] = v; });
(async () => {
  const b = await chromium.launch({ executablePath: process.env.HOME + '/.cache/ms-playwright/' + exe + '/chrome-linux64/chrome' });
  // 1. Help page: clips, network-only device voices (clips still work), order, preload, stop on call
  for (const vp of [{ width: 1280, height: 800 }, { width: 375, height: 667 }, { width: 320, height: 640 }]) {
    const { ctx, p } = await open(b, 'help.html', 'network', vp); const t = `help @${vp.width}`;
    const btn = p.locator('.ra-bar .ra-btn');
    ok(await btn.isVisible(), `${t}: read button visible with clips even when device voices are network-only`);
    ok(await p.$eval('.ra-note', e => e.textContent) === "Read aloud plays recordings stored on this website, or your device's own voice. Nothing you read or type is sent anywhere.", `${t}: Hale note`);
    const box = await btn.boundingBox(); ok(box.height >= 44 && box.width >= 44, `${t}: 44px read button ${box.width}x${box.height}`);
    for (const s of await p.$$('.ra-bar .ra-voice,.ra-bar .ra-sample')) { const bb = await s.boundingBox(); ok(bb && bb.height >= 44 && bb.width >= 44, `${t}: 44px voice control`); }
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
      ok(js.every(x => !/·/.test(x)) && !js.some(x => /\bGuide\b(?! to)/.test(x.split('.')[0] || '')) , `${t}: no separators or Guide labels in chunks`);
    }
    await btn.click(); await p.waitForTimeout(800);
    ok(await btn.getAttribute('aria-pressed') === 'true' && /Stop/.test(await btn.innerText()) && await btn.getAttribute('aria-label') === 'Stop reading', `${t}: toggles to Stop`);
    const vA = p.audioReqs.map(f => fileVoice[f]);
    ok(p.audioReqs.length > 20 && vA.every(v => v === 'A'), `${t}: first tap preloads all Voice A clips in one go (${p.audioReqs.length}) and none of B`);
    ok((await p.evaluate(() => window.__played.length)) >= 1 && (await p.evaluate(() => window.__spoken.length)) === 0, `${t}: plays a clip, no device speech`);
    // Pause / Resume: one toggle under the section being read, 44px, text label, keyboard
    { const pb = p.locator('.ra-pause');
      ok(await pb.isVisible(), `${t}: Pause button shown while reading`);
      const pbb = await pb.boundingBox(); ok(pbb.height >= 44 && pbb.width >= 44, `${t}: Pause 44px ${pbb.width}x${pbb.height}`);
      ok(await pb.innerText() === 'Pause' && await pb.getAttribute('aria-pressed') === 'false', `${t}: Pause label`);
      ok(await p.evaluate(() => { const b = document.querySelector('.ra-pause'); return !!b.closest('main .wrap') && b.compareDocumentPosition(document.querySelector('.ra-bar .ra-btn')) & Node.DOCUMENT_POSITION_PRECEDING; }), `${t}: Pause sits under the text being read (after the read bar)`);
      const playing = await p.evaluate(() => window.__playing && window.__playing.src), n0 = await p.evaluate(() => window.__played.length), z0 = await p.evaluate(() => window.__paused || 0);
      await pb.click(); await p.waitForTimeout(100);
      ok(await pb.innerText() === 'Resume' && await pb.getAttribute('aria-pressed') === 'true' && await pb.getAttribute('aria-label') === 'Resume reading', `${t}: toggles to Resume`);
      ok((await p.evaluate(() => window.__paused || 0)) > z0 && await btn.getAttribute('aria-pressed') === 'true', `${t}: paused, Stop still there`);
      await p.waitForTimeout(1700);
      ok((await p.evaluate(() => window.__played.length)) === n0, `${t}: nothing new plays while paused`);
      await pb.focus(); await p.keyboard.press('Enter'); await p.waitForTimeout(100);
      const pl = await p.evaluate(() => window.__played);
      ok(await pb.innerText() === 'Pause' && pl.length === n0 + 1 && pl[pl.length - 1] === playing, `${t}: Enter resumes the same clip (keeps the place)`);
      if (vp.width <= 375) ok(await p.evaluate(() => document.documentElement.scrollWidth <= window.innerWidth), `${t}: no horizontal scroll with Pause`); }
    // call link stays clickable while audio plays, and stops it
    await p.evaluate(() => { document.querySelectorAll('a[href^="tel:"]').forEach(a => a.addEventListener('click', e => e.preventDefault())); });
    const c0 = await p.evaluate(() => window.__paused || 0);
    await p.click('#now a[href="tel:000"]'); await p.waitForTimeout(200);
    ok(await btn.getAttribute('aria-pressed') === 'false' && (await p.evaluate(() => window.__paused || 0)) > c0, `${t}: tapping Call 000 stops reading`);
    ok(await p.locator('.ra-pause').isHidden(), `${t}: Pause hidden after a call link stops reading`);
    ok(p.offsite.length === 0, `${t}: no off-site requests ${p.offsite}`);
    ok(p.errs.length === 0, `${t}: no errors ${p.errs}`);
    if (vp.width !== 320) await p.screenshot({ path: `/workspace/shots/readaloud-help-${vp.width}.png` });
    await ctx.close();
  }
  // 2. Voice B choice: stored in localStorage only; next tap loads B only
  { const { ctx, p } = await open(b, 'help.html', 'network');
    ok(await p.locator('.ra-bar .ra-voices').isVisible(), 'voice picker visible when both voices exist');
    ok(await p.$eval('.ra-bar .ra-voices', e => e.getAttribute('aria-label')) === 'Read aloud voice' && await p.$eval('.ra-bar [data-ra-voice="B"]', e => e.getAttribute('aria-label')) === 'Use Voice B for read aloud', 'voice picker labelled');
    ok(JSON.stringify(await p.$$eval('.ra-bar [data-ra-voice]', x => x.map(e => e.textContent))) === '["Voice A","Voice B"]', 'labels Voice A / Voice B');
    await p.click('.ra-bar [data-ra-voice="B"]');
    ok(await p.evaluate(() => localStorage.getItem('hc.ra.voice.v1')) === 'B' && await p.$eval('.ra-bar [data-ra-voice="B"]', e => e.getAttribute('aria-pressed')) === 'true', 'Voice B stored in localStorage');
    ok(await p.evaluate(() => document.cookie === ''), 'no cookie');
    await p.click('.ra-bar [data-ra-sample="B"]'); await p.waitForTimeout(800);
    ok(p.audioReqs.length > 0 && p.audioReqs.every(f => fileVoice[f] === 'B'), 'sample B loads B clips only');
    await ctx.close(); }
  // 3. Missing clip in chosen voice -> other voice's clip (crisis), never silent
  { const emA = manifest.lines.find(l => l.id === 'kai.crisis.emergency').clips.A.file, emB = manifest.lines.find(l => l.id === 'kai.crisis.emergency').clips.B.file;
    const { ctx, p } = await open(b, 'index.html', 'none', null, { block: '**/' + emA });
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
    ok(played.length === 1 && played[0].startsWith('blob:') && (await p.evaluate(() => window.__primed)) >= 1, 'crisis reply plays a clip through the element primed in the tap (from Voice B, as A is missing) ' + played);
    ok(p.audioReqs.includes(emB), 'fell back to the other voice\'s crisis clip');
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
    await btn.click(); await p.waitForTimeout(300);
    const sp = await p.evaluate(() => window.__spoken);
    ok(sp.length >= 1 && sp.every(s => s.local === true && s.voice === 'Karen'), 'device fallback uses local en-AU voice only (Voice A style) ' + JSON.stringify(sp[0]));
    ok(p.audioReqs.length === 0, 'twelve steps loads no clips');
    await p.click('.ra-pause'); await p.waitForTimeout(50);
    ok((await p.evaluate(() => window.__ssPause)) === 1 && await p.locator('.ra-pause').innerText() === 'Resume', 'device voice: speechSynthesis.pause()');
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
    const lay = await p.evaluate(() => { const r = e => e && e.getBoundingClientRect(); const pb = r(document.querySelector('.ra-pause')); const hit = (a, b) => a && b && b.width && a.left < b.right && b.left < a.right && a.top < b.bottom && b.top < a.bottom;
      const others = [...document.querySelectorAll('#kai-start button, #kai-start a, #kai-crisis a, #kai-notsafe')].map(r);
      return { shown: !!pb && pb.width > 0, overlap: others.some(o => hit(pb, o)), h: pb && pb.height, sw: document.documentElement.scrollWidth <= window.innerWidth }; });
    ok(lay.shown && !lay.overlap && lay.h >= 44 && lay.sw, `Kai intro Pause @${vp.width}: no overlap with start buttons / 000 strip ${JSON.stringify(lay)}`);
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
  await b.close(); console.log(`readaloud browser: ${n - f}/${n} passed`); process.exit(f ? 1 : 0);
})();
