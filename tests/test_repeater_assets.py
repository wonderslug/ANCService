import gzip
from pathlib import Path

ASSETS = Path(__file__).resolve().parents[1] / "firmware" / "assets"
CSS = ASSETS / "ancs-ui.css"
JS = ASSETS / "ancs-ui.js"

# Generous budget for Stage A+B; tightened later. Gzipped bytes.
CSS_BUDGET = 8 * 1024
JS_BUDGET = 16 * 1024


def test_assets_exist():
    assert CSS.is_file()
    assert JS.is_file()


def test_assets_within_flash_budget_gzipped():
    assert len(gzip.compress(CSS.read_bytes())) <= CSS_BUDGET
    assert len(gzip.compress(JS.read_bytes())) <= JS_BUDGET


def test_js_is_node_requireable_shape():
    src = JS.read_text(encoding="utf-8")
    assert "module.exports" in src, "must export pure logic for Node tests"
    assert "typeof document" in src, "DOM bootstrap must be guarded"
