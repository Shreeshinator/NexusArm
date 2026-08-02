// generated from rosidl_generator_c/resource/idl__functions.h.em
// with input from modular_arm_interfaces:srv/MoveTo.idl
// generated code does not contain a copyright notice

// IWYU pragma: private, include "modular_arm_interfaces/srv/move_to.h"


#ifndef MODULAR_ARM_INTERFACES__SRV__DETAIL__MOVE_TO__FUNCTIONS_H_
#define MODULAR_ARM_INTERFACES__SRV__DETAIL__MOVE_TO__FUNCTIONS_H_

#ifdef __cplusplus
extern "C"
{
#endif

#include <stdbool.h>
#include <stdlib.h>

#include "rosidl_runtime_c/action_type_support_struct.h"
#include "rosidl_runtime_c/message_type_support_struct.h"
#include "rosidl_runtime_c/service_type_support_struct.h"
#include "rosidl_runtime_c/type_description/type_description__struct.h"
#include "rosidl_runtime_c/type_description/type_source__struct.h"
#include "rosidl_runtime_c/type_hash.h"
#include "rosidl_runtime_c/visibility_control.h"
#include "modular_arm_interfaces/msg/rosidl_generator_c__visibility_control.h"

#include "modular_arm_interfaces/srv/detail/move_to__struct.h"

/// Retrieve pointer to the hash of the description of this type.
ROSIDL_GENERATOR_C_PUBLIC_modular_arm_interfaces
const rosidl_type_hash_t *
modular_arm_interfaces__srv__MoveTo__get_type_hash(
  const rosidl_service_type_support_t * type_support);

/// Retrieve pointer to the description of this type.
ROSIDL_GENERATOR_C_PUBLIC_modular_arm_interfaces
const rosidl_runtime_c__type_description__TypeDescription *
modular_arm_interfaces__srv__MoveTo__get_type_description(
  const rosidl_service_type_support_t * type_support);

/// Retrieve pointer to the single raw source text that defined this type.
ROSIDL_GENERATOR_C_PUBLIC_modular_arm_interfaces
const rosidl_runtime_c__type_description__TypeSource *
modular_arm_interfaces__srv__MoveTo__get_individual_type_description_source(
  const rosidl_service_type_support_t * type_support);

/// Retrieve pointer to the recursive raw sources that defined the description of this type.
ROSIDL_GENERATOR_C_PUBLIC_modular_arm_interfaces
const rosidl_runtime_c__type_description__TypeSource__Sequence *
modular_arm_interfaces__srv__MoveTo__get_type_description_sources(
  const rosidl_service_type_support_t * type_support);

/// Initialize srv/MoveTo message.
/**
 * If the init function is called twice for the same message without
 * calling fini inbetween previously allocated memory will be leaked.
 * \param[in,out] msg The previously allocated message pointer.
 * Fields without a default value will not be initialized by this function.
 * You might want to call memset(msg, 0, sizeof(
 * modular_arm_interfaces__srv__MoveTo_Request
 * )) before or use
 * modular_arm_interfaces__srv__MoveTo_Request__create()
 * to allocate and initialize the message.
 * \return true if initialization was successful, otherwise false
 */
ROSIDL_GENERATOR_C_PUBLIC_modular_arm_interfaces
bool
modular_arm_interfaces__srv__MoveTo_Request__init(modular_arm_interfaces__srv__MoveTo_Request * msg);

/// Finalize srv/MoveTo message.
/**
 * \param[in,out] msg The allocated message pointer.
 */
ROSIDL_GENERATOR_C_PUBLIC_modular_arm_interfaces
void
modular_arm_interfaces__srv__MoveTo_Request__fini(modular_arm_interfaces__srv__MoveTo_Request * msg);

/// Create srv/MoveTo message.
/**
 * It allocates the memory for the message, sets the memory to zero, and
 * calls
 * modular_arm_interfaces__srv__MoveTo_Request__init().
 * \return The pointer to the initialized message if successful,
 * otherwise NULL
 */
ROSIDL_GENERATOR_C_PUBLIC_modular_arm_interfaces
modular_arm_interfaces__srv__MoveTo_Request *
modular_arm_interfaces__srv__MoveTo_Request__create(void);

/// Destroy srv/MoveTo message.
/**
 * It calls
 * modular_arm_interfaces__srv__MoveTo_Request__fini()
 * and frees the memory of the message.
 * \param[in,out] msg The allocated message pointer.
 */
ROSIDL_GENERATOR_C_PUBLIC_modular_arm_interfaces
void
modular_arm_interfaces__srv__MoveTo_Request__destroy(modular_arm_interfaces__srv__MoveTo_Request * msg);

/// Check for srv/MoveTo message equality.
/**
 * \param[in] lhs The message on the left hand size of the equality operator.
 * \param[in] rhs The message on the right hand size of the equality operator.
 * \return true if messages are equal, otherwise false.
 */
ROSIDL_GENERATOR_C_PUBLIC_modular_arm_interfaces
bool
modular_arm_interfaces__srv__MoveTo_Request__are_equal(const modular_arm_interfaces__srv__MoveTo_Request * lhs, const modular_arm_interfaces__srv__MoveTo_Request * rhs);

/// Copy a srv/MoveTo message.
/**
 * This functions performs a deep copy, as opposed to the shallow copy that
 * plain assignment yields.
 *
 * \param[in] input The source message pointer.
 * \param[out] output The target message pointer, which must
 *   have been initialized before calling this function.
 * \return true if successful, or false if either pointer is null
 *   or memory allocation fails.
 */
ROSIDL_GENERATOR_C_PUBLIC_modular_arm_interfaces
bool
modular_arm_interfaces__srv__MoveTo_Request__copy(
  const modular_arm_interfaces__srv__MoveTo_Request * input,
  modular_arm_interfaces__srv__MoveTo_Request * output);

/// Retrieve pointer to the hash of the description of this type.
ROSIDL_GENERATOR_C_PUBLIC_modular_arm_interfaces
const rosidl_type_hash_t *
modular_arm_interfaces__srv__MoveTo_Request__get_type_hash(
  const rosidl_message_type_support_t * type_support);

/// Retrieve pointer to the description of this type.
ROSIDL_GENERATOR_C_PUBLIC_modular_arm_interfaces
const rosidl_runtime_c__type_description__TypeDescription *
modular_arm_interfaces__srv__MoveTo_Request__get_type_description(
  const rosidl_message_type_support_t * type_support);

/// Retrieve pointer to the single raw source text that defined this type.
ROSIDL_GENERATOR_C_PUBLIC_modular_arm_interfaces
const rosidl_runtime_c__type_description__TypeSource *
modular_arm_interfaces__srv__MoveTo_Request__get_individual_type_description_source(
  const rosidl_message_type_support_t * type_support);

/// Retrieve pointer to the recursive raw sources that defined the description of this type.
ROSIDL_GENERATOR_C_PUBLIC_modular_arm_interfaces
const rosidl_runtime_c__type_description__TypeSource__Sequence *
modular_arm_interfaces__srv__MoveTo_Request__get_type_description_sources(
  const rosidl_message_type_support_t * type_support);

/// Initialize array of srv/MoveTo messages.
/**
 * It allocates the memory for the number of elements and calls
 * modular_arm_interfaces__srv__MoveTo_Request__init()
 * for each element of the array.
 * \param[in,out] array The allocated array pointer.
 * \param[in] size The size / capacity of the array.
 * \return true if initialization was successful, otherwise false
 * If the array pointer is valid and the size is zero it is guaranteed
 # to return true.
 */
ROSIDL_GENERATOR_C_PUBLIC_modular_arm_interfaces
bool
modular_arm_interfaces__srv__MoveTo_Request__Sequence__init(modular_arm_interfaces__srv__MoveTo_Request__Sequence * array, size_t size);

/// Finalize array of srv/MoveTo messages.
/**
 * It calls
 * modular_arm_interfaces__srv__MoveTo_Request__fini()
 * for each element of the array and frees the memory for the number of
 * elements.
 * \param[in,out] array The initialized array pointer.
 */
ROSIDL_GENERATOR_C_PUBLIC_modular_arm_interfaces
void
modular_arm_interfaces__srv__MoveTo_Request__Sequence__fini(modular_arm_interfaces__srv__MoveTo_Request__Sequence * array);

/// Create array of srv/MoveTo messages.
/**
 * It allocates the memory for the array and calls
 * modular_arm_interfaces__srv__MoveTo_Request__Sequence__init().
 * \param[in] size The size / capacity of the array.
 * \return The pointer to the initialized array if successful, otherwise NULL
 */
ROSIDL_GENERATOR_C_PUBLIC_modular_arm_interfaces
modular_arm_interfaces__srv__MoveTo_Request__Sequence *
modular_arm_interfaces__srv__MoveTo_Request__Sequence__create(size_t size);

/// Destroy array of srv/MoveTo messages.
/**
 * It calls
 * modular_arm_interfaces__srv__MoveTo_Request__Sequence__fini()
 * on the array,
 * and frees the memory of the array.
 * \param[in,out] array The initialized array pointer.
 */
ROSIDL_GENERATOR_C_PUBLIC_modular_arm_interfaces
void
modular_arm_interfaces__srv__MoveTo_Request__Sequence__destroy(modular_arm_interfaces__srv__MoveTo_Request__Sequence * array);

/// Check for srv/MoveTo message array equality.
/**
 * \param[in] lhs The message array on the left hand size of the equality operator.
 * \param[in] rhs The message array on the right hand size of the equality operator.
 * \return true if message arrays are equal in size and content, otherwise false.
 */
ROSIDL_GENERATOR_C_PUBLIC_modular_arm_interfaces
bool
modular_arm_interfaces__srv__MoveTo_Request__Sequence__are_equal(const modular_arm_interfaces__srv__MoveTo_Request__Sequence * lhs, const modular_arm_interfaces__srv__MoveTo_Request__Sequence * rhs);

/// Copy an array of srv/MoveTo messages.
/**
 * This functions performs a deep copy, as opposed to the shallow copy that
 * plain assignment yields.
 *
 * \param[in] input The source array pointer.
 * \param[out] output The target array pointer, which must
 *   have been initialized before calling this function.
 * \return true if successful, or false if either pointer
 *   is null or memory allocation fails.
 */
ROSIDL_GENERATOR_C_PUBLIC_modular_arm_interfaces
bool
modular_arm_interfaces__srv__MoveTo_Request__Sequence__copy(
  const modular_arm_interfaces__srv__MoveTo_Request__Sequence * input,
  modular_arm_interfaces__srv__MoveTo_Request__Sequence * output);

/// Initialize srv/MoveTo message.
/**
 * If the init function is called twice for the same message without
 * calling fini inbetween previously allocated memory will be leaked.
 * \param[in,out] msg The previously allocated message pointer.
 * Fields without a default value will not be initialized by this function.
 * You might want to call memset(msg, 0, sizeof(
 * modular_arm_interfaces__srv__MoveTo_Response
 * )) before or use
 * modular_arm_interfaces__srv__MoveTo_Response__create()
 * to allocate and initialize the message.
 * \return true if initialization was successful, otherwise false
 */
ROSIDL_GENERATOR_C_PUBLIC_modular_arm_interfaces
bool
modular_arm_interfaces__srv__MoveTo_Response__init(modular_arm_interfaces__srv__MoveTo_Response * msg);

/// Finalize srv/MoveTo message.
/**
 * \param[in,out] msg The allocated message pointer.
 */
ROSIDL_GENERATOR_C_PUBLIC_modular_arm_interfaces
void
modular_arm_interfaces__srv__MoveTo_Response__fini(modular_arm_interfaces__srv__MoveTo_Response * msg);

/// Create srv/MoveTo message.
/**
 * It allocates the memory for the message, sets the memory to zero, and
 * calls
 * modular_arm_interfaces__srv__MoveTo_Response__init().
 * \return The pointer to the initialized message if successful,
 * otherwise NULL
 */
ROSIDL_GENERATOR_C_PUBLIC_modular_arm_interfaces
modular_arm_interfaces__srv__MoveTo_Response *
modular_arm_interfaces__srv__MoveTo_Response__create(void);

/// Destroy srv/MoveTo message.
/**
 * It calls
 * modular_arm_interfaces__srv__MoveTo_Response__fini()
 * and frees the memory of the message.
 * \param[in,out] msg The allocated message pointer.
 */
ROSIDL_GENERATOR_C_PUBLIC_modular_arm_interfaces
void
modular_arm_interfaces__srv__MoveTo_Response__destroy(modular_arm_interfaces__srv__MoveTo_Response * msg);

/// Check for srv/MoveTo message equality.
/**
 * \param[in] lhs The message on the left hand size of the equality operator.
 * \param[in] rhs The message on the right hand size of the equality operator.
 * \return true if messages are equal, otherwise false.
 */
ROSIDL_GENERATOR_C_PUBLIC_modular_arm_interfaces
bool
modular_arm_interfaces__srv__MoveTo_Response__are_equal(const modular_arm_interfaces__srv__MoveTo_Response * lhs, const modular_arm_interfaces__srv__MoveTo_Response * rhs);

/// Copy a srv/MoveTo message.
/**
 * This functions performs a deep copy, as opposed to the shallow copy that
 * plain assignment yields.
 *
 * \param[in] input The source message pointer.
 * \param[out] output The target message pointer, which must
 *   have been initialized before calling this function.
 * \return true if successful, or false if either pointer is null
 *   or memory allocation fails.
 */
ROSIDL_GENERATOR_C_PUBLIC_modular_arm_interfaces
bool
modular_arm_interfaces__srv__MoveTo_Response__copy(
  const modular_arm_interfaces__srv__MoveTo_Response * input,
  modular_arm_interfaces__srv__MoveTo_Response * output);

/// Retrieve pointer to the hash of the description of this type.
ROSIDL_GENERATOR_C_PUBLIC_modular_arm_interfaces
const rosidl_type_hash_t *
modular_arm_interfaces__srv__MoveTo_Response__get_type_hash(
  const rosidl_message_type_support_t * type_support);

/// Retrieve pointer to the description of this type.
ROSIDL_GENERATOR_C_PUBLIC_modular_arm_interfaces
const rosidl_runtime_c__type_description__TypeDescription *
modular_arm_interfaces__srv__MoveTo_Response__get_type_description(
  const rosidl_message_type_support_t * type_support);

/// Retrieve pointer to the single raw source text that defined this type.
ROSIDL_GENERATOR_C_PUBLIC_modular_arm_interfaces
const rosidl_runtime_c__type_description__TypeSource *
modular_arm_interfaces__srv__MoveTo_Response__get_individual_type_description_source(
  const rosidl_message_type_support_t * type_support);

/// Retrieve pointer to the recursive raw sources that defined the description of this type.
ROSIDL_GENERATOR_C_PUBLIC_modular_arm_interfaces
const rosidl_runtime_c__type_description__TypeSource__Sequence *
modular_arm_interfaces__srv__MoveTo_Response__get_type_description_sources(
  const rosidl_message_type_support_t * type_support);

/// Initialize array of srv/MoveTo messages.
/**
 * It allocates the memory for the number of elements and calls
 * modular_arm_interfaces__srv__MoveTo_Response__init()
 * for each element of the array.
 * \param[in,out] array The allocated array pointer.
 * \param[in] size The size / capacity of the array.
 * \return true if initialization was successful, otherwise false
 * If the array pointer is valid and the size is zero it is guaranteed
 # to return true.
 */
ROSIDL_GENERATOR_C_PUBLIC_modular_arm_interfaces
bool
modular_arm_interfaces__srv__MoveTo_Response__Sequence__init(modular_arm_interfaces__srv__MoveTo_Response__Sequence * array, size_t size);

/// Finalize array of srv/MoveTo messages.
/**
 * It calls
 * modular_arm_interfaces__srv__MoveTo_Response__fini()
 * for each element of the array and frees the memory for the number of
 * elements.
 * \param[in,out] array The initialized array pointer.
 */
ROSIDL_GENERATOR_C_PUBLIC_modular_arm_interfaces
void
modular_arm_interfaces__srv__MoveTo_Response__Sequence__fini(modular_arm_interfaces__srv__MoveTo_Response__Sequence * array);

/// Create array of srv/MoveTo messages.
/**
 * It allocates the memory for the array and calls
 * modular_arm_interfaces__srv__MoveTo_Response__Sequence__init().
 * \param[in] size The size / capacity of the array.
 * \return The pointer to the initialized array if successful, otherwise NULL
 */
ROSIDL_GENERATOR_C_PUBLIC_modular_arm_interfaces
modular_arm_interfaces__srv__MoveTo_Response__Sequence *
modular_arm_interfaces__srv__MoveTo_Response__Sequence__create(size_t size);

/// Destroy array of srv/MoveTo messages.
/**
 * It calls
 * modular_arm_interfaces__srv__MoveTo_Response__Sequence__fini()
 * on the array,
 * and frees the memory of the array.
 * \param[in,out] array The initialized array pointer.
 */
ROSIDL_GENERATOR_C_PUBLIC_modular_arm_interfaces
void
modular_arm_interfaces__srv__MoveTo_Response__Sequence__destroy(modular_arm_interfaces__srv__MoveTo_Response__Sequence * array);

/// Check for srv/MoveTo message array equality.
/**
 * \param[in] lhs The message array on the left hand size of the equality operator.
 * \param[in] rhs The message array on the right hand size of the equality operator.
 * \return true if message arrays are equal in size and content, otherwise false.
 */
ROSIDL_GENERATOR_C_PUBLIC_modular_arm_interfaces
bool
modular_arm_interfaces__srv__MoveTo_Response__Sequence__are_equal(const modular_arm_interfaces__srv__MoveTo_Response__Sequence * lhs, const modular_arm_interfaces__srv__MoveTo_Response__Sequence * rhs);

/// Copy an array of srv/MoveTo messages.
/**
 * This functions performs a deep copy, as opposed to the shallow copy that
 * plain assignment yields.
 *
 * \param[in] input The source array pointer.
 * \param[out] output The target array pointer, which must
 *   have been initialized before calling this function.
 * \return true if successful, or false if either pointer
 *   is null or memory allocation fails.
 */
ROSIDL_GENERATOR_C_PUBLIC_modular_arm_interfaces
bool
modular_arm_interfaces__srv__MoveTo_Response__Sequence__copy(
  const modular_arm_interfaces__srv__MoveTo_Response__Sequence * input,
  modular_arm_interfaces__srv__MoveTo_Response__Sequence * output);

/// Initialize srv/MoveTo message.
/**
 * If the init function is called twice for the same message without
 * calling fini inbetween previously allocated memory will be leaked.
 * \param[in,out] msg The previously allocated message pointer.
 * Fields without a default value will not be initialized by this function.
 * You might want to call memset(msg, 0, sizeof(
 * modular_arm_interfaces__srv__MoveTo_Event
 * )) before or use
 * modular_arm_interfaces__srv__MoveTo_Event__create()
 * to allocate and initialize the message.
 * \return true if initialization was successful, otherwise false
 */
ROSIDL_GENERATOR_C_PUBLIC_modular_arm_interfaces
bool
modular_arm_interfaces__srv__MoveTo_Event__init(modular_arm_interfaces__srv__MoveTo_Event * msg);

/// Finalize srv/MoveTo message.
/**
 * \param[in,out] msg The allocated message pointer.
 */
ROSIDL_GENERATOR_C_PUBLIC_modular_arm_interfaces
void
modular_arm_interfaces__srv__MoveTo_Event__fini(modular_arm_interfaces__srv__MoveTo_Event * msg);

/// Create srv/MoveTo message.
/**
 * It allocates the memory for the message, sets the memory to zero, and
 * calls
 * modular_arm_interfaces__srv__MoveTo_Event__init().
 * \return The pointer to the initialized message if successful,
 * otherwise NULL
 */
ROSIDL_GENERATOR_C_PUBLIC_modular_arm_interfaces
modular_arm_interfaces__srv__MoveTo_Event *
modular_arm_interfaces__srv__MoveTo_Event__create(void);

/// Destroy srv/MoveTo message.
/**
 * It calls
 * modular_arm_interfaces__srv__MoveTo_Event__fini()
 * and frees the memory of the message.
 * \param[in,out] msg The allocated message pointer.
 */
ROSIDL_GENERATOR_C_PUBLIC_modular_arm_interfaces
void
modular_arm_interfaces__srv__MoveTo_Event__destroy(modular_arm_interfaces__srv__MoveTo_Event * msg);

/// Check for srv/MoveTo message equality.
/**
 * \param[in] lhs The message on the left hand size of the equality operator.
 * \param[in] rhs The message on the right hand size of the equality operator.
 * \return true if messages are equal, otherwise false.
 */
ROSIDL_GENERATOR_C_PUBLIC_modular_arm_interfaces
bool
modular_arm_interfaces__srv__MoveTo_Event__are_equal(const modular_arm_interfaces__srv__MoveTo_Event * lhs, const modular_arm_interfaces__srv__MoveTo_Event * rhs);

/// Copy a srv/MoveTo message.
/**
 * This functions performs a deep copy, as opposed to the shallow copy that
 * plain assignment yields.
 *
 * \param[in] input The source message pointer.
 * \param[out] output The target message pointer, which must
 *   have been initialized before calling this function.
 * \return true if successful, or false if either pointer is null
 *   or memory allocation fails.
 */
ROSIDL_GENERATOR_C_PUBLIC_modular_arm_interfaces
bool
modular_arm_interfaces__srv__MoveTo_Event__copy(
  const modular_arm_interfaces__srv__MoveTo_Event * input,
  modular_arm_interfaces__srv__MoveTo_Event * output);

/// Retrieve pointer to the hash of the description of this type.
ROSIDL_GENERATOR_C_PUBLIC_modular_arm_interfaces
const rosidl_type_hash_t *
modular_arm_interfaces__srv__MoveTo_Event__get_type_hash(
  const rosidl_message_type_support_t * type_support);

/// Retrieve pointer to the description of this type.
ROSIDL_GENERATOR_C_PUBLIC_modular_arm_interfaces
const rosidl_runtime_c__type_description__TypeDescription *
modular_arm_interfaces__srv__MoveTo_Event__get_type_description(
  const rosidl_message_type_support_t * type_support);

/// Retrieve pointer to the single raw source text that defined this type.
ROSIDL_GENERATOR_C_PUBLIC_modular_arm_interfaces
const rosidl_runtime_c__type_description__TypeSource *
modular_arm_interfaces__srv__MoveTo_Event__get_individual_type_description_source(
  const rosidl_message_type_support_t * type_support);

/// Retrieve pointer to the recursive raw sources that defined the description of this type.
ROSIDL_GENERATOR_C_PUBLIC_modular_arm_interfaces
const rosidl_runtime_c__type_description__TypeSource__Sequence *
modular_arm_interfaces__srv__MoveTo_Event__get_type_description_sources(
  const rosidl_message_type_support_t * type_support);

/// Initialize array of srv/MoveTo messages.
/**
 * It allocates the memory for the number of elements and calls
 * modular_arm_interfaces__srv__MoveTo_Event__init()
 * for each element of the array.
 * \param[in,out] array The allocated array pointer.
 * \param[in] size The size / capacity of the array.
 * \return true if initialization was successful, otherwise false
 * If the array pointer is valid and the size is zero it is guaranteed
 # to return true.
 */
ROSIDL_GENERATOR_C_PUBLIC_modular_arm_interfaces
bool
modular_arm_interfaces__srv__MoveTo_Event__Sequence__init(modular_arm_interfaces__srv__MoveTo_Event__Sequence * array, size_t size);

/// Finalize array of srv/MoveTo messages.
/**
 * It calls
 * modular_arm_interfaces__srv__MoveTo_Event__fini()
 * for each element of the array and frees the memory for the number of
 * elements.
 * \param[in,out] array The initialized array pointer.
 */
ROSIDL_GENERATOR_C_PUBLIC_modular_arm_interfaces
void
modular_arm_interfaces__srv__MoveTo_Event__Sequence__fini(modular_arm_interfaces__srv__MoveTo_Event__Sequence * array);

/// Create array of srv/MoveTo messages.
/**
 * It allocates the memory for the array and calls
 * modular_arm_interfaces__srv__MoveTo_Event__Sequence__init().
 * \param[in] size The size / capacity of the array.
 * \return The pointer to the initialized array if successful, otherwise NULL
 */
ROSIDL_GENERATOR_C_PUBLIC_modular_arm_interfaces
modular_arm_interfaces__srv__MoveTo_Event__Sequence *
modular_arm_interfaces__srv__MoveTo_Event__Sequence__create(size_t size);

/// Destroy array of srv/MoveTo messages.
/**
 * It calls
 * modular_arm_interfaces__srv__MoveTo_Event__Sequence__fini()
 * on the array,
 * and frees the memory of the array.
 * \param[in,out] array The initialized array pointer.
 */
ROSIDL_GENERATOR_C_PUBLIC_modular_arm_interfaces
void
modular_arm_interfaces__srv__MoveTo_Event__Sequence__destroy(modular_arm_interfaces__srv__MoveTo_Event__Sequence * array);

/// Check for srv/MoveTo message array equality.
/**
 * \param[in] lhs The message array on the left hand size of the equality operator.
 * \param[in] rhs The message array on the right hand size of the equality operator.
 * \return true if message arrays are equal in size and content, otherwise false.
 */
ROSIDL_GENERATOR_C_PUBLIC_modular_arm_interfaces
bool
modular_arm_interfaces__srv__MoveTo_Event__Sequence__are_equal(const modular_arm_interfaces__srv__MoveTo_Event__Sequence * lhs, const modular_arm_interfaces__srv__MoveTo_Event__Sequence * rhs);

/// Copy an array of srv/MoveTo messages.
/**
 * This functions performs a deep copy, as opposed to the shallow copy that
 * plain assignment yields.
 *
 * \param[in] input The source array pointer.
 * \param[out] output The target array pointer, which must
 *   have been initialized before calling this function.
 * \return true if successful, or false if either pointer
 *   is null or memory allocation fails.
 */
ROSIDL_GENERATOR_C_PUBLIC_modular_arm_interfaces
bool
modular_arm_interfaces__srv__MoveTo_Event__Sequence__copy(
  const modular_arm_interfaces__srv__MoveTo_Event__Sequence * input,
  modular_arm_interfaces__srv__MoveTo_Event__Sequence * output);
#ifdef __cplusplus
}
#endif

#endif  // MODULAR_ARM_INTERFACES__SRV__DETAIL__MOVE_TO__FUNCTIONS_H_
