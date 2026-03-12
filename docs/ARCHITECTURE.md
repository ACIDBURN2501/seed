# Architecture

This document explains how `seed-scaffold` is structured today, how project generation
works, and how to add a new template safely.

## Goals

- Keep the scaffolder small and easy to reason about
- Make templates mostly data-driven
- Avoid template-specific rename logic in Python
- Ensure every built-in template can be validated end-to-end

## Current Scope

- Ships with one built-in template: `meson-c-lib`
- Generates a Meson-based C11 static library project
- Includes unit test scaffolding, CI, formatting config, and a license file
- Discovers templates from package manifests in
  `src/seed_scaffold/templates/*/template.json`

## Generation Flow

The packaged CLI in `src/seed_scaffold/cli.py` follows this sequence:

1. Discover templates from `src/seed_scaffold/templates/*/template.json`
2. Parse command-line arguments
3. Validate required metadata such as name, slug, and version
4. Build a placeholder substitution map
5. Render every file from the chosen template's `files/` directory
6. Optionally run `git init` in the generated output directory

Use the tool through one of these entry points:

- installed CLI: `seed-scaffold ...`
- source checkout: `python -m seed_scaffold ...`

The renderer applies substitutions to:

- file contents
- file names
- directory names

This is why template files can use names like `__PROJECT_SLUG__.h`.

## Template Contract

Each template lives in its own directory:

```text
src/
  seed_scaffold/
    templates/
      <template-id>/
        template.json
        files/
          ...rendered project files...
```

### `template.json`

Current manifest fields:

- `id` unique template identifier used by `--template`
- `name` human-readable template name
- `description` short template summary shown by `--list-templates`
- `files_dir` relative path containing renderable files, usually `files`

Example:

```json
{
  "id": "meson-c-lib",
  "name": "Meson C Library",
  "description": "Meson-based C11 static library with tests and CI.",
  "files_dir": "files"
}
```

## Supported Placeholders

These placeholders are available in both file paths and file contents:

- `{{PROJECT_NAME}}`
- `{{PROJECT_SLUG}}`
- `{{PROJECT_LOWER}}`
- `{{PROJECT_UPPER}}`
- `{{VERSION}}`
- `{{VERSION_MAJOR}}`
- `{{VERSION_MINOR}}`
- `{{VERSION_PATCH}}`
- `{{DESCRIPTION}}`
- `{{AUTHOR}}`
- `{{YEAR}}`

Path-safe placeholders also exist for identifiers inside filenames or code:

- `__PROJECT_NAME__`
- `__PROJECT_SLUG__`
- `__PROJECT_UPPER__`

The double-underscore forms are especially useful when raw template files would
otherwise confuse editors or linters.

## Adding a New Template

Use this process:

1. Create `src/seed_scaffold/templates/<new-template-id>/`
2. Add `template.json`
3. Add a `files/` tree with placeholder-based filenames and contents
4. Add or update tests that validate the template renders correctly
5. If the generated project has a native build or test system, add an end-to-end
   smoke test that exercises it
6. Update `README.md` if the new template changes public scope

## Template Design Guidelines

- Prefer placeholders over post-processing logic
- Keep template assumptions explicit in template docs
- Include enough files for a user to build the generated project immediately
- Avoid stale repository-specific placeholders such as fixed GitHub URLs unless
  they are parameterized
- Keep generated docs honest and minimal

## Testing Strategy

The current test suite validates:

- template discovery
- CLI argument validation
- output directory safety rules
- placeholder replacement
- optional git initialization
- end-to-end generation and Meson build/test for the built-in template

When adding a new template, the minimum acceptable validation is:

- one test that confirms expected files are rendered
- one test that checks key placeholders were replaced
- one smoke test for configure/build/test if the template has a build system

Repository validation commands:

```sh
black --check .
flake8 .
python3 -m unittest discover -s tests -v
python3 -m build
```

## Current Constraints

- Manifests are intentionally simple and do not yet support per-template custom
  prompts, conditional files, or interactive questions
- Template-specific validation beyond generic rendering still lives in tests,
  not in the manifest format

## Future Extension Points

Likely next improvements:

- richer manifest schema for template-specific options
- multiple built-in templates across languages/build systems
- generated project metadata for repository URLs and badges

## Roadmap

- Add more templates beyond Meson/C
- Expand template manifests with richer metadata and options
- Add project metadata inputs for generated repository URLs and badges
- Publish the package to PyPI once the release process is in place
