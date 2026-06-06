# ANCService

Pre-compiled, web-installable firmware that turns an ESP32 into an Apple
Notification Center Service (ANCS) bridge — built on
[esphome-ancs](https://github.com/wonderslug/esphome-ancs).

## Install (users)

Open the web installer and click **Install** with your board plugged in via USB:
**https://wonderslug.github.io/ANCService/**

Supported boards: ESP32, ESP32-S3, ESP32-C3. The installer also sets WiFi (Improv),
shows logs, and links you into Home Assistant. The device joins HA **keyless**; to
add per-device API encryption, use ESPHome's **adopt / Take Control** flow.

## Pair your iPhone

ANCS pairing requires nRF Connect — see the
[pairing guide](https://github.com/wonderslug/esphome-ancs/blob/master/docs/pairing.md).

## Local development

Build and browser-flash any component ref without publishing:

```bash
pip install -r requirements-dev.txt
make dev CHIP=esp32-s3 REF=feat/my-branch    # then open http://localhost:8000/
make test                                    # run the Python unit tests
```

`CHIP` ∈ {esp32, esp32-s3, esp32-c3}. `REF` is any esphome-ancs tag or branch.

Web Serial flashing needs a secure context. `http://localhost` already counts as
one, so `make dev` works — just be sure to open **localhost**, not a LAN IP or
`.local` hostname. To flash from another device on your network (or if localhost
is unavailable), serve over HTTPS instead:

```bash
brew install mkcert && mkcert -install        # one-time: trust a local CA
make https CHIP=esp32 REF=master              # then open https://localhost:8443/
```

`make https` auto-generates a trusted `localhost` cert into `.dev-certs/` (gitignored).

For local development it's usually simplest to skip the browser installer and flash
over USB directly — esp-web-tools' Web Serial reset can fail to enter the bootloader
on some macOS/USB-adapter combinations:

```bash
make flash CHIP=esp32 REF=master                       # build + esptool write-flash
make flash CHIP=esp32 SERIAL_PORT=/dev/cu.SLAB_USBtoUART  # if auto-detect picks the wrong port
make monitor SERIAL_PORT=/dev/cu.SLAB_USBtoUART        # view serial logs (115200)
```

## Releases & versioning

- Tag `vX.Y.Z` → CI compiles all three chips, attaches `.bin` assets to a GitHub
  Release, and deploys the installer to Pages.
- **Patch** bumps are automatic: a new `esphome-ancs` release fires a
  `repository_dispatch` that re-pins the component and re-tags.
- **Minor/major** bumps are manual and reserved for actual ANCService changes.

## One-time maintainer setup

1. ANCService repo → Settings → Pages → Source: **GitHub Actions**.
2. Allow the `github-pages` environment to deploy from **tags** — the release
   workflow runs on `v*` tags, but the auto-created environment defaults to the
   default branch only. Either clear its deployment-branch policy:
   ```bash
   echo '{"deployment_branch_policy":null}' | \
     gh api -X PUT repos/wonderslug/ANCService/environments/github-pages --input -
   ```
   or in Settings → Environments → `github-pages`, set "Deployment branches and
   tags" to allow `v*`. (Symptom if skipped: publish job fails with
   *"Tag … is not allowed to deploy to github-pages due to environment protection rules."*)
3. Create a fine-grained PAT with `contents: write` on `wonderslug/ANCService`.
4. Add it as secret `ANCSERVICE_DISPATCH_TOKEN` in the `esphome-ancs` repo.
