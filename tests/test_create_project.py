from __future__ import annotations

import os
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
SRC_ROOT = REPO_ROOT / "src"


class CreateProjectTests(unittest.TestCase):
    def run_module(self, *args: str) -> subprocess.CompletedProcess[str]:
        env = os.environ.copy()
        existing_pythonpath = env.get("PYTHONPATH")
        env["PYTHONPATH"] = (
            str(SRC_ROOT)
            if not existing_pythonpath
            else f"{SRC_ROOT}{os.pathsep}{existing_pythonpath}"
        )

        return subprocess.run(
            [sys.executable, "-m", "seed_scaffold", *args],
            cwd=REPO_ROOT,
            env=env,
            text=True,
            capture_output=True,
            check=False,
        )

    def test_list_templates(self) -> None:
        result = self.run_module("--list-templates")

        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("meson-c-lib", result.stdout)
        self.assertIn("Meson C Library", result.stdout)

    def test_module_entry_point_lists_templates(self) -> None:
        result = self.run_module("--list-templates")

        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("meson-c-lib", result.stdout)

    def test_invalid_version_is_rejected(self) -> None:
        result = self.run_module(
            "--name",
            "demo",
            "--version",
            "1.2",
            "--description",
            "example",
        )

        self.assertNotEqual(result.returncode, 0)
        self.assertIn("Version must be in format X.Y.Z", result.stderr)

    def test_invalid_slug_is_rejected(self) -> None:
        result = self.run_module(
            "--name",
            "123 demo",
            "--version",
            "1.2.3",
            "--description",
            "example",
        )

        self.assertNotEqual(result.returncode, 0)
        self.assertIn("Project slug must match", result.stderr)

    def test_custom_slug_allows_non_identifier_display_name(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            output_dir = Path(temp_dir) / "demo-output"
            result = self.run_module(
                "--name",
                "123 demo library",
                "--slug",
                "demo_library",
                "--version",
                "1.2.3",
                "--description",
                "Example library",
                "--author",
                "Jane Developer",
                "--year",
                "2030",
                "--output",
                str(output_dir),
            )

            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertTrue(
                (output_dir / "include" / "demo_library.h").is_file()
            )

    def test_dry_run_does_not_write_files(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            output_dir = Path(temp_dir) / "preview"
            result = self.run_module(
                "--template",
                "meson-c-lib",
                "--name",
                "Preview Library",
                "--version",
                "0.1.0",
                "--description",
                "Preview only",
                "--output",
                str(output_dir),
                "--dry-run",
            )

            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertFalse(output_dir.exists())
            self.assertIn("Dry run", result.stdout)
            self.assertIn("include/preview_library.h", result.stdout)

    def test_existing_empty_directory_requires_force(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            output_dir = Path(temp_dir) / "existing"
            output_dir.mkdir()

            result = self.run_module(
                "--name",
                "demo",
                "--version",
                "1.0.0",
                "--description",
                "example",
                "--output",
                str(output_dir),
            )

            self.assertNotEqual(result.returncode, 0)
            self.assertIn("Pass --force", result.stderr)

    def test_project_generation_replaces_placeholders(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            output_dir = Path(temp_dir) / "sample"
            result = self.run_module(
                "--template",
                "meson-c-lib",
                "--name",
                "Sample Library",
                "--version",
                "1.2.3",
                "--description",
                "Example generated library",
                "--author",
                "Jane Developer",
                "--year",
                "2035",
                "--output",
                str(output_dir),
            )

            self.assertEqual(result.returncode, 0, result.stderr)

            expected_files = [
                output_dir / "LICENSE",
                output_dir / "README.md",
                output_dir / "meson.build",
                output_dir / "include" / "sample_library.h",
                output_dir / "src" / "sample_library.c",
                output_dir / "tests" / "test_sample_library.c",
            ]
            for file_path in expected_files:
                self.assertTrue(
                    file_path.is_file(), f"Missing generated file: {file_path}"
                )

            license_text = (output_dir / "LICENSE").read_text(encoding="utf-8")
            readme_text = (output_dir / "README.md").read_text(
                encoding="utf-8"
            )
            meson_text = (output_dir / "meson.build").read_text(
                encoding="utf-8"
            )

            self.assertIn("Jane Developer", license_text)
            self.assertIn("2035", license_text)
            self.assertNotIn("{{PROJECT_", readme_text)
            self.assertNotIn("USERNAME/REPO", readme_text)
            self.assertIn("'sample_library'", meson_text)
            self.assertIn("version: '1.2.3'", meson_text)
            self.assertIn(
                "meson.override_dependency('sample_library'", meson_text
            )

    @unittest.skipUnless(shutil.which("git"), "git is required for this test")
    def test_init_git_creates_repository(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            output_dir = Path(temp_dir) / "git-project"
            result = self.run_module(
                "--name",
                "git project",
                "--version",
                "1.0.0",
                "--description",
                "example",
                "--output",
                str(output_dir),
                "--init-git",
            )

            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertTrue((output_dir / ".git").is_dir())

    @unittest.skipUnless(
        shutil.which("meson") and shutil.which("ninja") and shutil.which("cc"),
        "meson, ninja, and cc are required for this test",
    )
    def test_generated_project_builds_and_tests(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            output_dir = Path(temp_dir) / "build-check"
            generate_result = self.run_module(
                "--template",
                "meson-c-lib",
                "--name",
                "Build Check",
                "--version",
                "1.2.3",
                "--description",
                "Build validation",
                "--output",
                str(output_dir),
            )
            self.assertEqual(
                generate_result.returncode, 0, generate_result.stderr
            )

            commands = [
                [
                    "meson",
                    "setup",
                    "build",
                    "--buildtype=debug",
                    "-Dbuild_tests=true",
                ],
                ["meson", "compile", "-C", "build"],
                ["meson", "test", "-C", "build", "--verbose"],
            ]

            for command in commands:
                result = subprocess.run(
                    command,
                    cwd=output_dir,
                    text=True,
                    capture_output=True,
                    check=False,
                )
                self.assertEqual(
                    result.returncode,
                    0,
                    msg=(
                        f"Command failed: {' '.join(command)}\n"
                        f"stdout:\n{result.stdout}\n"
                        f"stderr:\n{result.stderr}"
                    ),
                )


if __name__ == "__main__":
    unittest.main()
