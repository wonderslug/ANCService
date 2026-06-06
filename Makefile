# ANCService developer Makefile
PYTHON     ?= python3
CHIP       ?= esp32
REF        ?= master
PORT       ?= 8000
HTTPS_PORT ?= 8443
VERSION    ?= dev

# ESPHome writes .esphome/ next to the compiled config (firmware/boards/), not at repo root.
BUILD_BIN = firmware/boards/.esphome/build/ancservice/.pioenvs/ancservice/firmware.factory.bin

CERT_DIR = .dev-certs
CERT     = $(CERT_DIR)/localhost.pem
KEY      = $(CERT_DIR)/localhost-key.pem

# Optional explicit serial port (e.g. SERIAL_PORT=/dev/cu.SLAB_USBtoUART). Empty = esptool auto-detect.
SERIAL_PORT ?=
PORT_ARG     = $(if $(SERIAL_PORT),--port $(SERIAL_PORT),)

.PHONY: test compile stage dev https certs flash monitor clean

test:
	$(PYTHON) -m pytest tests/ -v

# Compile one chip against REF. Produces the merged factory bin.
compile:
	esphome -s ancs_ref $(REF) compile firmware/boards/$(CHIP).yaml

# Assemble the local dev installer (site/dev/) from a freshly compiled binary.
stage: compile
	mkdir -p site/dev
	cp "$(BUILD_BIN)" site/dev/ancservice-$(CHIP)-$(VERSION).bin
	$(PYTHON) scripts/gen_manifest.py \
	  --version $(VERSION) --ancs-ref $(REF) --mode local \
	  --build $(CHIP)=ancservice-$(CHIP)-$(VERSION).bin \
	  --out site/dev/manifest.json
	cp site/index.html site/dev/index.html
	cp -r site/assets site/dev/assets

# Build + serve over http://localhost (a secure context for Web Serial — flashing works).
# Serves site/dev as the web root so the local installer + local manifest are at /.
dev: stage
	@echo "Open http://localhost:$(PORT)/  (chip=$(CHIP) ref=$(REF))"
	$(PYTHON) -m http.server $(PORT) -d site/dev

# Generate an mkcert-trusted localhost cert if missing. Requires: brew install mkcert && mkcert -install
certs: $(CERT)
$(CERT):
	@command -v mkcert >/dev/null || { echo "mkcert not found. Run: brew install mkcert && mkcert -install"; exit 1; }
	mkdir -p $(CERT_DIR)
	mkcert -cert-file $(CERT) -key-file $(KEY) localhost 127.0.0.1 ::1

# Build + serve over https://localhost (needed to flash from another LAN device, or when
# localhost is unavailable). Requires the mkcert local CA installed (mkcert -install).
https: stage certs
	@echo "Open https://localhost:$(HTTPS_PORT)/  (chip=$(CHIP) ref=$(REF))"
	$(PYTHON) scripts/serve_https.py --dir site/dev --port $(HTTPS_PORT) --cert $(CERT) --key $(KEY)

# USB-flash the freshly built factory image with esptool — the reliable local-dev path
# (esp-web-tools' browser reset can fail to enter the bootloader on some macOS/adapter combos).
# Pass SERIAL_PORT=/dev/cu.xxx if auto-detect picks the wrong adapter.
flash: compile
	esptool $(PORT_ARG) --baud 460800 write-flash 0x0 "$(BUILD_BIN)"

# Serial monitor at the logger baud. Requires SERIAL_PORT=/dev/cu.xxx.
monitor:
	@test -n "$(SERIAL_PORT)" || { echo "set SERIAL_PORT=/dev/cu.xxx"; exit 1; }
	$(PYTHON) -m serial.tools.miniterm $(SERIAL_PORT) 115200

clean:
	rm -rf site/dev firmware/.esphome firmware/boards/.esphome
