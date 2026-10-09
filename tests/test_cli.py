"""The compare command is the product. These tests run it."""

from __future__ import annotations

import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SAMPLE = """\
ONLY example.env  SENTRY_DSN
ONLY local.env  DEBUG
DIFFER  DATABASE_URL
SAME  2
"""
SECRETS = (
    "acre-app",
    "s3cret-db",
    "other-secret",
    "sentry-token-99",
    "redis://localhost:6379/0",
    "postgres://",
)


def run(args: list[str]) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, "-m", "envdiff", *args],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
    )


class EnvdiffCommandTest(unittest.TestCase):
    def test_sample_files_match_the_readme_and_hide_values(self) -> None:
        result = run(["fixtures/example.env", "fixtures/local.env"])
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(result.stdout, SAMPLE)
        self.assertIn(SAMPLE.strip(), (ROOT / "README.md").read_text(encoding="utf-8"))
        leaked = result.stdout + result.stderr
        for secret in SECRETS:
            self.assertNotIn(secret, leaked)

    def test_same_files_print_the_same_report_twice(self) -> None:
        args = ["fixtures/example.env", "fixtures/local.env"]
        first = run(args)
        second = run(args)
        self.assertEqual(first.returncode, 0, first.stderr)
        self.assertEqual(first.stdout, second.stdout)

    def test_quotes_and_export_count_as_the_same_value(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            left = Path(tmp) / "a.env"
            right = Path(tmp) / "b.env"
            left.write_text('export TOKEN="abc"\n# note\n\nNAME=acre\n', encoding="utf-8")
            right.write_text("TOKEN=abc\nNAME=acre\n", encoding="utf-8")
            result = run([str(left), str(right)])
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(result.stdout, "SAME  2\n")
        self.assertNotIn("abc", result.stdout)
        self.assertNotIn("acre", result.stdout)

    def test_empty_value_is_present_and_can_differ(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            left = Path(tmp) / "a.env"
            right = Path(tmp) / "b.env"
            left.write_text("TOKEN=\n", encoding="utf-8")
            right.write_text("TOKEN=set\n", encoding="utf-8")
            result = run([str(left), str(right)])
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(result.stdout, "DIFFER  TOKEN\nSAME  0\n")
        self.assertNotIn("set", result.stdout)

    def test_duplicate_key_is_an_error(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            left = Path(tmp) / "a.env"
            right = Path(tmp) / "b.env"
            left.write_text("TOKEN=one\nTOKEN=two\n", encoding="utf-8")
            right.write_text("TOKEN=one\n", encoding="utf-8")
            result = run([str(left), str(right)])
        self.assertEqual(result.returncode, 1)
        self.assertIn("duplicate key TOKEN", result.stderr)
        self.assertEqual(result.stdout, "")
        self.assertNotIn("one", result.stderr)
        self.assertNotIn("two", result.stderr)


if __name__ == "__main__":
    unittest.main()
