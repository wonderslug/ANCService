from pathlib import Path

SITE = Path(__file__).resolve().parents[1] / "site"
WEBHOOKS_PAGE = SITE / "webhooks.html"
INDEX = SITE / "index.html"

PAYLOAD_FIELDS = {
    "Notification Webhook URL": [
        "uid", "category", "app_id", "title", "subtitle", "message",
        "date", "device_name", "iphone_name",
    ],
    "Incoming Call Webhook URL": [
        "uid", "caller", "app_id", "date", "device_name", "iphone_name",
    ],
    "Call Ended Webhook URL": [
        "uid", "device_name", "iphone_name",
    ],
}


def _webhooks_html():
    return WEBHOOKS_PAGE.read_text(encoding="utf-8")


def _index_html():
    return INDEX.read_text(encoding="utf-8")


def test_webhooks_page_exists():
    assert WEBHOOKS_PAGE.is_file()


def test_webhooks_page_documents_each_webhook_and_its_payload_fields():
    html = _webhooks_html()
    for label, fields in PAYLOAD_FIELDS.items():
        assert label in html, f"missing webhook: {label}"
        for field in fields:
            assert f"<code>{field}</code>" in html, f"missing payload field: {field}"


def test_webhooks_page_documents_master_switch_and_content_type():
    html = _webhooks_html()
    assert "Webhooks Enabled" in html
    assert "application/json" in html


def test_index_links_to_webhooks_page():
    assert 'href="webhooks.html"' in _index_html()
