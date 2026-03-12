project(
  '{{PROJECT_SLUG}}',
  'c',
  version: '{{VERSION}}',
  default_options: [
    'c_std=c11',
    'warning_level=3',
  ],
  license: 'MIT',
)

project_description = '{{DESCRIPTION}}'

ver = meson.project_version().split('.')
major = ver[0].to_int()
minor = ver[1].to_int()
patch = ver[2].to_int()

conf = configuration_data()
conf.set_quoted('VERSION', meson.project_version())
conf.set('MAJOR', major)
conf.set('MINOR', minor)
conf.set('PATCH', patch)

generated_version_header = configure_file(
  input: 'config' / '{{PROJECT_SLUG}}_version.h.in',
  output: '{{PROJECT_SLUG}}_version.h',
  configuration: conf,
  install: true,
  install_dir: get_option('includedir') / '{{PROJECT_SLUG}}',
)

public_headers = include_directories('include')
generated_headers = include_directories('.')

library_sources = files('src/{{PROJECT_SLUG}}.c')

__PROJECT_SLUG___lib = static_library(
  '{{PROJECT_SLUG}}',
  library_sources,
  include_directories: [public_headers, generated_headers],
  install: true,
)

install_headers('include/{{PROJECT_SLUG}}.h', subdir: '{{PROJECT_SLUG}}')

__PROJECT_SLUG___dep = declare_dependency(
  include_directories: [public_headers, generated_headers],
  link_with: __PROJECT_SLUG___lib,
  sources: generated_version_header,
)

meson.override_dependency('{{PROJECT_SLUG}}', __PROJECT_SLUG___dep)

pkg = import('pkgconfig')
pkg.generate(
  __PROJECT_SLUG___lib,
  description: project_description,
  filebase: '{{PROJECT_SLUG}}',
  name: '{{PROJECT_NAME}}',
  subdirs: '{{PROJECT_SLUG}}',
)

if get_option('build_tests')
  subdir('tests')
endif
