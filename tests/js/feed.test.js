const test = require("node:test");
const assert = require("node:assert/strict");
const ui = require("../../firmware/assets/ancs-ui.js");

test("parseFeedValue parses valid JSON and rejects junk", () => {
  assert.deepEqual(ui.parseFeedValue('{"t":"conn","ph":"A"}'), { t: "conn", ph: "A" });
  assert.equal(ui.parseFeedValue("not json"), null);
  assert.equal(ui.parseFeedValue(""), null);
});

test("notif adds to a phone's active set; removed deletes it", () => {
  const s = ui.createFeedStore();
  ui.applyFeedEvent(s, { t: "notif", ph: "A", uid: 1, title: "Mom", msg: "hi", cat: "social", ts: 10 });
  ui.applyFeedEvent(s, { t: "notif", ph: "A", uid: 2, title: "Cal", msg: "x", cat: "schedule", ts: 11 });
  assert.equal(ui.selectActive(s, "A").length, 2);
  ui.applyFeedEvent(s, { t: "removed", ph: "A", uid: 1 });
  const active = ui.selectActive(s, "A");
  assert.equal(active.length, 1);
  assert.equal(active[0].uid, 2);
});

test("disconnect clears the phone; connect makes it known but empty", () => {
  const s = ui.createFeedStore();
  ui.applyFeedEvent(s, { t: "notif", ph: "A", uid: 1, title: "x", msg: "", cat: "social", ts: 10 });
  ui.applyFeedEvent(s, { t: "disconn", ph: "A" });
  assert.equal(ui.selectActive(s, "A").length, 0);
  assert.equal(ui.isConnected(s, "A"), false);
  ui.applyFeedEvent(s, { t: "conn", ph: "A" });
  assert.equal(ui.isConnected(s, "A"), true);
  assert.equal(ui.selectActive(s, "A").length, 0);
});

test("applying the same notif twice is idempotent (dedupe by uid)", () => {
  const s = ui.createFeedStore();
  const evt = { t: "notif", ph: "A", uid: 7, title: "x", msg: "", cat: "social", ts: 10 };
  ui.applyFeedEvent(s, evt);
  ui.applyFeedEvent(s, evt);
  assert.equal(ui.selectActive(s, "A").length, 1);
});

test("selectActive sorts newest-first by ts", () => {
  const s = ui.createFeedStore();
  ui.applyFeedEvent(s, { t: "notif", ph: "A", uid: 1, ts: 10, title: "old", msg: "", cat: "social" });
  ui.applyFeedEvent(s, { t: "notif", ph: "A", uid: 2, ts: 20, title: "new", msg: "", cat: "social" });
  assert.equal(ui.selectActive(s, "A")[0].title, "new");
});

test("selectCall returns an incoming_call notif or null", () => {
  const s = ui.createFeedStore();
  ui.applyFeedEvent(s, { t: "notif", ph: "A", uid: 1, ts: 10, title: "Mom", msg: "", cat: "social" });
  assert.equal(ui.selectCall(s, "A"), null);
  ui.applyFeedEvent(s, { t: "notif", ph: "A", uid: 2, ts: 11, title: "Dad", msg: "", cat: "incoming_call" });
  assert.equal(ui.selectCall(s, "A").uid, 2);
});

test("knownPhones lists phones that are connected or have notifications", () => {
  const s = ui.createFeedStore();
  ui.applyFeedEvent(s, { t: "conn", ph: "A" });
  ui.applyFeedEvent(s, { t: "notif", ph: "B", uid: 1, ts: 1, title: "x", msg: "", cat: "social" });
  assert.deepEqual(ui.knownPhones(s).sort(), ["A", "B"]);
});

test("parseTheme reads preset, accent, and css url", () => {
  const t = ui.parseTheme("?iphone=A&theme=midnight&accent=%23ff3b30&css=https://x/y.css");
  assert.equal(t.preset, "midnight");
  assert.deepEqual(t.vars, { "--ancs-accent": "#ff3b30" });
  assert.equal(t.css, "https://x/y.css");
});

test("parseTheme returns empty pieces when absent", () => {
  const t = ui.parseTheme("?iphone=A");
  assert.equal(t.preset, null);
  assert.deepEqual(t.vars, {});
  assert.equal(t.css, null);
});

test("parseTheme only accepts known var params (no arbitrary injection)", () => {
  const t = ui.parseTheme("?bg=%23000000&evil=boom");
  assert.deepEqual(t.vars, { "--ancs-bg": "#000000" });
});
