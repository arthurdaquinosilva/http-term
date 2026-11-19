"""Record :http for the README: the start screen and a real request, saved as an SVG.

    python scripts/screenshot.py   # writes docs/assets/cover.svg

A tiny JSON API runs on localhost for the request, so the image shows a real response without
touching the network. Needs the dev extras (pexpect, pyte).
"""

from __future__ import annotations

import json
import sys
import threading
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

from _termshot import ROOT, capture, save_svg, to_text

COLS, ROWS = 110, 40
PORT = 8765
USERS = [
    {"id": 1, "name": "Ada Lovelace", "email": "ada@example.com", "admin": True},
    {"id": 2, "name": "Alan Turing", "email": "alan@example.com", "admin": False},
]


class API(BaseHTTPRequestHandler):
    def do_GET(self) -> None:  # noqa: N802 (the http.server API)
        body = json.dumps(USERS if self.path.startswith("/users") else {"error": "not found"}).encode()
        self.send_response(200 if self.path.startswith("/users") else 404)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, *args) -> None:
        pass


def main() -> None:
    server = ThreadingHTTPServer(("127.0.0.1", PORT), API)
    threading.Thread(target=server.serve_forever, daemon=True).start()
    try:
        steps = [(f"GET localhost:{PORT}/users\r", 2.5)]
        screen = capture(steps, COLS, ROWS, cwd=ROOT)
        save_svg(to_text(screen), ROOT / "docs" / "assets" / "cover.svg", COLS, title=":http")
    finally:
        server.shutdown()


if __name__ == "__main__":
    sys.exit(main())
