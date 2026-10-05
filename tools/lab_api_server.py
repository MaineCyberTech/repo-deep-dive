#!/usr/bin/env python3
"""Proxmox lab job API server (standard library only).

Serves the endpoints consumed by tools/lab_runner.py so audit/remediation work can be
dispatched to the lab:

  GET  /health                       -> {"status": "ok", ...}   (no auth)
  GET  /repos                        -> {"repos": [...]}        (auth)
  POST /sync   {repo,org,ref,token}  -> fetch/clone a repo workspace
  POST /run    {repo,cwd,command,timeout} -> run a shell command in a workspace

Auth: `Authorization: Bearer <LAB_API_TOKEN>` (constant-time compare). /health is
unauthenticated so the overlay preflight can poll it.

Config (environment, or EnvironmentFile=/etc/lab-api/env):
  LAB_API_TOKEN   required, shared secret
  LAB_API_ROOT    workspace root (default /var/lib/lab-repos)
  LAB_API_BIND    bind address (default 0.0.0.0)
  LAB_API_PORT    port (default 8722)

Security: no shell evaluation of JSON; commands run via `bash -o pipefail -c` under the
server user (root in the disposable lab guest). Clone tokens are passed as an HTTP header,
never in the URL.
"""

import base64
import hmac
import json
import os
import subprocess
import time
import urllib.parse
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

TOKEN = os.environ.get("LAB_API_TOKEN", "")
ROOT = os.environ.get("LAB_API_ROOT", "/var/lib/lab-repos")
BIND = os.environ.get("LAB_API_BIND", "0.0.0.0")
PORT = int(os.environ.get("LAB_API_PORT", "8722"))
MAX_BODY = 1 << 20


def _auth_ok(handler):
    if not TOKEN:
        return False
    header = handler.headers.get("Authorization", "")
    if not header.startswith("Bearer "):
        return False
    return hmac.compare_digest(header[len("Bearer "):].strip(), TOKEN)


def _git(args, cwd):
    try:
        p = subprocess.run(["git", *args], cwd=cwd, capture_output=True, text=True, timeout=60)
        return p.stdout.strip()
    except Exception:
        return ""


def _repo_info(path):
    return {
        "repo": os.path.basename(path),
        "head": _git(["rev-parse", "HEAD"], path),
        "branch": _git(["rev-parse", "--abbrev-ref", "HEAD"], path),
        "dirty": bool(_git(["status", "--porcelain"], path)),
    }


def _safe_name(name):
    return bool(name) and "/" not in name and name not in (".", "..") and \
        all(c.isalnum() or c in "-_." for c in name)


