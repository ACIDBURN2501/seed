# {{PROJECT_NAME}}

{{DESCRIPTION}}

## Features

- Meson-based C11 static library template
- Optional unit test scaffold
- Generated version header
- `pkg-config` metadata generation
- GitHub Actions CI workflow
- `.clang-format` and MIT license included

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

## Layout

- `include/` public headers
- `src/` library sources
- `tests/` unit tests
- `config/` generated header templates

## Next Steps

- Flesh out the public API in `include/{{PROJECT_SLUG}}.h`
- Implement library behavior in `src/{{PROJECT_SLUG}}.c`
- Replace the example unit test with real test coverage
