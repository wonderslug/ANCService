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
