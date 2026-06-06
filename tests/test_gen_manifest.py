import json
import pytest
from scripts.gen_manifest import release_asset_url, build_manifest, main


def test_release_asset_url():
    url = release_asset_url("wonderslug/ANCService", "v1.0.1", "ancservice-esp32-v1.0.1.bin")
    assert url == (
        "https://github.com/wonderslug/ANCService/releases/download/"
        "v1.0.1/ancservice-esp32-v1.0.1.bin"
    )


def _builds():
    return [
        {"chipFamily": "ESP32", "path": "a-esp32.bin"},
        {"chipFamily": "ESP32-S3", "path": "a-esp32s3.bin"},
        {"chipFamily": "ESP32-C3", "path": "a-esp32c3.bin"},
    ]


def test_build_manifest_shape():
    m = build_manifest(name="ANCService", version="1.0.1 (ancs v1.4.0)", builds=_builds())
    assert m["name"] == "ANCService"
    assert m["version"] == "1.0.1 (ancs v1.4.0)"
    assert m["new_install_prompt_erase"] is True
    assert [b["chipFamily"] for b in m["builds"]] == ["ESP32", "ESP32-S3", "ESP32-C3"]


def test_build_manifest_parts_offset_zero():
    m = build_manifest(name="ANCService", version="x", builds=_builds())
    for b in m["builds"]:
        assert b["parts"] == [{"path": b["parts"][0]["path"], "offset": 0}]
    assert m["builds"][0]["parts"][0]["path"] == "a-esp32.bin"


def test_build_manifest_is_json_serializable():
    m = build_manifest(name="ANCService", version="x", builds=_builds())
    json.dumps(m)  # must not raise


def test_build_manifest_rejects_empty_builds():
    with pytest.raises(ValueError):
        build_manifest(name="ANCService", version="x", builds=[])


def test_build_manifest_includes_home_assistant_domain():
    # esp-web-tools only shows "Add to Home Assistant" when this field is present.
    m = build_manifest(name="ANCService", version="x", builds=_builds(),
                       home_assistant_domain="esphome")
    assert m["home_assistant_domain"] == "esphome"


def test_build_manifest_omits_home_assistant_domain_when_unset():
    m = build_manifest(name="ANCService", version="x", builds=_builds())
    assert "home_assistant_domain" not in m


def test_main_writes_home_assistant_domain(tmp_path):
    out = tmp_path / "manifest.json"
    main([
        "--version", "dev", "--ancs-ref", "master", "--mode", "local",
        "--build", "esp32=ancservice-esp32-dev.bin", "--out", str(out),
    ])
    m = json.loads(out.read_text())
    assert m["home_assistant_domain"] == "esphome"


def test_main_stable_mode_requires_tag(tmp_path):
    # stable mode without --tag must fail fast (argparse error -> SystemExit 2)
    with pytest.raises(SystemExit):
        main([
            "--version", "v1.0.0", "--ancs-ref", "v1.4.0", "--mode", "stable",
            "--build", "esp32=ancservice-esp32-v1.0.0.bin",
            "--out", str(tmp_path / "manifest.json"),
        ])
