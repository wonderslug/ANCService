# ANCService Roadmap

The product vision and how it decomposes into independently shippable sub-projects.
Each sub-project gets its own spec → plan → build cycle. This file is the durable
index of that arc and where each piece stands.

## Vision

Productize the [`esphome-ancs`](https://github.com/wonderslug/esphome-ancs) component
into pre-compiled, web-installable firmware: turn a $5 ESP32 into an Apple Notification
Center Service bridge in ~5 minutes from a browser — no DIY YAML, no local toolchain.
Beyond a one-click install, the firmware should ship ready-to-go entities, set WiFi and
stream logs through the web installer, hand off cleanly into Home Assistant, and
eventually offer richer event delivery (MQTT/webhooks), on-device configuration, and
per-phone notification "repeater" display screens.

The DIY package path stays supported — `esphome-ancs` remains usable as an external
component for the quick-start crowd. ANCService is the batteries-included layer on top.

> Original brief: [`Claude.md`](./Claude.md).

## Sub-projects

| # | Sub-project | Status | Spec |
|---|---|---|---|
| 1 | **Distribution core** — reproducible firmware build, CI, tag-driven GitHub Release + Pages web installer, auto stable rebuilds on `esphome-ancs` release, local dev tooling | ✅ Shipped (`v0.1.0`) | `docs/superpowers/specs/2026-06-05-distribution-core-design.md` |
| 2 | **Onboarding & provisioning** — captive-portal WiFi fallback, baseline HA events, single-page guided quickstart (install → WiFi → Add to HA → pair → use) | 🛠️ Spec written | `docs/superpowers/specs/2026-06-05-onboarding-provisioning-design.md` |
| 3 | **Ready-to-go entities** — curated, pre-wired sensors and buttons for the ANCS services | ◻️ Planned | _tbd_ |
| 4 | **Event delivery** — MQTT topic publication and/or outbound webhooks beyond HA API events | ◻️ Planned | _tbd_ |
| 5 | **Configuration web interface** — on-device settings UI | ◻️ Planned | _tbd_ |
| 6 | **Notification display ("repeater") screens** — stylized per-phone notification/call display addressable by direct URL | ◻️ Future (architectural constraint to keep in mind now) | _tbd_ |

Legend: ✅ shipped · 🛠️ in progress · ⏭️ next · ◻️ planned

## #1 Distribution core — what shipped

The foundation everything else attaches to is live:

- **Canonical firmware** (`firmware/ancservice.yaml`) consuming `esphome-ancs` via a
  pinned ref, with keyless `api:` + `dashboard_import:` (adopt flow for per-device keys),
  `improv_serial:` WiFi provisioning, and `ota:`.
- **Build matrix**: ESP32 / ESP32-S3 / ESP32-C3 merged factory binaries.
- **Release pipeline** (`.github/workflows/release.yml`): a `v*` tag compiles all three
  chips, publishes a GitHub Release with `.bin` assets, and deploys the Pages installer.
  Binaries are also served same-origin from Pages so esp-web-tools can fetch them without
  GitHub's release-asset CORS getting in the way.
- **Auto stable rebuilds**: an `esphome-ancs` release fires a `repository_dispatch`
  (`component-release.yml`) that re-pins the component, patch-bumps the version, and
  re-tags — producing a new immutable ANCService release with no manual step.
- **Local dev tooling** (`Makefile` + `scripts/gen_manifest.py`): build/flash any
  component ref (tag or branch) without publishing.

Web installer: **https://wonderslug.github.io/ANCService/**

### Version policy (carried forward)

| Trigger | Bump | Who |
|---|---|---|
| New `esphome-ancs` release (only the pinned ref moves) | patch (`v1.0.0 → v1.0.1`) | automatic |
| Actual change to ANCService itself (firmware, site, pipeline, scripts) | minor / major | manual |

Each release records the exact `esphome-ancs` ref it was built against (e.g.
`ANCService v0.1.0 (ancs v1.1.1)`) so any installed firmware is traceable to source on
both repos.

## Notes for future sub-projects

- **#2 provisioning** replaces the minimal `wifi: ap: {}` with a real captive-portal
  fallback and an Add-to-HA landing experience. `dashboard_import:` already lays the
  groundwork for HA discovery + the adopt flow.
- **#6 repeater screens** are explicitly later, but the per-phone, URL-addressable display
  model is a constraint to keep in mind while designing #3–#5 so we don't paint into a
  corner.

---

Detailed specs and implementation plans live under `docs/superpowers/`. Note that
directory is currently gitignored (local-only); this roadmap is the tracked summary.
