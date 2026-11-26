/* HomeCircle events list: hide finished events in the event's own state time zone.
   No tracking, no cookies, no localStorage, no network. */
(function (global) {
  "use strict";

  var ZONES = {
    QLD: "Australia/Brisbane",
    NSW: "Australia/Sydney",
    ACT: "Australia/Sydney",
    VIC: "Australia/Melbourne",
    SA: "Australia/Adelaide",
    WA: "Australia/Perth",
    TAS: "Australia/Hobart",
    NT: "Australia/Darwin"
  };
  var DEFAULT_ZONE = "Australia/Brisbane";

  function zoneFor(state) {
    var key = (state || "").toString().trim().toUpperCase();
    return ZONES[key] || DEFAULT_ZONE;
  }

  function dateInZone(now, timeZone) {
    var parts = new Intl.DateTimeFormat("en-CA", {
      timeZone: timeZone,
      year: "numeric",
      month: "2-digit",
      day: "2-digit"
    }).formatToParts(now);
    var y = "", m = "", d = "";
    parts.forEach(function (p) {
      if (p.type === "year") y = p.value;
      if (p.type === "month") m = p.value;
      if (p.type === "day") d = p.value;
    });
    return y + "-" + m + "-" + d;
  }

  function isFinished(endDate, state, now) {
    if (!endDate) return false;
    now = now || new Date();
    return dateInZone(now, zoneFor(state)) > endDate;
  }

  function hideFinished(root, now) {
    if (!root) return 0;
    var shown = 0;
    var cards = root.querySelectorAll(".ev-card");
    for (var i = 0; i < cards.length; i++) {
      var li = cards[i];
      var end = li.getAttribute("data-end") || li.getAttribute("data-start") || "";
      var state = li.getAttribute("data-state") || "";
      var past = isFinished(end, state, now);
      li.hidden = past;
      if (!past) shown++;
    }
    var limit = parseInt(root.getAttribute("data-limit") || "0", 10);
    if (limit) {
      var visible = [];
      for (var j = 0; j < root.children.length; j++) {
        if (!root.children[j].hidden) visible.push(root.children[j]);
      }
      visible.slice(limit).forEach(function (li) { li.hidden = true; });
      shown = Math.min(shown, limit);
    }
    var empty = typeof document !== "undefined" ? document.getElementById("events-empty") : null;
    if (empty) empty.hidden = shown > 0;
    return shown;
  }

  function init(now) {
    var root = typeof document === "undefined" ? null : document.getElementById("events-list");
    if (!root) return 0;
    return hideFinished(root, now);
  }

  var api = {
    ZONES: ZONES,
    DEFAULT_ZONE: DEFAULT_ZONE,
    zoneFor: zoneFor,
    dateInZone: dateInZone,
    isFinished: isFinished,
    hideFinished: hideFinished,
    init: init
  };

  if (typeof module === "object" && module.exports) {
    module.exports = api;
  } else {
    global.hcEvents = api;
    init();
  }
})(typeof window !== "undefined" ? window : typeof globalThis !== "undefined" ? globalThis : this);
