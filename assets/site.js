/* HomeCircle website script. No tracking, no cookies, no storage, no third parties. */
(function () {
  "use strict";
  document.documentElement.classList.remove("no-js");

  /* Get help now: the link works without JavaScript (it goes to the Help page);
     with JavaScript it opens the panel instead. */
  var fab = document.getElementById("help-fab");
  var dlg = document.getElementById("help-dialog");
  if (fab && dlg && typeof dlg.showModal === "function") {
    fab.setAttribute("role", "button");
    fab.setAttribute("aria-haspopup", "dialog");
    fab.addEventListener("click", function (e) { e.preventDefault(); dlg.showModal(); var f = dlg.querySelector(".help-lines a"); if (f) f.focus(); });
    fab.addEventListener("keydown", function (e) { if (e.key === " ") { e.preventDefault(); fab.click(); } });
    dlg.addEventListener("click", function (e) { if (e.target === dlg) dlg.close(); });
    dlg.querySelectorAll("[data-close]").forEach(function (b) { b.addEventListener("click", function () { dlg.close(); }); });
    dlg.addEventListener("close", function () { fab.focus(); });
  }

  /* Small-screen menu */
  var mb = document.getElementById("menu-btn"), nav = document.getElementById("site-nav");
  if (mb && nav) {
    mb.hidden = false;
    mb.addEventListener("click", function () {
      var open = nav.classList.toggle("open");
      mb.setAttribute("aria-expanded", open ? "true" : "false");
    });
  }

  /* Library filter chips */
  var chips = document.querySelectorAll("[data-filter]");
  if (chips.length) {
    document.querySelector(".filters").hidden = false;
    chips.forEach(function (c) {
      c.addEventListener("click", function () {
        var f = c.getAttribute("data-filter");
        chips.forEach(function (o) { o.setAttribute("aria-pressed", o === c ? "true" : "false"); });
        document.querySelectorAll("[data-cat]").forEach(function (sec) {
          sec.hidden = !(f === "all" || sec.getAttribute("data-cat") === f);
        });
      });
    });
  }

  /* Upcoming events from events.json, soonest first, past hidden */
  var evList = document.getElementById("events-list");
  function todayISO() {
    var d = new Date();
    return d.getFullYear() + "-" + String(d.getMonth() + 1).padStart(2, "0") + "-" + String(d.getDate()).padStart(2, "0");
  }
  function hidePast(root) {
    var t = todayISO(), shown = 0;
    root.querySelectorAll("[data-end]").forEach(function (li) {
      var past = li.getAttribute("data-end") < t;
      li.hidden = past;
      if (!past) shown++;
    });
    var empty = document.getElementById("events-empty");
    if (empty) empty.hidden = shown > 0;
    return shown;
  }
  if (evList) {
    hidePast(evList);
    var limit = parseInt(evList.getAttribute("data-limit") || "0", 10);
    fetch(evList.getAttribute("data-src"), { cache: "no-cache" }).then(function (r) { return r.ok ? r.json() : null; }).then(function (data) {
      if (!data || !Array.isArray(data.events)) return;
      var months = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"];
      var evs = data.events.filter(function (e) { return e && e.title && e.start && /^https:\/\//.test(e.source || ""); })
        .sort(function (a, b) { return a.start < b.start ? -1 : a.start > b.start ? 1 : 0; });
      evList.textContent = "";
      evs.forEach(function (e) {
        var li = document.createElement("li");
        li.className = "event";
        li.setAttribute("data-end", e.end || e.start);
        var p = e.start.split("-"), q = (e.end || e.start).split("-");
        var date = document.createElement("div"); date.className = "date";
        var b = document.createElement("b"); b.textContent = String(parseInt(p[2], 10));
        date.appendChild(b);
        date.appendChild(document.createTextNode(months[parseInt(p[1], 10) - 1] + " " + p[0]));
        var body = document.createElement("div");
        var h = document.createElement("h3"); var a = document.createElement("a");
        a.href = e.source; a.textContent = e.title; a.rel = "noopener"; h.appendChild(a);
        var range = e.end && e.end !== e.start ? " to " + parseInt(q[2], 10) + " " + months[parseInt(q[1], 10) - 1] + " " + q[0] : "";
        var m1 = document.createElement("p");
        m1.textContent = parseInt(p[2], 10) + " " + months[parseInt(p[1], 10) - 1] + " " + p[0] + range + " · " + [e.place, e.state].filter(Boolean).join(", ") + " · " + (e.fellowship || "");
        var m2 = document.createElement("p");
        m2.textContent = "Listed by " + (e.organiser || "the organiser") + ". Check the official page for times and details.";
        body.appendChild(h); body.appendChild(m1); body.appendChild(m2);
        li.appendChild(date); li.appendChild(body);
        evList.appendChild(li);
      });
      var n = hidePast(evList);
      if (limit && n > limit) {
        var vis = Array.prototype.filter.call(evList.children, function (li) { return !li.hidden; });
        vis.slice(limit).forEach(function (li) { li.hidden = true; li.setAttribute("data-more", ""); });
        var more = document.getElementById("events-more");
        if (more) {
          more.hidden = false;
          more.textContent = "Show all " + n + " events";
          more.onclick = function () { evList.querySelectorAll("[data-more]").forEach(function (li) { li.hidden = false; }); more.hidden = true; };
        }
      }
    }).catch(function () { /* keep the built-in copy */ });
  }

  /* Breathing guide */
  var PATTERNS = {
    "breath-box": [["Breathe in", 4, 1], ["Hold", 4, 1], ["Breathe out", 4, 0], ["Hold empty", 4, 0]],
    "breath-478": [["Breathe in", 4, 1], ["Hold", 7, 1], ["Breathe out", 8, 0]],
    "breath-46": [["Breathe in", 4, 1], ["Breathe out", 6, 0]]
  };
  document.querySelectorAll("[data-breath]").forEach(function (root) {
    var ball = root.querySelector(".breath-ball"), label = root.querySelector(".breath-label"),
      phaseEl = root.querySelector("[data-phase]"), countEl = root.querySelector("[data-count]"),
      live = root.querySelector("[data-live]"), start = root.querySelector("[data-start]"),
      sel = root.querySelector("[data-pattern]"), mins = root.querySelector("[data-minutes]"),
      left = root.querySelector("[data-left]"), cues = root.querySelectorAll("[data-cue-for]");
    var timer = null, endAt = 0, running = false;
    function showCue(id) { cues.forEach(function (c) { c.hidden = c.getAttribute("data-cue-for") !== id; }); }
    function stop(msg) {
      running = false; clearTimeout(timer); clearInterval(root._tick);
      start.textContent = "Start"; start.setAttribute("aria-pressed", "false");
      ball.style.transitionDuration = "1.5s"; ball.style.transform = "scale(.35)";
      phaseEl.textContent = msg || "Ready"; countEl.textContent = ""; label.classList.add("dark");
      if (live) live.textContent = msg || "Stopped.";
      if (left) left.textContent = "";
      if (sel) sel.disabled = false; if (mins) mins.disabled = false;
    }
    function run(pattern, i) {
      if (!running) return;
      if (Date.now() >= endAt) { stop("Well done. Breathe normally."); return; }
      var ph = pattern[i % pattern.length], secs = ph[1];
      ball.style.transitionDuration = secs + "s";
      ball.style.transform = ph[2] ? "scale(1)" : "scale(.35)";
      label.classList.toggle("dark", !ph[2] && ph[0] !== "Hold");
      phaseEl.textContent = ph[0];
      if (live) live.textContent = ph[0] + " for " + secs;
      var n = secs; countEl.textContent = n;
      clearInterval(root._tick);
      root._tick = setInterval(function () {
        n--; if (n > 0) countEl.textContent = n;
        if (left) { var s = Math.max(0, Math.round((endAt - Date.now()) / 1000)); left.textContent = Math.floor(s / 60) + ":" + String(s % 60).padStart(2, "0") + " left"; }
      }, 1000);
      timer = setTimeout(function () { run(pattern, i + 1); }, secs * 1000);
    }
    if (sel) { sel.addEventListener("change", function () { showCue(sel.value); }); showCue(sel.value); }
    start.addEventListener("click", function () {
      if (running) { stop("Stopped. Breathe normally."); return; }
      var id = sel ? sel.value : root.getAttribute("data-breath");
      running = true; start.textContent = "Stop"; start.setAttribute("aria-pressed", "true");
      if (sel) sel.disabled = true; if (mins) mins.disabled = true;
      endAt = Date.now() + (mins ? parseInt(mins.value, 10) : 3) * 60000;
      run(PATTERNS[id] || PATTERNS["breath-46"], 0);
    });
    root.addEventListener("keydown", function (e) { if (e.key === "Escape" && running) stop("Stopped. Breathe normally."); });
    stop("Ready");
  });

  /* Step-by-step practice player */
  document.querySelectorAll("[data-player]").forEach(function (root) {
    var steps = root.querySelectorAll(".pstep"), i = 0, timer = null, paused = true;
    var prev = root.querySelector("[data-prev]"), next = root.querySelector("[data-next]"),
      play = root.querySelector("[data-play]"), count = root.querySelector("[data-pcount]"),
      bar = root.querySelector(".progress i"), pos = root.querySelector("[data-pos]");
    var timed = Array.prototype.some.call(steps, function (s) { return parseInt(s.getAttribute("data-seconds"), 10) > 0; });
    root.querySelectorAll(".pcontrols").forEach(function (c) { c.hidden = false; });
    root.querySelectorAll(".pstep").forEach(function (s) { s.hidden = true; });
    if (!timed && play) play.hidden = true;
    function show(n) {
      i = Math.max(0, Math.min(steps.length - 1, n));
      steps.forEach(function (s, k) { s.hidden = k !== i; });
      pos.textContent = "Step " + (i + 1) + " of " + steps.length;
      prev.disabled = i === 0; next.textContent = i === steps.length - 1 ? "Finish" : "Next";
      bar.style.width = ((i + 1) / steps.length * 100) + "%";
      var secs = parseInt(steps[i].getAttribute("data-seconds"), 10) || 0;
      count.textContent = secs ? secs + "s" : "";
      clearInterval(timer);
      if (!paused && secs) {
        var left = secs;
        timer = setInterval(function () {
          left--; count.textContent = left + "s";
          if (left <= 0) { clearInterval(timer); if (i < steps.length - 1) show(i + 1); else finish(); }
        }, 1000);
      }
    }
    function finish() { clearInterval(timer); paused = true; if (play) play.textContent = "Start again"; pos.textContent = "Finished. Take a moment before you get up."; count.textContent = ""; }
    prev.addEventListener("click", function () { show(i - 1); });
    next.addEventListener("click", function () { if (i === steps.length - 1) finish(); else show(i + 1); });
    if (play) play.addEventListener("click", function () {
      if (play.textContent === "Start again") { paused = false; play.textContent = "Pause"; show(0); return; }
      paused = !paused; play.textContent = paused ? "Resume" : "Pause"; show(i);
    });
    show(0);
  });

  /* Body scan opt-in (nothing is saved) */
  var optin = document.getElementById("bodyscan-optin");
  if (optin) {
    var target = document.getElementById("bodyscan-content");
    optin.hidden = false; target.hidden = true;
    optin.querySelector("button").addEventListener("click", function () { target.hidden = false; optin.hidden = true; target.querySelector("h2, h3").focus(); });
  }
})();
