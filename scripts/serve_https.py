"""Serve a directory over HTTPS for local esp-web-tools flashing.

Web Serial needs a secure context. `http://localhost` already qualifies, but
HTTPS is required to flash from another device on the LAN (or when localhost
is otherwise unavailable). Pair this with an mkcert-issued cert so the browser
trusts it without warnings.
"""
import argparse
import functools
import ssl
from http.server import HTTPServer, SimpleHTTPRequestHandler


def main(argv=None):
    p = argparse.ArgumentParser()
    p.add_argument("--dir", default="site")
    p.add_argument("--port", type=int, default=8443)
    p.add_argument("--host", default="127.0.0.1")
    p.add_argument("--cert", required=True)
    p.add_argument("--key", required=True)
    args = p.parse_args(argv)

    handler = functools.partial(SimpleHTTPRequestHandler, directory=args.dir)
    httpd = HTTPServer((args.host, args.port), handler)
    ctx = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
    ctx.load_cert_chain(certfile=args.cert, keyfile=args.key)
    httpd.socket = ctx.wrap_socket(httpd.socket, server_side=True)
    print(f"Serving {args.dir}/ at https://localhost:{args.port}/  (Ctrl-C to stop)")
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\nstopped")


if __name__ == "__main__":
    main()
