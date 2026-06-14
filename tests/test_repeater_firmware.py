from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
HEADER = ROOT / "firmware" / "ancs_feed.h"


def _header():
    return HEADER.read_text(encoding="utf-8")


def test_feed_header_exists():
    assert HEADER.is_file()


def test_feed_header_defines_builders():
    h = _header()
    for fn in ("feed_notif_json", "feed_removed_json", "feed_conn_json"):
        assert fn in h, f"missing builder: {fn}"


def test_feed_header_escapes_and_truncates():
    h = _header()
    # JSON-unsafe characters must be handled
    assert '\\\\"' in h or '\\"' in h, "no quote escaping"
    assert "utf8_truncate" in h, "no UTF-8-safe truncation helper"


YAML = ROOT / "firmware" / "ancservice.yaml"
UI = ROOT / "firmware" / "ui.yaml"


def _yaml():
    return YAML.read_text(encoding="utf-8")


def _ui():
    return UI.read_text(encoding="utf-8")


def test_ui_layer_includes_feed_header():
    assert "../ancs_feed.h" in _ui()


def test_ui_layer_defines_internal_feed_sensor():
    u = _ui()
    assert "id: notification_feed" in u
    assert "internal: true" in u


def test_ui_layer_web_server_includes_internal_and_assets():
    u = _ui()
    assert "include_internal: true" in u
    assert "css_include: ../assets/ancs-ui.css" in u
    assert "js_include: ../assets/ancs-ui.js" in u


def test_ui_layer_publishes_all_four_feed_events():
    u = _ui()
    assert "feed_notif_json" in u
    assert "feed_removed_json" in u
    assert u.count("feed_conn_json") >= 2  # connect (true) and disconnect (false)


def test_board_wrappers_include_ui_layer():
    for chip in ("esp32", "esp32-s3", "esp32-c3"):
        w = (ROOT / "firmware" / "boards" / f"{chip}.yaml").read_text(encoding="utf-8")
        assert "ui.yaml" in w, f"{chip} wrapper must include ui.yaml"


def test_ancservice_yaml_stays_adopt_clean():
    # the dashboard_import/adopt file must NOT carry local includes/asset refs/feed sensor
    y = _yaml()
    assert "includes:" not in y
    assert "css_include" not in y
    assert "js_include" not in y
    assert "notification_feed" not in y
