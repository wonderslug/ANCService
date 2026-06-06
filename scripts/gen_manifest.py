"""Generate an esp-web-tools manifest.json for ANCService.

stable mode -> parts point at GitHub Release asset URLs.
local mode  -> parts are filenames sitting beside the dev manifest.
"""
import argparse
import json


def release_asset_url(repo, tag, filename):
    """GitHub Release asset download URL."""
    return f"https://github.com/{repo}/releases/download/{tag}/{filename}"


def build_manifest(name, version, builds, erase=True, home_assistant_domain=None):
    """Build the manifest dict.

    builds: list of {"chipFamily": str, "path": str}. Each becomes a single
    factory part flashed at offset 0.

    home_assistant_domain: when set, esp-web-tools shows an "Add to Home
    Assistant" button after install (ESPHome devices use "esphome").
    """
    if not builds:
        raise ValueError("builds must not be empty")
    manifest = {
        "name": name,
        "version": version,
        "new_install_prompt_erase": erase,
        "builds": [
            {
                "chipFamily": b["chipFamily"],
                "parts": [{"path": b["path"], "offset": 0}],
            }
            for b in builds
        ],
    }
    if home_assistant_domain:
        manifest["home_assistant_domain"] = home_assistant_domain
    return manifest


# chip -> esp-web-tools chipFamily
CHIP_FAMILY = {
    "esp32": "ESP32",
    "esp32-s3": "ESP32-S3",
    "esp32-c3": "ESP32-C3",
}


def _parse_build_arg(value):
    """Parse 'chip=filename' into a dict, resolving chipFamily."""
    chip, _, filename = value.partition("=")
    if chip not in CHIP_FAMILY:
        raise argparse.ArgumentTypeError(f"unknown chip: {chip}")
    return {"chip": chip, "chipFamily": CHIP_FAMILY[chip], "filename": filename}


def main(argv=None):
    p = argparse.ArgumentParser()
    p.add_argument("--name", default="ANCService")
    p.add_argument("--version", required=True)
    p.add_argument("--ancs-ref", required=True)
    p.add_argument("--mode", choices=["stable", "local"], required=True)
    p.add_argument("--repo", default="wonderslug/ANCService")
    p.add_argument("--tag", help="release tag (stable mode)")
    p.add_argument("--build", action="append", type=_parse_build_arg, required=True,
                   help="chip=filename, repeatable")
    p.add_argument("--home-assistant-domain", default="esphome",
                   help="enables esp-web-tools 'Add to Home Assistant' (default: esphome)")
    p.add_argument("--out", required=True)
    args = p.parse_args(argv)
    if args.mode == "stable" and not args.tag:
        p.error("--tag is required when --mode=stable")

    version = f"{args.version} (ancs {args.ancs_ref})"
    builds = []
    for b in args.build:
        if args.mode == "stable":
            path = release_asset_url(args.repo, args.tag, b["filename"])
        else:
            path = b["filename"]
        builds.append({"chipFamily": b["chipFamily"], "path": path})

    manifest = build_manifest(name=args.name, version=version, builds=builds,
                              home_assistant_domain=args.home_assistant_domain)
    with open(args.out, "w") as f:
        json.dump(manifest, f, indent=2)
    print(f"wrote {args.out} ({len(builds)} builds, mode={args.mode})")


if __name__ == "__main__":
    main()
