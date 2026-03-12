test_exe = executable(
  'test_{{PROJECT_SLUG}}',
  files('test_{{PROJECT_SLUG}}.c'),
  dependencies: [__PROJECT_SLUG___dep],
  include_directories: [public_headers, generated_headers],
)

test('{{PROJECT_SLUG}} module', test_exe)
