/*
 * @file test_{{PROJECT_SLUG}}.c
 * @brief Unit tests for {{PROJECT_NAME}}.
 */

#include "__PROJECT_SLUG__.h"
#include <stdio.h>
#include <stdlib.h>

#define TEST_ASSERT(expr)                                                      \
        do {                                                                   \
                if (!(expr)) {                                                 \
                        fprintf(stderr, "FAIL  %s:%d  %s\n", __FILE__,       \
                                __LINE__, #expr);                              \
                        exit(EXIT_FAILURE);                                    \
                }                                                              \
        } while (0)

#define TEST_PASS(name) fprintf(stdout, "PASS  %s\n", (name))

#define TEST_CASE(name)                                                        \
        static void name(void);                                                \
        static void name(void)

TEST_CASE(test_example)
{
        TEST_ASSERT(1 == 1);
}

static void
run_test(void (*test_func)(void), const char *name)
{
        test_func();
        TEST_PASS(name);
}

int
main(void)
{
        fprintf(stdout, "\n=== Running {{PROJECT_SLUG}} unit tests ===\n\n");

        run_test(test_example, "test_example");

        fprintf(stdout, "\n=== All tests passed ===\n\n");
        return EXIT_SUCCESS;
}
