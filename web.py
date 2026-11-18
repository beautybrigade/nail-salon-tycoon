"""Browser front end for Nail Salon Tycoon (R7).

Run with:  python3 web.py   (optionally --seed N, --port N, --no-browser)

This starts a small web server on this computer only (127.0.0.1) and opens the
game in the default browser. The page in static/ draws and animates the salon;
every game rule stays in salon.py. The page and this server talk in JSON:

    POST /api/new-game  {}                        -> first client, step menu
    POST /api/step      {"game_id", "step"}       -> animation, nail looks
    POST /api/finish    {"game_id"}               -> star, next client or day
"""

from __future__ import annotations

import argparse
import itertools
import json
import random
import webbrowser
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlsplit

import salon

HOST = "127.0.0.1"  # only this computer can reach the game
DEFAULT_PORT = 8000
STATIC_DIR = Path(__file__).resolve().parent / "static"
STATIC_FILES = {  # the only files the server hands out
    "index.html": "text/html; charset=utf-8",
    "style.css": "text/css; charset=utf-8",
    "app.js": "text/javascript; charset=utf-8",
}

# R8: each step plays its own animation in the page (names match app.js/style.css)
STEP_ANIMATIONS = {
    salon.Step.ASK_HEALTH: "ask-health",
    salon.Step.WASH_HANDS: "wash-hands",
    salon.Step.REMOVE_PRODUCT: "remove-product",
    salon.Step.FILE: "file-nails",
    salon.Step.BUFF: "buff-nails",
    salon.Step.POLISH: "polish-nails",
}


# --- Turning game objects into JSON-friendly dicts ---------------------------

def format_hour(hour: int) -> str:
    return f"{hour:02d}:00"


def look_json(look: salon.NailLook) -> dict:
    return {
        "has_product": look.has_product,
        "filed": look.filed,
        "buffed": look.buffed,
        "polish_color": look.polish_color,
        "polish_hex": salon.POLISH_COLORS.get(look.polish_color),
    }


def nails_json(client: salon.Client, steps: list[salon.Step]) -> dict:
    return {area: look_json(look)
            for area, look in salon.nail_looks(client, steps).items()}


def client_json(client: salon.Client | None) -> dict | None:
    if client is None:
        return None
    return {
        "hour": client.hour,
        "time": format_hour(client.hour),
        "kind": client.kind,
        "service": client.service.name,
        "price": client.service.price,
        "areas": list(client.service.areas),
        "has_product": client.has_product,
        "polish_color": client.polish_color,
        "polish_hex": salon.POLISH_COLORS[client.polish_color],
        "working_area": salon.working_area(client, []),
        "nails": nails_json(client, []),
    }


def day_json(day: salon.DayResult) -> dict:
    return {
        "total": day.total,
        "goal": day.goal,
        "goal_met": day.goal_met,
        "results": [
            {
                "time": format_hour(r.client.hour),
                "kind": r.client.kind,
                "service": r.client.service.name,
                "stars": r.stars,
                "earned": r.earned,
            }
            for r in day.results
        ],
    }


# --- The server ---------------------------------------------------------------

class BadRequest(Exception):
    """The page sent something the game can't use; becomes a 400 reply."""


class SalonServer(ThreadingHTTPServer):
    """An HTTP server that also remembers the games being played."""

    daemon_threads = True

    def __init__(self, address, seed: int | None = None):
        super().__init__(address, SalonHandler)
        self.seed = seed
        self.games: dict[str, salon.Game] = {}
        self._ids = itertools.count(1)

    def new_game(self) -> tuple[str, salon.Game]:
        game_id = str(next(self._ids))
        self.games[game_id] = salon.Game(random.Random(self.seed))
        return game_id, self.games[game_id]

    def get_game(self, body: dict) -> salon.Game:
        game = self.games.get(str(body.get("game_id")))
        if game is None:
            raise BadRequest("unknown game; start a new one")
        return game


