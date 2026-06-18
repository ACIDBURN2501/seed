/**
 * SPDX-License-Identifier: MIT
 *
 * @file {{PROJECT_SLUG}}_conf.h
 * @brief Public configuration header for {{PROJECT_NAME}}.
 *
 * @details
 *    This header provides configuration options for the {{PROJECT_SLUG}} module.
 *    It is included automatically by {{PROJECT_SLUG}}.h, but applications may
 *    also include it directly before {{PROJECT_SLUG}}.h to keep configuration in
 *    one place. Default values are provided if not overridden.
 *
 * @note
 *    Override any configuration option by defining it before including
 *    this file. Example:
 *    @code
 *    #define {{PROJECT_UPPER}}_MAX 1000000.0f
 *    #include "{{PROJECT_SLUG}}_conf.h"
 *    #include "{{PROJECT_SLUG}}.h"
 *    @endcode
 *
 */
#ifndef __PROJECT_UPPER___CONF_H_
#define __PROJECT_UPPER___CONF_H_

/* ================ CONFIGURATION =========================================== */

/* ---------------- Example Configuration ----------------------------------- */

#ifndef __PROJECT_UPPER___MAX
/**
 * @def {{PROJECT_UPPER}}_MAX
 * @brief Maximum value for {{PROJECT_NAME}} operations.
 *
 * @details
 *    This defines the maximum value that can be processed by {{PROJECT_NAME}}.
 *    Adjust this based on your application requirements.
 *
 * @note
 *    The default value of 1000000 is suitable for most applications.
 *    Override this value before including this header if needed.
 */
#define __PROJECT_UPPER___MAX (1000000)
#endif

#ifndef __PROJECT_UPPER___MIN
/**
 * @def {{PROJECT_UPPER}}_MIN
 * @brief Minimum value for {{PROJECT_NAME}} operations.
 *
 * @details
 *    This defines the minimum value that can be processed by {{PROJECT_NAME}}.
 *
 * @note
 *    The default value of -1000000 complements the maximum value.
 */
#define __PROJECT_UPPER___MIN (-1000000)
#endif

#endif /* __PROJECT_UPPER___CONF_H_ */