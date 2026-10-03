#!/usr/bin/env python3
"""Repository inventory for repo-deep-dive Wave 0 (read-only, repo-agnostic).

Scans any repository layout and emits a portable inventory.json: file/line
counts, detected stacks, entry points, routes, migrations, workflows,
containers, tests, and secret-adjacent filenames (names only, never contents).

Usage:
  python3 tools/repo_inventory.py <repo-root> [-o inventory.json]

Read-only against the target repo; only the output file is written.
Designed for new/adapted repos where prompt 01 has no prior map.
Paths in output always use forward slashes.
"""

import argparse
import datetime
import fnmatch
import json
import os
import re
import subprocess
import sys

sys.dont_write_bytecode = True

SKIP_DIRS = {
    ".git", "node_modules", ".pnpm", ".next", "dist", "build", "out",
    "vendor", "venv", ".venv", "__pycache__", ".tox", "target",
    ".idea", ".vscode", "coverage", ".nyc_output",
}

CODE_EXTS = {
    ".ts", ".tsx", ".js", ".jsx", ".mjs", ".cjs", ".py", ".rb", ".go",
    ".rs", ".java", ".cs", ".php", ".swift", ".kt", ".c", ".h",
    ".cpp", ".hpp", ".sql", ".tf", ".sh", ".ps1", ".yaml", ".yml",
    ".json", ".toml",
}

STACK_MARKERS = [
    ("package.json", "node"),
    ("pnpm-lock.yaml", "pnpm"),
    ("package-lock.json", "npm"),
    ("requirements.txt", "python-pip"),
    ("pyproject.toml", "python"),
    ("Pipfile", "python-pipenv"),
    ("Cargo.toml", "rust"),
    ("go.mod", "go"),
    ("composer.json", "php"),
    ("Gemfile", "ruby"),
    ("pom.xml", "java-maven"),
    ("build.gradle", "java-gradle"),
    ("build.sbt", "scala-sbt"),
    ("Dockerfile", "docker"),
    ("docker-compose.yml", "docker-compose"),
    ("docker-compose.yaml", "docker-compose"),
    (".github/workflows", "github-actions"),
    (".gitlab-ci.yml", "gitlab-ci"),
    ("Jenkinsfile", "jenkins"),
    ("azure-pipelines.yml", "azure-pipelines"),
    ("azure-pipelines.yaml", "azure-pipelines"),
    ("Chart.yaml", "helm"),
    ("serverless.yml", "serverless"),
    ("supabase/migrations", "supabase"),
    ("prisma/schema.prisma", "prisma"),
    ("migrations", "migrations-dir"),
    ("terraform", "terraform-dir"),
    ("k8s", "k8s-manifests"),
    ("helm", "helm"),
]

# Basename glob markers (matched against every file's basename).
GLOB_MARKERS = [
    ("*.sln", "dotnet"),
    ("*.csproj", "dotnet"),
    ("Podfile", "ios-cocoapods"),
    ("AndroidManifest.xml", "android"),
    ("*.tf", "terraform"),
]

SECRET_NAME_PATTERNS = [
    "*.pem", "*.key", "*.p12", "*.pfx", ".env", ".env.*",
    "*secret*", "*credential*", "*token*", "id_rsa*", "*.asc", "*.gpg",
]


def run_git(root, args):
    try:
        r = subprocess.run(
            ["git"] + args, capture_output=True, text=True, cwd=root,
            timeout=15,
        )
        return r.stdout.strip() if r.returncode == 0 else ""
    except Exception:
        return ""


def rel_posix(root, path):
    return os.path.relpath(path, root).replace(os.sep, "/")


def iter_files(root):
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = [d for d in dirnames if d not in SKIP_DIRS]
        for f in filenames:
            yield os.path.join(dirpath, f)


