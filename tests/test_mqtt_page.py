from pathlib import Path

SITE = Path(__file__).resolve().parents[1] / "site"
MQTT_PAGE = SITE / "mqtt.html"
INDEX = SITE / "index.html"

PAYLOAD_FIELDS = {
    "ancservice/&lt;device&gt;/notification": [
        "uid", "category", "app_id", "title", "subtitle", "message",
        "date", "device_name", "iphone_name",
    ],
    "ancservice/&lt;device&gt;/incoming_call": [
        "uid", "caller", "app_id", "date", "device_name", "iphone_name",
    ],
    "ancservice/&lt;device&gt;/call_ended": [
        "uid", "device_name", "iphone_name",
    ],
}


def _mqtt_html():
    return MQTT_PAGE.read_text(encoding="utf-8")


def _index_html():
    return INDEX.read_text(encoding="utf-8")


def test_mqtt_page_exists():
    assert MQTT_PAGE.is_file()


def test_mqtt_page_documents_each_topic_and_its_payload_fields():
    html = _mqtt_html()
    for topic, fields in PAYLOAD_FIELDS.items():
        assert topic in html, f"missing topic: {topic}"
        for field in fields:
            assert f"<code>{field}</code>" in html, f"missing payload field: {field}"


def test_mqtt_page_documents_master_switch_and_build_your_own_requirement():
    html = _mqtt_html()
    assert "MQTT Enabled" in html
    assert "ancservice-mqtt.yaml" in html


def test_index_links_to_mqtt_page():
    assert 'href="mqtt.html"' in _index_html()
