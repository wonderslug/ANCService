/* ANCService custom web UI. Single file (web_server js_include is one file).
   Pure logic is exported for Node tests; DOM/SSE boot is guarded by `document`. */
(function (root) {
  "use strict";

  // ---- URL / mode detection (pure) -------------------------------------
  function parseMode(search, hash) {
    var params = new URLSearchParams(search || "");
    var iphone = params.get("iphone");
    var wantRepeater = (hash || "").indexOf("repeater") !== -1 || iphone !== null;
    return { repeater: wantRepeater, iphone: iphone };
  }

  // ---- Pure feed core --------------------------------------------------
  function parseFeedValue(str) {
    if (!str) return null;
    try {
      var v = JSON.parse(str);
      return v && typeof v === "object" && v.t ? v : null;
    } catch (e) {
      return null;
    }
  }

  // store: { phones: Map<phone, Map<uid, notif>>, connected: Set<phone> }
  function createFeedStore() {
    return { phones: new Map(), connected: new Set() };
  }

  function ensurePhone(store, ph) {
    if (!store.phones.has(ph)) store.phones.set(ph, new Map());
    return store.phones.get(ph);
  }

  function applyFeedEvent(store, evt) {
    if (!evt || !evt.t || evt.ph == null) return store;
    var ph = evt.ph;
    switch (evt.t) {
      case "conn":
        store.connected.add(ph);
        ensurePhone(store, ph);
        break;
      case "disconn":
        store.connected.delete(ph);
        store.phones.delete(ph);
        break;
      case "notif":
        store.connected.add(ph);
        ensurePhone(store, ph).set(evt.uid, {
          uid: evt.uid, app: evt.app || "", cat: evt.cat || "",
          title: evt.title || "", msg: evt.msg || "", ts: evt.ts || 0,
        });
        break;
      case "removed":
        if (store.phones.has(ph)) store.phones.get(ph).delete(evt.uid);
        break;
    }
    return store;
  }

  function selectActive(store, ph) {
    var m = store.phones.get(ph);
    if (!m) return [];
    return Array.from(m.values()).sort(function (a, b) { return b.ts - a.ts; });
  }

  function selectCall(store, ph) {
    var list = selectActive(store, ph);
    for (var i = 0; i < list.length; i++) {
      if (list[i].cat === "incoming_call") return list[i];
    }
    return null;
  }

  function isConnected(store, ph) { return store.connected.has(ph); }

  function knownPhones(store) {
    var set = new Set(store.connected);
    store.phones.forEach(function (_m, ph) { set.add(ph); });
    return Array.from(set);
  }

  // Whitelist of query params that map to CSS variables (prevents arbitrary
  // property injection). Values are CSS color/length strings.
  var THEME_VARS = {
    accent: "--ancs-accent",
    bg: "--ancs-bg",
    fg: "--ancs-fg",
    font: "--ancs-font",
    radius: "--ancs-radius",
  };

  function parseTheme(search) {
    var p = new URLSearchParams(search || "");
    var vars = {};
    Object.keys(THEME_VARS).forEach(function (k) {
      if (p.has(k)) vars[THEME_VARS[k]] = p.get(k);
    });
    return { preset: p.get("theme"), vars: vars, css: p.get("css") };
  }

  // ---- Repeater app (browser only) ------------------------------------
  var FEED_ID_MATCH = "notification_feed"; // web_server entity id is text_sensor-notification_feed
  var CYCLE_MS = 6000;

  function iconFor(cat) {
    switch (cat) {
      case "incoming_call": return "☎";   // ☎
      case "social": return "💬";      // 💬
      case "schedule": return "📅";    // 📅
      case "email": return "✉";             // ✉
      default: return "🔔";            // 🔔
    }
  }

  function relTime(ts) {
    if (!ts) return "";
    var d = Math.max(0, Math.floor(Date.now() / 1000) - ts);
    if (d < 60) return d + "s ago";
    if (d < 3600) return Math.floor(d / 60) + "m ago";
    return Math.floor(d / 3600) + "h ago";
  }

  function el(tag, cls, text) {
    var n = document.createElement(tag);
    if (cls) n.className = cls;
    if (text != null) n.textContent = text;
    return n;
  }

  function applyTheme(theme) {
    if (theme.preset) document.documentElement.setAttribute("data-ancs-theme", theme.preset);
    Object.keys(theme.vars).forEach(function (cssVar) {
      document.documentElement.style.setProperty(cssVar, theme.vars[cssVar]);
    });
    if (theme.css) {
      var link = document.createElement("link");
      link.rel = "stylesheet";
      link.href = theme.css; // loaded AFTER the base sheet so user rules win
      document.head.appendChild(link);
    }
  }

  function bootRepeater(mode) {
    var store = createFeedStore();
    var root = el("div");
    root.id = "ancs-repeater";
    document.body.appendChild(root);
    applyTheme(parseTheme(location.search));

    var cycleIndex = 0;
    var phone = mode.iphone;

    function render() {
      root.className = "";
      root.innerHTML = "";

      if (!phone) { renderPicker(root, store); return; }

      var connected = isConnected(store, phone);
      var call = selectCall(store, phone);
      var active = selectActive(store, phone);

      root.appendChild(topBar(phone, connected));

      if (!connected) {
        root.classList.add("ancs-disconnected");
        root.appendChild(centered("📵", "Waiting for " + phone + " to reconnect…"));
        return;
      }
      if (call) {
        root.classList.add("ancs-call");
        root.appendChild(callStage(call));
        return;
      }
      if (active.length === 0) {
        root.appendChild(centered("✓", "All caught up — no active notifications"));
        return;
      }
      if (cycleIndex >= active.length) cycleIndex = 0;
      root.appendChild(notifStage(active[cycleIndex]));
      root.appendChild(footer(cycleIndex, active.length));
    }

    function topBar(ph, connected) {
      var top = el("div", "ancs-top");
      var status = el("div", "ancs-status");
      status.appendChild(el("span", "ancs-dot"));
      status.appendChild(el("span", null, ph + (connected ? " · connected" : " · disconnected")));
      top.appendChild(status);
      top.appendChild(el("div", "ancs-brand", "ANCService"));
      return top;
    }

    function notifStage(n) {
      var stage = el("div", "ancs-stage");
      stage.appendChild(el("div", "ancs-app-icon", iconFor(n.cat)));
      stage.appendChild(el("div", "ancs-meta", (n.cat || "notification") + " · " + relTime(n.ts)));
      stage.appendChild(el("div", "ancs-title", n.title || ""));
      if (n.msg) stage.appendChild(el("div", "ancs-msg", n.msg));
      return stage;
    }

    function callStage(n) {
      var stage = el("div", "ancs-stage");
      stage.appendChild(el("div", "ancs-ring"));
      stage.appendChild(el("div", "ancs-meta", "Incoming call"));
      stage.appendChild(el("div", "ancs-title", n.title || "Unknown"));
      stage.appendChild(el("div", "ancs-msg", "calling…"));
      return stage;
    }

    function centered(glyph, text) {
      var stage = el("div", "ancs-stage");
      var g = el("div", "ancs-title", glyph);
      g.style.opacity = "0.6";
      stage.appendChild(g);
      stage.appendChild(el("div", "ancs-msg", text));
      return stage;
    }

    function footer(idx, total) {
      var foot = el("div", "ancs-foot");
      foot.appendChild(el("span", null, "showing " + (idx + 1) + " of " + total + " active"));
      var dots = el("div", "ancs-dots");
      for (var i = 0; i < total; i++) {
        var d = el("i", i === idx ? "on" : null);
        dots.appendChild(d);
      }
      foot.appendChild(dots);
      return foot;
    }

    // advance the carousel
    setInterval(function () {
      var active = phone ? selectActive(store, phone) : [];
      if (active.length > 1 && !selectCall(store, phone)) {
        cycleIndex = (cycleIndex + 1) % active.length;
        render();
      }
    }, CYCLE_MS);

    // periodic re-render so relative timestamps refresh
    setInterval(render, 30000);

    subscribeFeed(store, render);
    render();
  }

  function renderPicker(root, store) {
    var phones = knownPhones(store);
    root.appendChild((function () {
      var top = el("div", "ancs-top");
      top.appendChild(el("div", "ancs-status", "Select a phone"));
      top.appendChild(el("div", "ancs-brand", "ANCService"));
      return top;
    })());
    var picker = el("div", "ancs-picker");
    if (phones.length === 0) {
      picker.appendChild(el("div", "ancs-msg", "No phones connected yet…"));
    } else {
      phones.forEach(function (ph) {
        var a = el("a", null, ph);
        a.href = "?iphone=" + encodeURIComponent(ph);
        picker.appendChild(a);
      });
    }
    root.appendChild(picker);
  }

  function subscribeFeed(store, onChange) {
    if (typeof EventSource === "undefined") return;
    var es = new EventSource("/events");
    es.addEventListener("state", function (e) {
      var data;
      try { data = JSON.parse(e.data); } catch (err) { return; }
      if (!data || !data.id || data.id.indexOf(FEED_ID_MATCH) === -1) return;
      var evt = parseFeedValue(data.value);
      if (evt) { applyFeedEvent(store, evt); onChange(); }
    });
    // EventSource auto-reconnects on error; nothing else needed.
  }

  var api = {
    parseMode: parseMode,
    bootRepeater: bootRepeater,
    parseFeedValue: parseFeedValue,
    createFeedStore: createFeedStore,
    applyFeedEvent: applyFeedEvent,
    selectActive: selectActive,
    selectCall: selectCall,
    isConnected: isConnected,
    knownPhones: knownPhones,
    parseTheme: parseTheme,
  };

  if (typeof module !== "undefined" && module.exports) {
    module.exports = api;
  }

  if (typeof document !== "undefined") {
    document.addEventListener("DOMContentLoaded", function () {
      try {
        var mode = parseMode(location.search, location.hash);
        if (!mode.repeater) return; // leave the stock page untouched (graceful fallback)
        if (typeof api.bootRepeater === "function") api.bootRepeater(mode);
      } catch (e) {
        /* never break the page; stock UI remains */
        if (window.console) console.error("ancs-ui:", e);
      }
    });
  }

  if (typeof window !== "undefined") window.ANCSUI = api;
})(this);