def scan_repo(root):
    inv = {
        "repo": os.path.abspath(root),
        "generated_at": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        "git": {},
        "totals": {"files": 0, "lines": 0, "by_ext": {}},
        "stacks": [],
        "entry_points": [],
        "routes": [],
        "migrations": [],
        "workflows": [],
        "containers": [],
        "tests": {"files": 0, "dirs": []},
        "secret_adjacent_files": [],
        "largest_dirs": [],
    }

    inv["git"] = {
        "branch": run_git(root, ["rev-parse", "--abbrev-ref", "HEAD"]),
        "sha": run_git(root, ["rev-parse", "--short", "HEAD"]),
        "dirty": bool(run_git(root, ["status", "--porcelain"])),
    }

    by_ext = {}
    n_files = 0
    n_lines = 0
    dir_sizes = {}
    for path in iter_files(root):
        rel = rel_posix(root, path)
        n_files += 1
        top = rel.split("/")[0] if "/" in rel else "(root)"
        dir_sizes[top] = dir_sizes.get(top, 0) + 1
        ext = os.path.splitext(path)[1].lower()
        if ext:
            by_ext[ext] = by_ext.get(ext, 0) + 1
        if ext in CODE_EXTS:
            try:
                with open(path, "r", encoding="utf-8", errors="replace") as fh:
                    n_lines += sum(1 for _ in fh)
            except OSError:
                pass
        for pat in SECRET_NAME_PATTERNS:
            if fnmatch.fnmatch(os.path.basename(path), pat):
                inv["secret_adjacent_files"].append(rel)
                break

    inv["totals"] = {"files": n_files, "lines": n_lines, "by_ext": dict(sorted(by_ext.items()))}
    inv["largest_dirs"] = [
        {"dir": d, "files": c} for d, c in sorted(dir_sizes.items(), key=lambda kv: -kv[1])[:15]
    ]
    inv["secret_adjacent_files"] = sorted(set(inv["secret_adjacent_files"]))

    for marker, stack in STACK_MARKERS:
        if os.path.exists(os.path.join(root, marker)):
            inv["stacks"].append(stack)
    for path in iter_files(root):
        base = os.path.basename(path)
        for pat, stack in GLOB_MARKERS:
            if fnmatch.fnmatch(base, pat):
                inv["stacks"].append(stack)
                break
    inv["stacks"] = sorted(set(inv["stacks"]))
    inv["ci"] = sorted(set(
        s for s in inv["stacks"]
        if s in ("github-actions", "gitlab-ci", "jenkins", "azure-pipelines")
    ))

    entry_names = ["main.ts", "main.py", "app.py", "app.ts", "server.ts",
                   "index.ts", "index.js", "main.go", "main.rs", "Main.java"]
    for path in iter_files(root):
        base = os.path.basename(path)
        if base in entry_names and len(rel_posix(root, path).split("/")) <= 4:
            inv["entry_points"].append(rel_posix(root, path))
    inv["entry_points"] = sorted(set(inv["entry_points"]))[:50]

    route_re = re.compile(
        r"(?:router|app)\.(?:get|post|put|patch|delete|use)\s*\(\s*[\"']([^\"']+)|"
        r"@(?:app|router)\.(?:get|post|put|patch|delete)\([\"']([^\"']+)|"
        r"Route::(?:get|post|put|patch|delete)\(\s*[\"']([^\"']+)"
    )
    for path in iter_files(root):
        if not path.endswith((".ts", ".js", ".py", ".rb", ".go", ".php", ".java")):
            continue
        rel = rel_posix(root, path)
        if "test" in rel.lower() or "spec" in rel.lower():
            continue
        try:
            with open(path, "r", encoding="utf-8", errors="replace") as fh:
                content = fh.read()
        except OSError:
            continue
        for m in route_re.finditer(content):
            route = m.group(1) or m.group(2) or m.group(3)
            if route:
                inv["routes"].append({"file": rel, "path": route})
                if len(inv["routes"]) >= 500:
                    break
        if len(inv["routes"]) >= 500:
            break

    for path in iter_files(root):
        rel = rel_posix(root, path)
        low = rel.lower()
        if low.endswith(".sql") and ("migrat" in low or "supabase" in low or "prisma" in low or "schema" in low):
            inv["migrations"].append(rel)
        if ".github/workflows/" in rel and rel.endswith((".yml", ".yaml")):
            inv["workflows"].append(rel)
        if os.path.basename(path) in ("Dockerfile", "Dockerfile.prod") or rel.endswith(".dockerfile"):
            inv["containers"].append(rel)
        if "test" in low or "spec" in low:
            if path.endswith((".ts", ".tsx", ".js", ".jsx", ".py", ".go", ".rs", ".rb")):
                inv["tests"]["files"] += 1
        if os.path.basename(path) in ("__tests__", "tests", "test", "e2e", "spec"):
            inv["tests"]["dirs"].append(rel)
    inv["migrations"] = sorted(set(inv["migrations"]))[:200]
    inv["workflows"] = sorted(set(inv["workflows"]))
    inv["containers"] = sorted(set(inv["containers"]))
    inv["tests"]["dirs"] = sorted(set(inv["tests"]["dirs"]))

    return inv


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("repo", help="target repository root (read-only scan)")
    ap.add_argument("-o", "--output", default=None,
                    help="write inventory.json here (default: stdout)")
    args = ap.parse_args()

    if not os.path.isdir(args.repo):
        print("error: not a directory: %s" % args.repo, file=sys.stderr)
        raise SystemExit(2)

    inv = scan_repo(os.path.abspath(args.repo))
    text = json.dumps(inv, indent=2)

    if args.output:
        with open(args.output, "w", encoding="utf-8") as fh:
            fh.write(text + "\n")
        print("wrote %s" % args.output)

    print("repo: %s" % inv["repo"])
    print("files: %d lines: %d" % (inv["totals"]["files"], inv["totals"]["lines"]))
    print("stacks: %s" % (", ".join(inv["stacks"]) or "none detected"))
    print("ci systems: %s" % (", ".join(inv["ci"]) or "none detected"))
    print("routes: %d migrations: %d workflows: %d containers: %d test_files: %d" % (
        len(inv["routes"]), len(inv["migrations"]), len(inv["workflows"]),
        len(inv["containers"]), inv["tests"]["files"]))
    print("secret-adjacent filenames (names only): %d" % len(inv["secret_adjacent_files"]))


if __name__ == "__main__":
    main()
