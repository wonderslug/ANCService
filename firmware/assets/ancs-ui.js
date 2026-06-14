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

  var api = {
    parseMode: parseMode,
    // filled in by later tasks:
    parseFeedValue: null,
    createFeedStore: null,
    applyFeedEvent: null,
    selectActive: null,
    selectCall: null,
    parseTheme: null,
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
