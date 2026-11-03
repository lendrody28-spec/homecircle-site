/* HomeCircle meeting finder. Reads the public meeting list that the app uses.
   Nothing is sent anywhere except the plain file requests to GitHub Pages.
   Location is only asked for when you press "Near me", and it never leaves this page. */
(function () {
  "use strict";
  var BASE = "https://lendrody28-spec.github.io/homecircle/feed/au/";
  var STATES = ["QLD", "NSW", "VIC", "WA", "SA", "TAS", "ACT", "NT"];
  var DAYS = ["Sunday", "Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"];
  var form = document.getElementById("finder");
  if (!form) return;
  var q = document.getElementById("f-q"), st = document.getElementById("f-state"), day = document.getElementById("f-day"),
    fel = document.getElementById("f-fellowship"), fmt = document.getElementById("f-format"),
    out = document.getElementById("results"), status = document.getElementById("f-status"),
    near = document.getElementById("f-near"), more = document.getElementById("f-more"), info = document.getElementById("feed-info");
  var cache = {}, index = null, origin = null, originLabel = "", shown = 0, list = [];
  form.hidden = false;
  document.getElementById("finder-nojs").hidden = true;

  function getJSON(url) { return fetch(url, { cache: "default" }).then(function (r) { if (!r.ok) throw new Error(r.status); return r.json(); }); }
  function loadIndex() {
    if (index) return Promise.resolve(index);
    return getJSON(BASE + "index.json").then(function (d) { index = d; return d; });
  }
  function loadState(code) {
    if (cache[code]) return Promise.resolve(cache[code]);
    return loadIndex().then(function (ix) {
      var row = (ix.states || []).filter(function (s) { return s.state === code; })[0];
      if (!row || !/^[A-Za-z0-9._-]+\.json$/.test(row.file)) return [];
      return getJSON(BASE + row.file).then(function (d) { cache[code] = Array.isArray(d.meetings) ? d.meetings : []; return cache[code]; });
    });
  }
  function stateForPostcode(pc) {
    var n = parseInt(pc, 10);
    if (pc.length !== 4 || isNaN(n)) return null;
    if (n >= 800 && n <= 899) return "NT";
    if ((n >= 200 && n <= 299) || (n >= 2600 && n <= 2618) || (n >= 2900 && n <= 2920)) return "ACT";
    if (n >= 1000 && n <= 2999) return "NSW";
    if ((n >= 3000 && n <= 3999) || (n >= 8000 && n <= 8999)) return "VIC";
    if ((n >= 4000 && n <= 4999) || (n >= 9000 && n <= 9999)) return "QLD";
    if (n >= 5000 && n <= 5999) return "SA";
    if (n >= 6000 && n <= 6999) return "WA";
    if (n >= 7000 && n <= 7999) return "TAS";
    return null;
  }
  function km(a, b, c, d) {
    var R = 6371, dLat = (c - a) * Math.PI / 180, dLon = (d - b) * Math.PI / 180;
    var x = Math.sin(dLat / 2) * Math.sin(dLat / 2) + Math.cos(a * Math.PI / 180) * Math.cos(c * Math.PI / 180) * Math.sin(dLon / 2) * Math.sin(dLon / 2);
    return R * 2 * Math.atan2(Math.sqrt(x), Math.sqrt(Math.max(0, 1 - x)));
  }
  function coord(m) {
    var l = m.location || {};
    if (typeof l.latitude !== "number" || typeof l.longitude !== "number") return null;
    if (Math.abs(l.latitude) > 90 || Math.abs(l.longitude) > 180) return null;
    return [l.latitude, l.longitude];
  }
  function wd(m) {
    var s = m.schedule || {};
    if (s.weekday >= 0 && s.weekday <= 6) return s.weekday;
    var i = DAYS.map(function (d) { return d.toLowerCase(); }).indexOf(String(s.day || "").toLowerCase());
    return i < 0 ? 0 : i;
  }
  function tzName(tz) {
    try { var p = new Intl.DateTimeFormat("en-AU", { timeZone: tz, timeZoneName: "short" }).formatToParts(new Date()); return (p.filter(function (x) { return x.type === "timeZoneName"; })[0] || {}).value || ""; } catch (e) { return ""; }
  }
  function clock(start) {
    var p = String(start || "").split(":"), h = parseInt(p[0], 10), mi = parseInt(p[1], 10);
    if (isNaN(h) || isNaN(mi)) return start || "";
    return ((h % 12) || 12) + ":" + String(mi).padStart(2, "0") + " " + (h < 12 ? "am" : "pm");
  }
  function isLive(m) {
    var s = m.schedule || {};
    try {
      var parts = new Intl.DateTimeFormat("en-US", { timeZone: s.timezone, weekday: "short", hour: "2-digit", minute: "2-digit", hourCycle: "h23" }).formatToParts(new Date());
      var g = function (t) { return (parts.filter(function (x) { return x.type === t; })[0] || {}).value; };
      var today = ["Sun", "Mon", "Tue", "Wed", "Thu", "Fri", "Sat"].indexOf(g("weekday"));
      if (today !== wd(m)) return false;
      var now = parseInt(g("hour"), 10) * 60 + parseInt(g("minute"), 10);
      var p = String(s.start).split(":"), st0 = parseInt(p[0], 10) * 60 + parseInt(p[1], 10);
      return now >= st0 && now < st0 + Math.max(1, s.duration_minutes || 60);
    } catch (e) { return false; }
  }
  function safeURL(u) { return typeof u === "string" && /^https?:\/\//i.test(u.trim()) ? u.trim() : null; }
  function el(tag, cls, text) { var e = document.createElement(tag); if (cls) e.className = cls; if (text != null) e.textContent = text; return e; }
  var FORMAT = { in_person: "In person", online: "Online", hybrid: "Hybrid" };

  function card(m) {
    var c = el("article", "meeting"), l = m.location || {}, s = m.schedule || {};
    var top = el("div");
    top.appendChild(el("span", "pill", m.fellowship || ""));
    top.appendChild(el("span", "pill", FORMAT[m.format] || "Other"));
    if (isLive(m)) top.appendChild(el("span", "pill live", "Live now"));
    (m.tags || []).slice(0, 4).forEach(function (t) { top.appendChild(el("span", "pill", String(t).replace(/_/g, " "))); });
    c.appendChild(top);
    c.appendChild(el("h3", null, m.name || "Meeting"));
    var when = DAYS[wd(m)] + " · " + clock(s.start) + (tzName(s.timezone) ? " " + tzName(s.timezone) : "");
    if (s.duration_minutes) when += " · " + s.duration_minutes + " min";
    c.appendChild(el("div", "when", when));
    var addr = [l.name, l.address, l.suburb, l.state, l.postal_code].filter(function (x) { return x && String(x).trim(); }).join(", ");
    var meta = el("div", "meta", addr + (l.approximate ? " (approximate location)" : ""));
    if (m._km != null) meta.textContent += " · " + (m._km < 10 ? m._km.toFixed(1) : Math.round(m._km)) + " km away";
    c.appendChild(meta);
    var acts = el("div", "acts");
    var join = (m.format === "online" || m.format === "hybrid") ? safeURL((m.online || {}).url) : null;
    if (join) { var a = el("a", null, "Join online"); a.href = join; a.rel = "noopener nofollow"; acts.appendChild(a); }
    if (m.format !== "online" && (addr || coord(m))) {
      var pt = coord(m), d = el("a", null, "Directions");
      d.href = "https://www.google.com/maps/search/?api=1&query=" + encodeURIComponent(pt && !l.approximate ? pt[0] + "," + pt[1] : addr);
      d.rel = "noopener nofollow"; acts.appendChild(d);
    }
    var src = safeURL((m.source || {}).record_url);
    if (src) { var o = el("a", null, "Official listing"); o.href = src; o.rel = "noopener nofollow"; acts.appendChild(o); }
    c.appendChild(acts);
    if (m.notes) { var det = el("details"); det.appendChild(el("summary", null, "Notes from the listing")); det.appendChild(el("pre", null, String(m.notes))); c.appendChild(det); }
    return c;
  }

  function render(reset) {
    if (reset) { out.textContent = ""; shown = 0; }
    var next = list.slice(shown, shown + 50);
    next.forEach(function (m) { out.appendChild(card(m)); });
    shown += next.length;
    more.hidden = shown >= list.length;
  }

  function filterAndSort(all, text) {
    var dayV = day.value, felV = fel.value, fmtV = fmt.value;
    var todayIdx = new Date().getDay();
    var needle = text.trim().toLowerCase(), isPC = /^\d{4}$/.test(needle);
    var base = all.filter(function (m) {
      if (felV && String(m.fellowship).toUpperCase() !== felV) return false;
      if (fmtV && m.format !== fmtV) return false;
      if (dayV !== "" && wd(m) !== (dayV === "today" ? todayIdx : parseInt(dayV, 10))) return false;
      return true;
    });
    var center = origin;
    originLabel = origin ? "you" : "";
    if (!center && needle) {
      var hits = all.filter(function (m) { var l = m.location || {}; return isPC ? l.postal_code === needle : String(l.suburb || "").toLowerCase() === needle; });
      var pts = hits.map(coord).filter(Boolean);
      if (pts.length) {
        center = [pts.reduce(function (s, p) { return s + p[0]; }, 0) / pts.length, pts.reduce(function (s, p) { return s + p[1]; }, 0) / pts.length];
        originLabel = needle.toUpperCase() === needle ? needle : (hits[0].location.suburb || needle);
      }
    }
    var res;
    if (center) {
      var radius = origin ? 25 : 15;
      res = base.filter(function (m) {
        if (m.format === "online") return false;
        var p = coord(m); if (!p) return false;
        m._km = km(center[0], center[1], p[0], p[1]);
        return m._km <= radius;
      });
      if (needle && !origin) {
        base.forEach(function (m) {
          var l = m.location || {};
          if (res.indexOf(m) < 0 && m.format !== "online" && (isPC ? l.postal_code === needle : String(l.suburb || "").toLowerCase() === needle)) { m._km = null; res.push(m); }
        });
      }
      res.sort(function (a, b) { return (a._km == null ? 1e9 : a._km) - (b._km == null ? 1e9 : b._km) || wd(a) - wd(b); });
    } else {
      res = base.filter(function (m) {
        m._km = null;
        if (!needle) return true;
        var l = m.location || {};
        return [m.name, l.name, l.address, l.suburb, l.state, l.postal_code].join(" ").toLowerCase().indexOf(needle) >= 0;
      });
      res.sort(function (a, b) { return wd(a) - wd(b) || String(a.schedule.start).localeCompare(String(b.schedule.start)); });
    }
    return { res: res, radius: center ? (origin ? 25 : 15) : 0 };
  }

  function search(ev) {
    if (ev) ev.preventDefault();
    var text = q.value || "";
    var code = st.value;
    var pcState = origin ? null : stateForPostcode(text.trim());
    if (!origin && !text.trim() && !code) { status.textContent = "Type a suburb or postcode, or choose a state."; return; }
    var codes = origin ? STATES : pcState ? [pcState] : code === "online" ? ["online"] : (code && code !== "ALL") ? [code] : STATES;
    status.textContent = "Loading meetings…";
    out.setAttribute("aria-busy", "true");
    Promise.all(codes.map(loadState)).then(function (arrs) {
      var all = [].concat.apply([], arrs);
      var r = filterAndSort(all, origin ? "" : text);
      list = r.res;
      var where = origin ? "within " + r.radius + " km of you" : r.radius ? "in or near " + originLabel + " (within " + r.radius + " km)" : (text.trim() ? "matching \u201C" + text.trim() + "\u201D" : "");
      status.textContent = list.length ? list.length + " meeting" + (list.length === 1 ? "" : "s") + " found " + where + "." : "No meetings found " + where + ". Try another day, a nearby suburb, or another state.";
      render(true);
      out.removeAttribute("aria-busy");
    }).catch(function () {
      out.removeAttribute("aria-busy");
      status.textContent = "The meeting list didn't load. Check your connection, or use the official AA and NA meeting lists below.";
    });
  }
  form.addEventListener("submit", function (e) { origin = null; search(e); });
  more.addEventListener("click", function () { render(false); });
  [st, day, fel, fmt].forEach(function (s) { s.addEventListener("change", function () { if (out.children.length || origin) search(); }); });

  if (near) {
    if (!("geolocation" in navigator)) near.hidden = true;
    near.addEventListener("click", function () {
      status.textContent = "Asking your browser for your location…";
      navigator.geolocation.getCurrentPosition(function (pos) {
        origin = [pos.coords.latitude, pos.coords.longitude];
        q.value = ""; search();
      }, function () {
        status.textContent = "Location wasn't shared. You can still search by suburb or postcode.";
      }, { enableHighAccuracy: false, timeout: 15000, maximumAge: 600000 });
    });
  }

  loadIndex().then(function (ix) {
    if (!info) return;
    var d = new Date(ix.generated_at);
    info.textContent = (ix.meeting_count || "") + " AA and NA meetings in the list, last updated " +
      d.toLocaleDateString("en-AU", { day: "numeric", month: "long", year: "numeric" }) + ".";
  }).catch(function () {});
})();
