# {{PROJECT_NAME}}

{{DESCRIPTION}}

## Features

_Add a short list of the projects feature here_

- **<Topic>**: <description>

## Using the Library

### As a Meson subproject

```meson
{{PROJECT_SLUG}}_dep = dependency('{{PROJECT_SLUG}}', fallback: ['{{PROJECT_SLUG}}', '{{PROJECT_SLUG}}_dep'])
```

The template also exports `meson.override_dependency('{{PROJECT_SLUG}}', ...)`
so downstream Meson builds can resolve the subproject dependency by name.

For subproject builds, include the public header directly:

```c
#include "{{PROJECT_SLUG}}.h"
```

### As an installed dependency

If the library is installed system-wide, include the namespaced header path:

```c
#include <{{PROJECT_SLUG}}/{{PROJECT_SLUG}}.h>
```

If `pkg-config` files are installed in your environment, downstream builds can
also discover the package as `{{PROJECT_SLUG}}`.

The generated version header is available as `{{PROJECT_SLUG}}_version.h` in the
build tree and as `<{{PROJECT_SLUG}}/{{PROJECT_SLUG}}_version.h>` after install.

## Building

```sh
# Library only (release)
meson setup build --buildtype=release -Dbuild_tests=false
meson compile -C build

# With unit tests
meson setup build --buildtype=debug -Dbuild_tests=true
meson compile -C build
meson test -C build --verbose
```

## Quick Start

_Add a code snippet for a quick start use for the project_

## API Reference

_Add the API reference here_

## Use Cases

_Add a small list of use case examples_

- **<Topic>**: <description>

## Notes

| Topic | Note |
|-------|------|
| **<Topic>** | <description> |

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for build, style, and test
conventions. Security concerns should be reported privately as described in
[SECURITY.md](.github/SECURITY.md).

## License

Released under the MIT License. See [LICENSE](LICENSE) for the full text.
