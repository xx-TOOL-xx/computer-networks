"""Tiny in-memory REST API used for the HTTP methods task.

Run:  python3 test_api.py   (listens on http://localhost:8000)

GET  /tasks        -> 200, list of tasks
POST /tasks        -> 201, the created task and a Location header
"""
import json
from http.server import BaseHTTPRequestHandler, HTTPServer

tasks = []


class Handler(BaseHTTPRequestHandler):
    protocol_version = "HTTP/1.1"

    def _send(self, status, payload, headers=None):
        body = json.dumps(payload).encode()
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        for name, value in (headers or {}).items():
            self.send_header(name, value)
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):
        if self.path == "/tasks":
            self._send(200, tasks)
        else:
            self._send(404, {"error": "Not found"})

    def do_POST(self):
        if self.path != "/tasks":
            self._send(404, {"error": "Not found"})
            return
        length = int(self.headers.get("Content-Length", 0))
        try:
            data = json.loads(self.rfile.read(length) or b"{}")
        except json.JSONDecodeError:
            self._send(400, {"error": "Body must be valid JSON"})
            return
        if not isinstance(data, dict) or not data.get("title"):
            self._send(400, {"error": "Field 'title' is required"})
            return
        task = {"id": len(tasks) + 1, "title": data["title"], "done": False}
        tasks.append(task)
        self._send(201, task, {"Location": f"/tasks/{task['id']}"})

    def log_message(self, *args):
        pass


if __name__ == "__main__":
    HTTPServer(("0.0.0.0", 8000), Handler).serve_forever()
