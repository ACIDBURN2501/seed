"""Project template scaffolder CLI."""

from __future__ import annotations

import argparse
import json
import re
import shutil
import subprocess
import sys
from dataclasses import dataclass
from datetime import date
from pathlib import Path
from typing import Any, NoReturn, Sequence

VERSION_RE = re.compile(r"^\d+\.\d+\.\d+$")
SLUG_RE = re.compile(r"^[a-z][a-z0-9_]*$")
DEFAULT_TEMPLATE = "meson-c-lib"


@dataclass(frozen=True)
class TemplateManifest:
    """Metadata describing a project template."""

    template_id: str
    name: str
    description: str
    root_dir: Path
    files_dir: Path


def fail(message: str) -> NoReturn:
    """Print an error and exit."""
    print(f"Error: {message}", file=sys.stderr)
    raise SystemExit(1)


def get_package_root() -> Path:
    """Return the root directory of the installed package."""
    return Path(__file__).resolve().parent


def get_templates_root() -> Path:
    """Return the directory containing all templates."""
    return get_package_root() / "templates"


def normalize_slug(name: str) -> str:
    """Convert a display name into a filesystem-friendly project slug."""
    slug = re.sub(r"[^A-Za-z0-9]+", "_", name.strip()).strip("_").lower()
    slug = re.sub(r"_+", "_", slug)
    return slug


def validate_project_name(name: str) -> str:
    """Validate the display name supplied by the user."""
    cleaned_name = name.strip()
    if not cleaned_name:
        fail("Project name must not be empty")
    return cleaned_name


def validate_slug(slug: str) -> str:
    """Validate a project slug used for file names and C identifiers."""
    if not slug:
        fail(
            "Project slug resolved to an empty value; choose a different "
            "name or pass --slug"
        )

    if not SLUG_RE.fullmatch(slug):
        fail(
            "Project slug must match [a-z][a-z0-9_]*; "
            f"got {slug!r}. Pass --slug to override."
        )

    return slug


