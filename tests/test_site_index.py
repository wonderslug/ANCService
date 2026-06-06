from pathlib import Path

INDEX = Path(__file__).resolve().parents[1] / "site" / "index.html"


def _html():
    return INDEX.read_text(encoding="utf-8")


def test_install_button_present():
    html = _html()
    assert "esp-web-install-button" in html
    assert 'manifest="manifest.json"' in html


def test_all_five_steps_present():
    html = _html()
    for marker in [
        "Install the firmware",
        "Set WiFi",
        "Add to Home Assistant",
        "Pair your iPhone",
        "Use it in Home Assistant",
    ]:
        assert marker in html, f"missing step: {marker}"


def test_wifi_recovery_ap_named():
    assert "ANCService Setup" in _html()


def test_pairing_uses_nrf_connect_with_app_store_link():
    html = _html()
    assert "nRF Connect" in html
    assert "apps.apple.com" in html


def test_ha_events_documented():
    html = _html()
    for event in [
        "esphome.ancs_incoming_call",
        "esphome.ancs_notification",
        "esphome.ancs_call_ended",
    ]:
        assert event in html, f"missing event: {event}"


def test_optional_content_collapsed_in_details():
    # why-nRF-Connect, encryption/adopt note, extra automations, etc.
    assert _html().count("<details") >= 5
