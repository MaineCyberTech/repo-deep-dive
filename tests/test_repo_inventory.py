"""Tests for tools/repo_inventory.py: test-path detection, route derivation, scan."""

import json
import pathlib
import sys
import tempfile
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))

import repo_inventory  # noqa: E402


class IsTestPathTest(unittest.TestCase):
    def test_true_positives(self):
        for rel in ("tests/test_lib.py", "app/tests/helpers.ts",
                    "src/foo.test.ts", "src/foo.spec.js",
                    "tools/test_repo_inventory.py", "pkg/util_test.py"):
            self.assertTrue(repo_inventory.is_test_path(rel), rel)

    def test_false_positive_guarded(self):
        # "species.ts" contains "spec" but is not a test.
        self.assertFalse(repo_inventory.is_test_path("src/data/species.ts"))
        self.assertFalse(repo_inventory.is_test_path("src/latest.ts"))
        self.assertFalse(repo_inventory.is_test_path("README.md"))


class RouteDerivationTest(unittest.TestCase):
    def test_app_router_route(self):
        self.assertEqual(
            repo_inventory.app_router_route("src/app/users/[id]/route.ts"),
            "/users/[id]")

    def test_app_router_route_group(self):
        self.assertEqual(
            repo_inventory.app_router_route("src/app/(marketing)/about/route.ts"),
            "/about")

    def test_app_router_not_app(self):
        self.assertIsNone(repo_inventory.app_router_route("src/lib/route.ts"))

    def test_pages_api_route(self):
        self.assertEqual(
            repo_inventory.pages_api_route("pages/api/users/index.ts"),
            "/api/users")

    def test_pages_api_route_plain(self):
        self.assertEqual(
            repo_inventory.pages_api_route("pages/api/health.ts"),
            "/api/health")

    def test_pages_api_route_not_pages(self):
        self.assertIsNone(repo_inventory.pages_api_route("src/api/health.ts"))


class ScanRepoTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = pathlib.Path(self.tmp.name)
        (self.root / "package.json").write_text("{}", encoding="utf-8")
        (self.root / ".github" / "workflows").mkdir(parents=True)
        (self.root / ".github" / "workflows" / "ci.yml").write_text(
            "name: ci\non: push\n", encoding="utf-8")
        (self.root / "app.py").write_text(
            'ROUTES = [("GET", "/health")]\n'
            'if __name__ == "__main__":\n    pass\n', encoding="utf-8")
        (self.root / "schema.sql").write_text(
            "CREATE TABLE users (id int);\n", encoding="utf-8")
        (self.root / "tests").mkdir()
        (self.root / "tests" / "test_app.py").write_text("", encoding="utf-8")

    def tearDown(self):
        self.tmp.cleanup()

    def test_scan_detects_stack_routes_tables_tests(self):
        inv = repo_inventory.scan_repo(str(self.root))
        self.assertIn("node", inv["stacks"])
        self.assertIn("github-actions", inv["stacks"])
        self.assertIn("github-actions", inv["ci"])
        paths = {r["path"] for r in inv["routes"]}
        self.assertIn("/health", paths)
        tables = {t["table"] for t in inv["schema_tables"]}
        self.assertIn("users", tables)
        self.assertIn("app.py", inv["entry_points"])
        self.assertEqual(inv["tests"]["files"], 1)
        self.assertIn("tests", inv["tests"]["dirs"])

    def test_scan_isolated_from_git(self):
        # A non-git directory must not crash and must report empty git fields.
        inv = repo_inventory.scan_repo(str(self.root))
        self.assertEqual(inv["git"]["sha"], "")

    def test_scan_output_is_json_serializable(self):
        inv = repo_inventory.scan_repo(str(self.root))
        json.dumps(inv)  # must not raise


if __name__ == "__main__":
    unittest.main()
