# seed-scaffold

Reusable project scaffolding for small, opinionated starter templates.

## Features

- Placeholder substitution in both file contents and file paths
- Template selection with `--template`
- Safe output handling with `--dry-run` and `--force`
- Metadata injection for author and copyright year
- Optional git repository initialization
- End-to-end tests that validate generated projects build with Meson

## Installation

### From PyPI or pipx

Once the package has been published, install it with:

```sh
pip install seed-scaffold
# or
pipx install seed-scaffold
```

This installs the CLI entry point `seed-scaffold`.

### From a source checkout

```sh
git clone <your-repo-url> seed-scaffold
cd seed-scaffold
python3 -m pip install -e .
python3 -m seed_scaffold --list-templates
```

Validation and generated-project smoke tests expect these tools to be available:

- `python3`
- `meson`
- `ninja`
- a C compiler such as `cc`

For development tooling, install the package with dev extras:

```sh
python3 -m pip install -e .[dev]
```

## Usage

List available templates:

```sh
seed-scaffold --list-templates
```

Generate a new project:

```sh
seed-scaffold \
    --template meson-c-lib \
    --name "My Library" \
    --version 1.0.0 \
    --description "A small Meson-based C library" \
    --author "Jane Developer" \
    --init-git
```

Preview output without writing files:

```sh
seed-scaffold \
    --template meson-c-lib \
    --name "Preview Library" \
    --version 0.1.0 \
    --description "Dry-run example" \
    --dry-run
```

## Arguments

| Argument | Short | Required | Description |
|---|---|---|---|
| `--name` | `-n` | Yes* | Human-friendly project name |
| `--slug` |  | No | Filesystem/API slug; defaults to a sanitized form of `--name` |
| `--version` | `-v` | Yes* | Initial version in `X.Y.Z` format |
| `--description` | `-d` | Yes* | Short project description |
| `--author` |  | No | Copyright holder for generated files |
| `--year` |  | No | Copyright year (default: current year) |
| `--template` |  | No | Template ID to render (default: `meson-c-lib`) |
| `--output` | `-o` | No | Output directory (default: current directory / project slug) |
| `--init-git` |  | No | Run `git init` in the generated project |
| `--dry-run` |  | No | Print planned output without writing files |
| `--force` |  | No | Allow writing into an existing empty output directory |
| `--list-templates` |  | No | List available templates and exit |

`*` Not required when using `--list-templates`.

## Adding templates

See [`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md) for adding templates, maintainer information, validation details, current scope, and roadmap notes.
