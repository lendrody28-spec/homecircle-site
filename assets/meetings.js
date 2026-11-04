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


  /* ---------- Add reminder: a calendar file with an alert 2 hours before ----------
     Made in this browser and downloaded straight to you. HomeCircle sends no notifications
     and keeps no copy. The alert is always 2 hours before the start, never at the start. */
  var VTZ = {
    east: ["+1000", "+1100"], adelaide: ["+0930", "+1030"],
    fixed: { "Australia/Brisbane": "+1000", "Australia/Lindeman": "+1000", "Australia/Darwin": "+0930", "Australia/Perth": "+0800" },
    zones: { "Australia/Sydney": "east", "Australia/Melbourne": "east", "Australia/Hobart": "east", "Australia/Canberra": "east",
      "Australia/ACT": "east", "Australia/NSW": "east", "Australia/Victoria": "east", "Australia/Tasmania": "east", "Australia/Currie": "east",
      "Australia/Adelaide": "adelaide", "Australia/Broken_Hill": "adelaide", "Australia/South": "adelaide" }
  };
  function vtimezone(tz) {
    var lines = ["BEGIN:VTIMEZONE", "TZID:" + tz];
    if (VTZ.fixed[tz]) {
      lines.push("BEGIN:STANDARD", "DTSTART:19700101T000000", "TZOFFSETFROM:" + VTZ.fixed[tz], "TZOFFSETTO:" + VTZ.fixed[tz], "END:STANDARD");
    } else {
      var o = VTZ[VTZ.zones[tz]];
      // Daylight saving in south-eastern Australia: starts 2am on the first Sunday in October, ends 3am on the first Sunday in April.
      lines.push("BEGIN:STANDARD", "DTSTART:19700405T030000", "RRULE:FREQ=YEARLY;BYMONTH=4;BYDAY=1SU", "TZOFFSETFROM:" + o[1], "TZOFFSETTO:" + o[0], "END:STANDARD",
        "BEGIN:DAYLIGHT", "DTSTART:19701004T020000", "RRULE:FREQ=YEARLY;BYMONTH=10;BYDAY=1SU", "TZOFFSETFROM:" + o[0], "TZOFFSETTO:" + o[1], "END:DAYLIGHT");
    }
    lines.push("END:VTIMEZONE");
    return lines;
  }
  function knownTZ(tz) { return !!(VTZ.fixed[tz] || VTZ.zones[tz]); }
  function pad(n) { return String(n).padStart(2, "0"); }
  function partsIn(tz, d) {
    var p = new Intl.DateTimeFormat("en-US", { timeZone: tz, year: "numeric", month: "2-digit", day: "2-digit", hour: "2-digit", minute: "2-digit", second: "2-digit", hourCycle: "h23", weekday: "short" }).formatToParts(d);
    var g = function (t) { return (p.filter(function (x) { return x.type === t; })[0] || {}).value; };
    return { y: +g("year"), m: +g("month"), d: +g("day"), h: +g("hour"), mi: +g("minute"), s: +g("second"), wd: ["Sun", "Mon", "Tue", "Wed", "Thu", "Fri", "Sat"].indexOf(g("weekday")) };
  }
  // The UTC instant of a wall-clock time in a time zone.
  function instant(tz, y, m, d, h, mi) {
    var guess = Date.UTC(y, m - 1, d, h, mi);
    for (var k = 0; k < 2; k++) {
      var p = partsIn(tz, new Date(guess));
      var shown = Date.UTC(p.y, p.m - 1, p.d, p.h, p.mi);
      guess += Date.UTC(y, m - 1, d, h, mi) - shown;
    }
    return new Date(guess);
  }
  function nextStart(m) {
    var s = m.schedule || {}, tz = s.timezone || "Australia/Sydney";
    var t = String(s.start || "").split(":"), h = parseInt(t[0], 10), mi = parseInt(t[1], 10);
    if (isNaN(h) || isNaN(mi)) return null;
    var now = new Date(), p = partsIn(tz, now);
    var ahead = (wd(m) - p.wd + 7) % 7;
    if (ahead === 0 && (p.h * 60 + p.mi) >= h * 60 + mi) ahead = 7;
    var day = new Date(Date.UTC(p.y, p.m - 1, p.d + ahead));
    var y = day.getUTCFullYear(), mo = day.getUTCMonth() + 1, d = day.getUTCDate();
    return { tz: tz, y: y, m: mo, d: d, h: h, mi: mi, at: instant(tz, y, mo, d, h, mi) };
  }
  function icsText(v) { return String(v || "").replace(/\\/g, "\\\\").replace(/;/g, "\\;").replace(/,/g, "\\,").replace(/\r?\n/g, "\\n"); }
  function fold(line) {
    var out = [], cur = "", len = 0;
    Array.from(line).forEach(function (ch) {
      var b = unescape(encodeURIComponent(ch)).length;
      if (len + b > 73) { out.push(cur); cur = " "; len = 1; }
      cur += ch; len += b;
    });
    out.push(cur);
    return out.join("\r\n");
  }
  function utcStamp(d) { return d.getUTCFullYear() + pad(d.getUTCMonth() + 1) + pad(d.getUTCDate()) + "T" + pad(d.getUTCHours()) + pad(d.getUTCMinutes()) + pad(d.getUTCSeconds()) + "Z"; }
  function buildICS(m, weekly) {
    var n = nextStart(m); if (!n) return null;
    var dur = Math.max(15, Math.min(360, parseInt((m.schedule || {}).duration_minutes, 10) || 60));
    var end = new Date(n.at.getTime() + dur * 60000);
    var l = m.location || {}, name = (m.fellowship ? m.fellowship + ": " : "") + (m.name || "Meeting");
    var where = m.format === "online" ? "Online" : [l.name, l.address, l.suburb, l.state, l.postal_code].filter(function (x) { return x && String(x).trim(); }).join(", ");
    var src = safeURL((m.source || {}).record_url), join = safeURL((m.online || {}).url);
    var desc = "Reminder added from homecircle.au. Times can change, so check the official listing." + (src ? "\nOfficial listing: " + src : "") + (join ? "\nJoin online: " + join : "") +
      "\nHomeCircle is support, not medical care. In an emergency call 000. Lifeline 13 11 14.";
    var lines = ["BEGIN:VCALENDAR", "VERSION:2.0", "PRODID:-//HomeCircle//Meeting reminder//EN", "CALSCALE:GREGORIAN", "METHOD:PUBLISH"];
    var start, finish;
    if (knownTZ(n.tz)) {
      lines = lines.concat(vtimezone(n.tz));
      var e = partsIn(n.tz, end);
      start = "DTSTART;TZID=" + n.tz + ":" + n.y + pad(n.m) + pad(n.d) + "T" + pad(n.h) + pad(n.mi) + "00";
      finish = "DTEND;TZID=" + n.tz + ":" + e.y + pad(e.m) + pad(e.d) + "T" + pad(e.h) + pad(e.mi) + "00";
    } else {
      start = "DTSTART:" + utcStamp(n.at); finish = "DTEND:" + utcStamp(end);
    }
    lines.push("BEGIN:VEVENT", "UID:" + (m.id || "meeting").toString().replace(/[^A-Za-z0-9._-]/g, "") + "-" + (weekly ? "weekly" : utcStamp(n.at)) + "@homecircle.au",
      "DTSTAMP:" + utcStamp(new Date()), start, finish);
    if (weekly) lines.push("RRULE:FREQ=WEEKLY");
    lines.push("SUMMARY:" + icsText(name));
    if (where) lines.push("LOCATION:" + icsText(where));
    if (src) lines.push("URL:" + src);
    lines.push("DESCRIPTION:" + icsText(desc),
      "BEGIN:VALARM", "ACTION:DISPLAY", "DESCRIPTION:" + icsText("Starts in 2 hours: " + name), "TRIGGER:-PT2H", "END:VALARM",
      "END:VEVENT", "END:VCALENDAR");
    return { text: lines.map(fold).join("\r\n") + "\r\n", next: n, soon: n.at.getTime() - Date.now() < 2 * 3600000 };
  }
  function download(name, text) {
    var blob = new Blob([text], { type: "text/calendar;charset=utf-8" });
    var url = URL.createObjectURL(blob), a = document.createElement("a");
    a.href = url; a.download = name; document.body.appendChild(a); a.click();
    setTimeout(function () { URL.revokeObjectURL(url); a.remove(); }, 1500);
  }
  function reminderBox(m, c) {
    var box = el("div", "remind"); box.hidden = true;
    box.id = "rem-" + Math.random().toString(36).slice(2, 9);
    box.appendChild(el("p", "remind-h", "Remind me 2 hours before"));
    var row = el("div", "btn-row");
    var once = el("button", "btn ghost", "Just this one"), weekly = el("button", "btn ghost", "Every week");
    once.type = weekly.type = "button";
    row.appendChild(once); row.appendChild(weekly); box.appendChild(row);
    var msg = el("p", "small"); msg.setAttribute("role", "status"); box.appendChild(msg);
    box.appendChild(el("p", "small", "This downloads a calendar file (.ics) for your calendar app. Its alert is set for 2 hours before the meeting starts. HomeCircle sends no notifications, and nothing is sent to us."));
    function go(isWeekly) {
      var r = buildICS(m, isWeekly);
      if (!r) { msg.textContent = "This meeting's time isn't clear in the list, so a reminder can't be made. Check the official listing."; return; }
      var slug = String(m.name || "meeting").toLowerCase().replace(/[^a-z0-9]+/g, "-").replace(/^-|-$/g, "").slice(0, 40) || "meeting";
      download("homecircle-" + slug + (isWeekly ? "-weekly" : "") + ".ics", r.text);
      var when = DAYS[wd(m)] + " " + clock((m.schedule || {}).start);
      msg.textContent = "Calendar file downloaded. Starts in 2 hours" + (isWeekly ? " · Every week" : "") + " · " + when + ". Open it to add it to your calendar." +
        (r.soon ? " This one starts in less than 2 hours, so your calendar may not alert you this time." : "");
    }
    once.addEventListener("click", function () { go(false); });
    weekly.addEventListener("click", function () { go(true); });
    return box;
  }

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
    var rb = el("button", "linkish", "Add reminder"); rb.type = "button"; rb.setAttribute("aria-expanded", "false");
    var box = reminderBox(m, c); rb.setAttribute("aria-controls", box.id);
    rb.addEventListener("click", function () { box.hidden = !box.hidden; rb.setAttribute("aria-expanded", box.hidden ? "false" : "true"); });
    acts.appendChild(rb);
    c.appendChild(acts);
    c.appendChild(box);
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
