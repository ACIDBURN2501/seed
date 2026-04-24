from __future__ import annotations

import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[1]
SRC_ROOT = REPO_ROOT / "src"


def run_module(*args: str) -> subprocess.CompletedProcess[str]:
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


def test_list_templates() -> None:
    result = run_module("--list-templates")

    assert result.returncode == 0, result.stderr
    assert "meson-c-lib" in result.stdout
    assert "Meson C Library" in result.stdout


def test_module_entry_point_lists_templates() -> None:
    result = run_module("--list-templates")

    assert result.returncode == 0, result.stderr
    assert "meson-c-lib" in result.stdout


def test_invalid_version_is_rejected() -> None:
    result = run_module(
        "--name",
        "demo",
        "--proj-version",
        "1.2",
        "--description",
        "example",
    )

    assert result.returncode != 0
    assert "Version must be in format X.Y.Z" in result.stderr


def test_invalid_slug_is_rejected() -> None:
    result = run_module(
        "--name",
        "123 demo",
        "--proj-version",
        "1.2.3",
        "--description",
        "example",
    )

    assert result.returncode != 0
    assert "Project slug must match" in result.stderr


def test_custom_slug_allows_non_identifier_display_name() -> None:
    with tempfile.TemporaryDirectory() as temp_dir:
        output_dir = Path(temp_dir) / "demo-output"
        result = run_module(
            "--name",
            "123 demo library",
            "--slug",
            "demo_library",
            "--proj-version",
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

        assert result.returncode == 0, result.stderr
        assert (output_dir / "include" / "demo_library.h").is_file()


def test_dry_run_does_not_write_files() -> None:
    with tempfile.TemporaryDirectory() as temp_dir:
        output_dir = Path(temp_dir) / "preview"
        result = run_module(
            "--template",
            "meson-c-lib",
            "--name",
            "Preview Library",
            "--proj-version",
            "0.1.0",
            "--description",
            "Preview only",
            "--output",
            str(output_dir),
            "--dry-run",
        )

        assert result.returncode == 0, result.stderr
        assert not output_dir.exists()
        assert "Dry run" in result.stdout
        assert "include/preview_library.h" in result.stdout


def test_existing_empty_directory_requires_force() -> None:
    with tempfile.TemporaryDirectory() as temp_dir:
        output_dir = Path(temp_dir) / "existing"
        output_dir.mkdir()

        result = run_module(
            "--name",
            "demo",
            "--proj-version",
            "1.0.0",
            "--description",
            "example",
            "--output",
            str(output_dir),
        )

        assert result.returncode != 0
        assert "Pass --force" in result.stderr


def test_project_generation_replaces_placeholders() -> None:
    with tempfile.TemporaryDirectory() as temp_dir:
        output_dir = Path(temp_dir) / "sample"
        result = run_module(
            "--template",
            "meson-c-lib",
            "--name",
            "Sample Library",
            "--proj-version",
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

        assert result.returncode == 0, result.stderr

        expected_files = [
            output_dir / "LICENSE",
            output_dir / "README.md",
            output_dir / "meson.build",
            output_dir / "include" / "sample_library.h",
            output_dir / "include" / "sample_library_conf.h",
            output_dir / "src" / "sample_library.c",
            output_dir / "tests" / "test_sample_library.c",
        ]
        for file_path in expected_files:
            assert file_path.is_file(), f"Missing generated file: {file_path}"

        license_text = (output_dir / "LICENSE").read_text(encoding="utf-8")
        readme_text = (output_dir / "README.md").read_text(encoding="utf-8")
        meson_text = (output_dir / "meson.build").read_text(encoding="utf-8")

        assert "Jane Developer" in license_text
        assert "2035" in license_text
        assert "{{PROJECT_" not in readme_text
        assert "USERNAME/REPO" not in readme_text
        assert "'sample_library'" in meson_text
        assert "version: '1.2.3'" in meson_text
        assert "meson.override_dependency('sample_library'" in meson_text

        # Verify configuration header was generated
        conf_header = (
            output_dir / "include" / "sample_library_conf.h"
        ).read_text(encoding="utf-8")
        assert "SAMPLE_LIBRARY_MAX" in conf_header
        assert "SAMPLE_LIBRARY_MIN" in conf_header


@pytest.mark.skipif(
    not shutil.which("git"), reason="git is required for this test"
)
def test_init_git_creates_repository() -> None:
    with tempfile.TemporaryDirectory() as temp_dir:
        output_dir = Path(temp_dir) / "git-project"
        result = run_module(
            "--name",
            "git project",
            "--proj-version",
            "1.0.0",
            "--description",
            "example",
            "--output",
            str(output_dir),
            "--init-git",
        )

        assert result.returncode == 0, result.stderr
        assert (output_dir / ".git").is_dir()


@pytest.mark.skipif(
    not (
        shutil.which("meson") and shutil.which("ninja") and shutil.which("cc")
    ),
    reason="meson, ninja, and cc are required for this test",
)
def test_generated_project_builds_and_tests() -> None:
    with tempfile.TemporaryDirectory() as temp_dir:
        output_dir = Path(temp_dir) / "build-check"
        generate_result = run_module(
            "--template",
            "meson-c-lib",
            "--name",
            "Build Check",
            "--proj-version",
            "1.2.3",
            "--description",
            "Build validation",
            "--output",
            str(output_dir),
        )
        assert generate_result.returncode == 0, generate_result.stderr

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
            msg = (
                f"Command failed: {' '.join(command)}\n"
                f"stdout:\n{result.stdout}\n"
                f"stderr:\n{result.stderr}"
            )
            assert result.returncode == 0, msg


def test_template_ci_uses_master_branch() -> None:
    """Verify the template CI workflow targets 'master', not 'main'."""
    ci_path = (
        SRC_ROOT
        / "seed_scaffold"
        / "templates"
        / "meson-c-lib"
        / "files"
        / ".github"
        / "workflows"
        / "ci.yml"
    )
    content = ci_path.read_text(encoding="utf-8")
    assert 'branches: ["master"]' in content
    assert 'branches: ["main"]' not in content


def test_generated_project_includes_changelog() -> None:
    """Verify common files (CHANGELOG.md) appear in generated output."""
    with tempfile.TemporaryDirectory() as temp_dir:
        output_dir = Path(temp_dir) / "changelog-check"
        result = run_module(
            "--template",
            "meson-c-lib",
            "--name",
            "Changelog Check",
            "--proj-version",
            "1.0.0",
            "--description",
            "Test",
            "--output",
            str(output_dir),
        )

        assert result.returncode == 0, result.stderr
        assert (output_dir / "CHANGELOG.md").is_file(), (
            "CHANGELOG.md should be included from common files"
        )


def test_common_not_listed_as_template() -> None:
    """Verify the common/ directory is not exposed as a template."""
    result = run_module("--list-templates")

    assert result.returncode == 0, result.stderr
    assert "common" not in result.stdout