def load_manifest_data(manifest_path: Path) -> dict[str, Any]:
    """Load and validate raw manifest data."""
    try:
        manifest_data = json.loads(manifest_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        fail(f"Invalid template manifest {manifest_path}: {exc}")

    if not isinstance(manifest_data, dict):
        fail(f"Template manifest must contain a JSON object: {manifest_path}")

    return manifest_data


def load_template_manifest(template_dir: Path) -> TemplateManifest:
    """Load a template manifest from disk."""
    manifest_path = template_dir / "template.json"
    if not manifest_path.exists():
        fail(f"Missing template manifest: {manifest_path}")

    manifest_data = load_manifest_data(manifest_path)
    template_id = manifest_data.get("id") or template_dir.name
    files_dir_name = manifest_data.get("files_dir", "files")

    if not isinstance(template_id, str) or not template_id.strip():
        fail(
            f"Template manifest id must be a non-empty string: {manifest_path}"
        )

    if not isinstance(files_dir_name, str) or not files_dir_name.strip():
        message = "Template manifest files_dir must be a non-empty string: "
        fail(f"{message}{manifest_path}")

    files_dir = template_dir / files_dir_name

    if not files_dir.is_dir():
        fail(f"Template files directory does not exist: {files_dir}")

    name = manifest_data.get("name", template_id)
    description = manifest_data.get("description", "")

    if not isinstance(name, str):
        fail(f"Template manifest name must be a string: {manifest_path}")
    if not isinstance(description, str):
        fail(
            f"Template manifest description must be a string: {manifest_path}"
        )

    return TemplateManifest(
        template_id=template_id,
        name=name,
        description=description,
        root_dir=template_dir,
        files_dir=files_dir,
    )


def discover_templates() -> dict[str, TemplateManifest]:
    """Discover all available templates."""
    templates_root = get_templates_root()
    if not templates_root.is_dir():
        fail(f"Templates directory not found: {templates_root}")

    templates: dict[str, TemplateManifest] = {}
    for template_dir in sorted(templates_root.iterdir()):
        if not template_dir.is_dir():
            continue

        manifest = load_template_manifest(template_dir)
        if manifest.template_id in templates:
            fail(f"Duplicate template id found: {manifest.template_id}")

        templates[manifest.template_id] = manifest

    if not templates:
        fail(f"No templates found in {templates_root}")

    return templates


def build_substitutions(
    args: argparse.Namespace, project_name: str, project_slug: str
) -> dict[str, str]:
    """Construct the placeholder mapping used in file contents and paths."""
    version_major, version_minor, version_patch = args.version.split(".")
    project_upper = project_slug.upper()

    return {
        "{{PROJECT_NAME}}": project_name,
        "{{PROJECT_SLUG}}": project_slug,
        "{{PROJECT_LOWER}}": project_slug,
        "{{PROJECT_UPPER}}": project_upper,
        "{{VERSION}}": args.version,
        "{{VERSION_MAJOR}}": version_major,
        "{{VERSION_MINOR}}": version_minor,
        "{{VERSION_PATCH}}": version_patch,
        "{{DESCRIPTION}}": args.description,
        "{{AUTHOR}}": args.author,
        "{{YEAR}}": str(args.year),
        "__PROJECT_NAME__": project_name,
        "__PROJECT_SLUG__": project_slug,
        "__PROJECT_UPPER__": project_upper,
    }


def substitute_tokens(value: str, substitutions: dict[str, str]) -> str:
    """Apply all placeholder substitutions to a string."""
    for placeholder, replacement in substitutions.items():
        value = value.replace(placeholder, replacement)
    return value


def render_relative_path(
    relative_path: Path, substitutions: dict[str, str]
) -> Path:
    """Apply placeholder substitutions to a relative filesystem path."""
    rendered_parts = [
        substitute_tokens(part, substitutions) for part in relative_path.parts
    ]
    return Path(*rendered_parts)


def ensure_output_directory(
    output_dir: Path, force: bool, dry_run: bool
) -> None:
    """Validate and prepare the output directory."""
    if output_dir.exists():
        if not output_dir.is_dir():
            fail(f"Output path exists and is not a directory: {output_dir}")

        if any(output_dir.iterdir()):
            fail(
                "Output directory already exists and is not empty: "
                f"{output_dir}. "
                "Choose a different path or empty it first."
            )

        if not force:
            fail(
                f"Output directory already exists: {output_dir}. "
                "Pass --force to write into an existing empty directory."
            )
        return

    if not dry_run:
        output_dir.mkdir(parents=True, exist_ok=False)


def copy_template_file(
    src_path: Path,
    dest_path: Path,
    substitutions: dict[str, str],
    dry_run: bool,
) -> None:
    """Copy a template file, substituting placeholders in text content."""
    try:
        content = src_path.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        if dry_run:
            return

        dest_path.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(src_path, dest_path)
        return

    content = substitute_tokens(content, substitutions)

    if dry_run:
        return

    dest_path.parent.mkdir(parents=True, exist_ok=True)
    dest_path.write_text(content, encoding="utf-8")
    shutil.copystat(src_path, dest_path)


def process_template(
    manifest: TemplateManifest,
    output_dir: Path,
    substitutions: dict[str, str],
    dry_run: bool,
) -> list[Path]:
    """Render all files in a template into the destination directory."""
    rendered_files: list[Path] = []

    for src_path in sorted(manifest.files_dir.rglob("*")):
        if not src_path.is_file():
            continue

        relative_path = src_path.relative_to(manifest.files_dir)
        rendered_relative_path = render_relative_path(
            relative_path, substitutions
        )
        dest_path = output_dir / rendered_relative_path
        rendered_files.append(rendered_relative_path)
        copy_template_file(src_path, dest_path, substitutions, dry_run)

    return rendered_files


def initialize_git_repository(output_dir: Path) -> None:
    """Initialize a git repository in the generated project."""
    if shutil.which("git") is None:
        fail("git is not installed or is not available on PATH")

    try:
        subprocess.run(["git", "init"], cwd=output_dir, check=True)
    except subprocess.CalledProcessError as exc:
        fail(f"git init failed with exit code {exc.returncode}")


def create_parser(
    templates: dict[str, TemplateManifest],
) -> argparse.ArgumentParser:
    """Create the top-level argument parser."""
    parser = argparse.ArgumentParser(
        description="Create a new project from a reusable template",
    )
    parser.add_argument(
        "--name",
        "-n",
        help="Project display name (for example: My Library)",
    )
    parser.add_argument(
        "--slug",
        help=(
            "Project slug used for file names and C identifiers "
            "(default: derived from --name)"
        ),
    )
    parser.add_argument(
        "--version",
        "-v",
        help="Initial version in X.Y.Z format (for example: 1.0.0)",
    )
    parser.add_argument(
        "--description",
        "-d",
        help="Short project description",
    )
    parser.add_argument(
        "--author",
        default="Unknown Author",
        help="Copyright holder written into generated files",
    )
    parser.add_argument(
        "--year",
        type=int,
        default=date.today().year,
        help="Copyright year written into generated files",
    )
    parser.add_argument(
        "--template",
        default=DEFAULT_TEMPLATE,
        choices=sorted(templates.keys()),
        help="Template identifier to render",
    )
    parser.add_argument(
        "--output",
        "-o",
        type=Path,
        default=None,
        help="Output directory (default: current directory / project-slug)",
    )
    parser.add_argument(
        "--init-git",
        action="store_true",
        help="Initialize a git repository in the generated project",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Print the planned output without writing any files",
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="Allow writing into an existing empty output directory",
    )
    parser.add_argument(
        "--list-templates",
        action="store_true",
        help="List available templates and exit",
    )
    return parser


def parse_args(argv: Sequence[str] | None = None) -> argparse.Namespace:
    """Parse command line arguments."""
    templates = discover_templates()
    parser = create_parser(templates)
    args = parser.parse_args(argv)
    args.templates = templates
    return args


def main(argv: Sequence[str] | None = None) -> int:
    """Entry point."""
    args = parse_args(argv)

    if args.list_templates:
        print("Available templates:")
        for template_id, manifest in sorted(args.templates.items()):
            print(f"  {template_id}: {manifest.name}")
            if manifest.description:
                print(f"    {manifest.description}")
        return 0

    missing_args = [
        flag
        for flag, value in (
            ("--name", args.name),
            ("--version", args.version),
            ("--description", args.description),
        )
        if value is None
    ]
    if missing_args:
        fail(f"Missing required arguments: {', '.join(missing_args)}")

    if not VERSION_RE.fullmatch(args.version):
        fail("Version must be in format X.Y.Z (for example: 1.0.0)")

    if args.year < 1:
        fail("Year must be a positive integer")

    project_name = validate_project_name(args.name)
    project_slug = validate_slug(args.slug or normalize_slug(project_name))
    output_dir = (
        args.output.expanduser() if args.output else Path.cwd() / project_slug
    )

    ensure_output_directory(output_dir, args.force, args.dry_run)

    manifest = args.templates[args.template]
    substitutions = build_substitutions(args, project_name, project_slug)
    rendered_files = process_template(
        manifest=manifest,
        output_dir=output_dir,
        substitutions=substitutions,
        dry_run=args.dry_run,
    )

    if args.dry_run:
        print(f"Dry run for template {manifest.template_id!r}")
        print(f"  Project name: {project_name}")
        print(f"  Project slug: {project_slug}")
        print(f"  Output dir:   {output_dir}")
        print("  Files:")
        for rendered_file in rendered_files:
            print(f"    {rendered_file.as_posix()}")
        if args.init_git:
            print("  Note: git repository would be initialized")
        return 0

    if args.init_git:
        initialize_git_repository(output_dir)

    created_message = 'Created project "{}" from template "{}".'.format(
        project_name,
        manifest.template_id,
    )
    print(created_message)
    print(f"  Directory: {output_dir}")
    print("  Next steps:")
    print(f"    cd {output_dir}")
    print("    meson setup build --buildtype=debug -Dbuild_tests=true")
    print("    meson compile -C build")
    print("    meson test -C build --verbose")
    return 0