class Handler(BaseHTTPRequestHandler):
    server_version = "lab-api/1.0"
    protocol_version = "HTTP/1.1"

    def log_message(self, fmt, *args):
        print("[lab-api] " + (fmt % args), flush=True)

    def _send(self, code, obj):
        body = json.dumps(obj).encode()
        self.send_response(code)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def _read_json(self):
        try:
            n = int(self.headers.get("Content-Length", "0") or "0")
        except ValueError:
            return {}
        if n <= 0 or n > MAX_BODY:
            return {}
        try:
            return json.loads(self.rfile.read(n) or b"{}")
        except Exception:
            return {}

    def do_GET(self):
        path = urllib.parse.urlparse(self.path).path.rstrip("/") or "/"
        if path == "/health":
            self._send(200, {"status": "ok", "host": os.uname().nodename, "time": int(time.time())})
            return
        if not _auth_ok(self):
            self._send(401, {"error": "unauthorized"})
            return
        if path == "/repos":
            repos = []
            if os.path.isdir(ROOT):
                for name in sorted(os.listdir(ROOT)):
                    full = os.path.join(ROOT, name)
                    if os.path.exists(os.path.join(full, ".git")):
                        repos.append(_repo_info(full))
            self._send(200, {"repos": repos})
            return
        self._send(404, {"error": "not found"})

    def do_POST(self):
        if not _auth_ok(self):
            self._send(401, {"error": "unauthorized"})
            return
        path = urllib.parse.urlparse(self.path).path.rstrip("/") or "/"
        body = self._read_json()

        if path == "/sync":
            repo = str(body.get("repo") or "")
            org = str(body.get("org") or "MaineCyberTech")
            ref = str(body.get("ref") or "")
            token = str(body.get("token") or "")
            if not _safe_name(repo) or not _safe_name(org):
                self._send(400, {"error": "invalid repo/org"})
                return
            dest = os.path.join(ROOT, repo)
            os.makedirs(ROOT, exist_ok=True)
            auth = ""
            if token:
                auth = "AUTHORIZATION: Basic " + base64.b64encode(
                    ("x-access-token:" + token).encode()).decode()
            if not os.path.exists(os.path.join(dest, ".git")):
                cmd = ["git", "-c", "credential.helper="]
                if auth:
                    cmd += ["-c", "http.extraheader=" + auth]
                cmd += ["clone", "-q", "https://github.com/%s/%s.git" % (org, repo), dest]
                rc = subprocess.run(cmd, capture_output=True, text=True, timeout=1200).returncode
                if rc != 0:
                    self._send(502, {"error": "clone failed", "exit": rc})
                    return
            else:
                # Apply the same auth header to the fetch as the clone: the
                # workspace already exists, so an unauthenticated fetch would
                # silently fall back to public-only access and ignore the token.
                fetch = ["git", "-c", "credential.helper="]
                if auth:
                    fetch += ["-c", "http.extraheader=" + auth]
                fetch += ["fetch", "-q", "--all", "--tags"]
                rc = subprocess.run(fetch, cwd=dest, capture_output=True,
                                    text=True, timeout=600).returncode
                if rc != 0:
                    self._send(502, {"error": "fetch failed", "exit": rc})
                    return
            if ref:
                # Fail closed: an unresolvable ref must not report success with a
                # stale/previous checkout still in place.
                rc = subprocess.run(["git", "checkout", "-q", ref], cwd=dest,
                                    capture_output=True, text=True, timeout=120).returncode
                if rc != 0:
                    self._send(404, {"error": "ref not found", "ref": ref})
                    return
            info = _repo_info(dest)
            info["cwd"] = dest
            info["exit"] = 0
            self._send(200, info)
            return

        if path == "/run":
            repo = str(body.get("repo") or "")
            cwd = str(body.get("cwd") or "")
            command = str(body.get("command") or "")
            try:
                timeout = int(body.get("timeout") or 1800)
            except (TypeError, ValueError):
                timeout = 1800
            if not command:
                self._send(400, {"error": "command required"})
                return
            if not cwd:
                cwd = os.path.join(ROOT, repo) if repo else ROOT
            if not os.path.isdir(cwd):
                self._send(400, {"error": "cwd not found", "cwd": cwd})
                return
            t0 = time.time()
            try:
                p = subprocess.run(["bash", "-o", "pipefail", "-c", command], cwd=cwd,
                                   capture_output=True, text=True, timeout=timeout)
                out, err, rc = p.stdout, p.stderr, p.returncode
            except subprocess.TimeoutExpired as e:
                def _s(v):
                    return v.decode() if isinstance(v, bytes) else (v or "")
                out, err, rc = _s(e.stdout), _s(e.stderr), 124
            self._send(200, {"stdout": out, "stderr": err, "exit": rc,
                             "duration": round(time.time() - t0, 3), "cwd": cwd})
            return

        self._send(404, {"error": "not found"})


def main():
    if not TOKEN:
        raise SystemExit("LAB_API_TOKEN is not set")
    os.makedirs(ROOT, exist_ok=True)
    srv = ThreadingHTTPServer((BIND, PORT), Handler)
    print("[lab-api] listening on %s:%d root=%s" % (BIND, PORT, ROOT), flush=True)
    srv.serve_forever()


if __name__ == "__main__":
    main()
