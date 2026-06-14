from pathlib import Path

SITE = Path(__file__).resolve().parents[1] / "site"
PAGE = SITE / "repeater.html"
INDEX = SITE / "index.html"

URL_PARAMS = ["iphone", "theme", "accent", "css"]
TOKENS = ["--ancs-accent", "--ancs-bg", "--ancs-font"]


def _page():
    return PAGE.read_text(encoding="utf-8")


def test_repeater_page_exists():
    assert PAGE.is_file()


def test_repeater_page_documents_url_params():
    html = _page()
    for p in URL_PARAMS:
        assert f"<code>{p}</code>" in html, f"missing url param: {p}"


def test_repeater_page_documents_css_tokens():
    html = _page()
    for t in TOKENS:
        assert t in html, f"missing token: {t}"


def test_index_links_to_repeater_page():
    assert 'href="repeater.html"' in INDEX.read_text(encoding="utf-8")