class SalonHandler(BaseHTTPRequestHandler):
    server: SalonServer

    def log_message(self, format, *args):  # keep the terminal quiet
        pass

    # GET: the page and its files
    def do_GET(self):
        path = urlsplit(self.path).path
        name = "index.html" if path == "/" else path.removeprefix("/static/")
        if path != "/" and not path.startswith("/static/"):
            name = ""
        if name not in STATIC_FILES:
            self._send(HTTPStatus.NOT_FOUND, b"Not found", "text/plain")
            return
        self._send(HTTPStatus.OK, (STATIC_DIR / name).read_bytes(), STATIC_FILES[name])

    # POST: the game interface
    def do_POST(self):
        routes = {
            "/api/new-game": self._new_game,
            "/api/step": self._step,
            "/api/finish": self._finish,
        }
        route = routes.get(urlsplit(self.path).path)
        if route is None:
            self._send_json(HTTPStatus.NOT_FOUND, {"error": "no such address"})
            return
        try:
            length = int(self.headers.get("Content-Length") or 0)
            body = json.loads(self.rfile.read(length) or b"{}")
            if not isinstance(body, dict):
                raise BadRequest("expected a JSON object")
            self._send_json(HTTPStatus.OK, route(body))
        except (BadRequest, ValueError) as err:
            self._send_json(HTTPStatus.BAD_REQUEST, {"error": str(err)})

    def _new_game(self, body: dict) -> dict:
        game_id, game = self.server.new_game()
        return {
            "game_id": game_id,
            "goal": salon.DAILY_GOAL,
            "total_clients": len(game.clients),
            "client_number": 1,
            "client": client_json(game.current_client),
            "steps": [
                {"id": s.name, "label": s.value, "animation": STEP_ANIMATIONS[s]}
                for s in salon.Step
            ],
        }

    def _step(self, body: dict) -> dict:
        game = self.server.get_game(body)
        try:
            step = salon.Step[str(body.get("step"))]
        except KeyError:
            raise BadRequest(f"unknown step: {body.get('step')}") from None
        game.take_step(step)  # ValueError if the day is over
        client = game.current_client
        reply = {
            "step": step.name,
            "label": step.value,
            "animation": STEP_ANIMATIONS[step],
            "working_area": salon.working_area(client, game.steps),
            "nails": nails_json(client, game.steps),
            "steps_taken": [s.value for s in game.steps],
        }
        if step is salon.Step.ASK_HEALTH:
            reply["health_answer"] = salon.health_answer(client)
        return reply

    def _finish(self, body: dict) -> dict:
        game = self.server.get_game(body)
        client = game.current_client
        result = game.finish()  # ValueError if the day is over
        return {
            "result": {
                "satisfied": result.satisfied,
                "stars": result.stars,
                "earned": result.earned,
            },
            "correct_steps": [s.value for s in salon.required_steps(client)],
            "total_so_far": sum(r.earned for r in game.results),
            "client_number": game.index + 1,
            "next_client": client_json(game.current_client),
            "day": day_json(game.day_result()) if game.is_over else None,
        }

    def _send_json(self, status: HTTPStatus, data: dict) -> None:
        self._send(status, json.dumps(data).encode(), "application/json")

    def _send(self, status: HTTPStatus, body: bytes, content_type: str) -> None:
        self.send_response(status)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(body)


def make_server(host: str = HOST, port: int = DEFAULT_PORT,
                seed: int | None = None) -> SalonServer:
    """Create the server. Port 0 means "any free port"."""
    return SalonServer((host, port), seed)


def main(argv: list[str] | None = None) -> SalonServer:
    """R7: the one command. Start the server and open the game in the browser."""
    parser = argparse.ArgumentParser(description="Nail Salon Tycoon in your browser")
    parser.add_argument("--seed", type=int, help="replay the same day")
    parser.add_argument("--port", type=int, default=DEFAULT_PORT,
                        help=f"port to use (default {DEFAULT_PORT})")
    parser.add_argument("--no-browser", action="store_true",
                        help="don't open the browser automatically")
    args = parser.parse_args(argv)

    try:
        server = make_server(HOST, args.port, args.seed)
    except OSError:  # that port is busy (maybe the game is already running)
        server = make_server(HOST, 0, args.seed)
    host, port = server.server_address[:2]
    url = f"http://{host}:{port}/"

    print(f"Nail Salon Tycoon is open at {url}")
    print("Press Ctrl+C here to close the salon.")
    if not args.no_browser:
        webbrowser.open(url)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nThe salon is closed. Goodbye!")
    finally:
        server.server_close()
    return server


if __name__ == "__main__":
    main()
