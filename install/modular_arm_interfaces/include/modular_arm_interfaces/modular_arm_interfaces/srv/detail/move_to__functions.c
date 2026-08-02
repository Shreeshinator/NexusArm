// generated from rosidl_generator_c/resource/idl__functions.c.em
// with input from modular_arm_interfaces:srv/MoveTo.idl
// generated code does not contain a copyright notice
#include "modular_arm_interfaces/srv/detail/move_to__functions.h"

#include <assert.h>
#include <stdbool.h>
#include <stdlib.h>
#include <string.h>

#include "rcutils/allocator.h"

// Include directives for member types
// Member `elbow`
#include "rosidl_runtime_c/string_functions.h"

bool
modular_arm_interfaces__srv__MoveTo_Request__init(modular_arm_interfaces__srv__MoveTo_Request * msg)
{
  if (!msg) {
    return false;
  }
  // x
  // y
  // z
  // pitch
  // elbow
  if (!rosidl_runtime_c__String__init(&msg->elbow)) {
    modular_arm_interfaces__srv__MoveTo_Request__fini(msg);
    return false;
  }
  // duration_sec
  return true;
}

void
modular_arm_interfaces__srv__MoveTo_Request__fini(modular_arm_interfaces__srv__MoveTo_Request * msg)
{
  if (!msg) {
    return;
  }
  // x
  // y
  // z
  // pitch
  // elbow
  rosidl_runtime_c__String__fini(&msg->elbow);
  // duration_sec
}

bool
modular_arm_interfaces__srv__MoveTo_Request__are_equal(const modular_arm_interfaces__srv__MoveTo_Request * lhs, const modular_arm_interfaces__srv__MoveTo_Request * rhs)
{
  if (!lhs || !rhs) {
    return false;
  }
  // x
  if (lhs->x != rhs->x) {
    return false;
  }
  // y
  if (lhs->y != rhs->y) {
    return false;
  }
  // z
  if (lhs->z != rhs->z) {
    return false;
  }
  // pitch
  if (lhs->pitch != rhs->pitch) {
    return false;
  }
  // elbow
  if (!rosidl_runtime_c__String__are_equal(
      &(lhs->elbow), &(rhs->elbow)))
  {
    return false;
  }
  // duration_sec
  if (lhs->duration_sec != rhs->duration_sec) {
    return false;
  }
  return true;
}

bool
modular_arm_interfaces__srv__MoveTo_Request__copy(
  const modular_arm_interfaces__srv__MoveTo_Request * input,
  modular_arm_interfaces__srv__MoveTo_Request * output)
{
  if (!input || !output) {
    return false;
  }
  // x
  output->x = input->x;
  // y
  output->y = input->y;
  // z
  output->z = input->z;
  // pitch
  output->pitch = input->pitch;
  // elbow
  if (!rosidl_runtime_c__String__copy(
      &(input->elbow), &(output->elbow)))
  {
    return false;
  }
  // duration_sec
  output->duration_sec = input->duration_sec;
  return true;
}

modular_arm_interfaces__srv__MoveTo_Request *
modular_arm_interfaces__srv__MoveTo_Request__create(void)
{
  rcutils_allocator_t allocator = rcutils_get_default_allocator();
  modular_arm_interfaces__srv__MoveTo_Request * msg = (modular_arm_interfaces__srv__MoveTo_Request *)allocator.allocate(sizeof(modular_arm_interfaces__srv__MoveTo_Request), allocator.state);
  if (!msg) {
    return NULL;
  }
  memset(msg, 0, sizeof(modular_arm_interfaces__srv__MoveTo_Request));
  bool success = modular_arm_interfaces__srv__MoveTo_Request__init(msg);
  if (!success) {
    allocator.deallocate(msg, allocator.state);
    return NULL;
  }
  return msg;
}

void
modular_arm_interfaces__srv__MoveTo_Request__destroy(modular_arm_interfaces__srv__MoveTo_Request * msg)
{
  rcutils_allocator_t allocator = rcutils_get_default_allocator();
  if (msg) {
    modular_arm_interfaces__srv__MoveTo_Request__fini(msg);
  }
  allocator.deallocate(msg, allocator.state);
}


bool
modular_arm_interfaces__srv__MoveTo_Request__Sequence__init(modular_arm_interfaces__srv__MoveTo_Request__Sequence * array, size_t size)
{
  if (!array) {
    return false;
  }
  rcutils_allocator_t allocator = rcutils_get_default_allocator();
  modular_arm_interfaces__srv__MoveTo_Request * data = NULL;

  if (size) {
    if (size > SIZE_MAX / sizeof(modular_arm_interfaces__srv__MoveTo_Request)) {
      return false;
    }
    data = (modular_arm_interfaces__srv__MoveTo_Request *)allocator.zero_allocate(size, sizeof(modular_arm_interfaces__srv__MoveTo_Request), allocator.state);
    if (!data) {
      return false;
    }
    // initialize all array elements
    size_t i;
    for (i = 0; i < size; ++i) {
      bool success = modular_arm_interfaces__srv__MoveTo_Request__init(&data[i]);
      if (!success) {
        break;
      }
    }
    if (i < size) {
      // if initialization failed finalize the already initialized array elements
      for (; i > 0; --i) {
        modular_arm_interfaces__srv__MoveTo_Request__fini(&data[i - 1]);
      }
      allocator.deallocate(data, allocator.state);
      return false;
    }
  }
  array->data = data;
  array->size = size;
  array->capacity = size;
  return true;
}

void
modular_arm_interfaces__srv__MoveTo_Request__Sequence__fini(modular_arm_interfaces__srv__MoveTo_Request__Sequence * array)
{
  if (!array) {
    return;
  }
  rcutils_allocator_t allocator = rcutils_get_default_allocator();

  if (array->data) {
    // ensure that data and capacity values are consistent
    assert(array->capacity > 0);
    // finalize all array elements
    for (size_t i = 0; i < array->capacity; ++i) {
      modular_arm_interfaces__srv__MoveTo_Request__fini(&array->data[i]);
    }
    allocator.deallocate(array->data, allocator.state);
    array->data = NULL;
    array->size = 0;
    array->capacity = 0;
  } else {
    // ensure that data, size, and capacity values are consistent
    assert(0 == array->size);
    assert(0 == array->capacity);
  }
}

modular_arm_interfaces__srv__MoveTo_Request__Sequence *
modular_arm_interfaces__srv__MoveTo_Request__Sequence__create(size_t size)
{
  rcutils_allocator_t allocator = rcutils_get_default_allocator();
  modular_arm_interfaces__srv__MoveTo_Request__Sequence * array = (modular_arm_interfaces__srv__MoveTo_Request__Sequence *)allocator.allocate(sizeof(modular_arm_interfaces__srv__MoveTo_Request__Sequence), allocator.state);
  if (!array) {
    return NULL;
  }
  bool success = modular_arm_interfaces__srv__MoveTo_Request__Sequence__init(array, size);
  if (!success) {
    allocator.deallocate(array, allocator.state);
    return NULL;
  }
  return array;
}

void
modular_arm_interfaces__srv__MoveTo_Request__Sequence__destroy(modular_arm_interfaces__srv__MoveTo_Request__Sequence * array)
{
  rcutils_allocator_t allocator = rcutils_get_default_allocator();
  if (array) {
    modular_arm_interfaces__srv__MoveTo_Request__Sequence__fini(array);
  }
  allocator.deallocate(array, allocator.state);
}

bool
modular_arm_interfaces__srv__MoveTo_Request__Sequence__are_equal(const modular_arm_interfaces__srv__MoveTo_Request__Sequence * lhs, const modular_arm_interfaces__srv__MoveTo_Request__Sequence * rhs)
{
  if (!lhs || !rhs) {
    return false;
  }
  if (lhs->size != rhs->size) {
    return false;
  }
  for (size_t i = 0; i < lhs->size; ++i) {
    if (!modular_arm_interfaces__srv__MoveTo_Request__are_equal(&(lhs->data[i]), &(rhs->data[i]))) {
      return false;
    }
  }
  return true;
}

bool
modular_arm_interfaces__srv__MoveTo_Request__Sequence__copy(
  const modular_arm_interfaces__srv__MoveTo_Request__Sequence * input,
  modular_arm_interfaces__srv__MoveTo_Request__Sequence * output)
{
  if (!input || !output) {
    return false;
  }
  if (output->capacity < input->size) {
    if (input->size > SIZE_MAX / sizeof(modular_arm_interfaces__srv__MoveTo_Request)) {
      return false;
    }
    const size_t allocation_size =
      input->size * sizeof(modular_arm_interfaces__srv__MoveTo_Request);
    rcutils_allocator_t allocator = rcutils_get_default_allocator();
    modular_arm_interfaces__srv__MoveTo_Request * data =
      (modular_arm_interfaces__srv__MoveTo_Request *)allocator.reallocate(
      output->data, allocation_size, allocator.state);
    if (!data) {
      return false;
    }
    // If reallocation succeeded, memory may or may not have been moved
    // to fulfill the allocation request, invalidating output->data.
    output->data = data;
    for (size_t i = output->capacity; i < input->size; ++i) {
      if (!modular_arm_interfaces__srv__MoveTo_Request__init(&output->data[i])) {
        // If initialization of any new item fails, roll back
        // all previously initialized items. Existing items
        // in output are to be left unmodified.
        for (; i-- > output->capacity; ) {
          modular_arm_interfaces__srv__MoveTo_Request__fini(&output->data[i]);
        }
        return false;
      }
    }
    output->capacity = input->size;
  }
  output->size = input->size;
  for (size_t i = 0; i < input->size; ++i) {
    if (!modular_arm_interfaces__srv__MoveTo_Request__copy(
        &(input->data[i]), &(output->data[i])))
    {
      return false;
    }
  }
  return true;
}


// Include directives for member types
// Member `message`
// already included above
// #include "rosidl_runtime_c/string_functions.h"
// Member `joint_angles`
#include "rosidl_runtime_c/primitives_sequence_functions.h"

bool
modular_arm_interfaces__srv__MoveTo_Response__init(modular_arm_interfaces__srv__MoveTo_Response * msg)
{
  if (!msg) {
    return false;
  }
  // success
  // message
  if (!rosidl_runtime_c__String__init(&msg->message)) {
    modular_arm_interfaces__srv__MoveTo_Response__fini(msg);
    return false;
  }
  // joint_angles
  if (!rosidl_runtime_c__double__Sequence__init(&msg->joint_angles, 0)) {
    modular_arm_interfaces__srv__MoveTo_Response__fini(msg);
    return false;
  }
  return true;
}

void
modular_arm_interfaces__srv__MoveTo_Response__fini(modular_arm_interfaces__srv__MoveTo_Response * msg)
{
  if (!msg) {
    return;
  }
  // success
  // message
  rosidl_runtime_c__String__fini(&msg->message);
  // joint_angles
  rosidl_runtime_c__double__Sequence__fini(&msg->joint_angles);
}

bool
modular_arm_interfaces__srv__MoveTo_Response__are_equal(const modular_arm_interfaces__srv__MoveTo_Response * lhs, const modular_arm_interfaces__srv__MoveTo_Response * rhs)
{
  if (!lhs || !rhs) {
    return false;
  }
  // success
  if (lhs->success != rhs->success) {
    return false;
  }
  // message
  if (!rosidl_runtime_c__String__are_equal(
      &(lhs->message), &(rhs->message)))
  {
    return false;
  }
  // joint_angles
  if (!rosidl_runtime_c__double__Sequence__are_equal(
      &(lhs->joint_angles), &(rhs->joint_angles)))
  {
    return false;
  }
  return true;
}

bool
modular_arm_interfaces__srv__MoveTo_Response__copy(
  const modular_arm_interfaces__srv__MoveTo_Response * input,
  modular_arm_interfaces__srv__MoveTo_Response * output)
{
  if (!input || !output) {
    return false;
  }
  // success
  output->success = input->success;
  // message
  if (!rosidl_runtime_c__String__copy(
      &(input->message), &(output->message)))
  {
    return false;
  }
  // joint_angles
  if (!rosidl_runtime_c__double__Sequence__copy(
      &(input->joint_angles), &(output->joint_angles)))
  {
    return false;
  }
  return true;
}

modular_arm_interfaces__srv__MoveTo_Response *
modular_arm_interfaces__srv__MoveTo_Response__create(void)
{
  rcutils_allocator_t allocator = rcutils_get_default_allocator();
  modular_arm_interfaces__srv__MoveTo_Response * msg = (modular_arm_interfaces__srv__MoveTo_Response *)allocator.allocate(sizeof(modular_arm_interfaces__srv__MoveTo_Response), allocator.state);
  if (!msg) {
    return NULL;
  }
  memset(msg, 0, sizeof(modular_arm_interfaces__srv__MoveTo_Response));
  bool success = modular_arm_interfaces__srv__MoveTo_Response__init(msg);
  if (!success) {
    allocator.deallocate(msg, allocator.state);
    return NULL;
  }
  return msg;
}

void
modular_arm_interfaces__srv__MoveTo_Response__destroy(modular_arm_interfaces__srv__MoveTo_Response * msg)
{
  rcutils_allocator_t allocator = rcutils_get_default_allocator();
  if (msg) {
    modular_arm_interfaces__srv__MoveTo_Response__fini(msg);
  }
  allocator.deallocate(msg, allocator.state);
}


bool
modular_arm_interfaces__srv__MoveTo_Response__Sequence__init(modular_arm_interfaces__srv__MoveTo_Response__Sequence * array, size_t size)
{
  if (!array) {
    return false;
  }
  rcutils_allocator_t allocator = rcutils_get_default_allocator();
  modular_arm_interfaces__srv__MoveTo_Response * data = NULL;

  if (size) {
    if (size > SIZE_MAX / sizeof(modular_arm_interfaces__srv__MoveTo_Response)) {
      return false;
    }
    data = (modular_arm_interfaces__srv__MoveTo_Response *)allocator.zero_allocate(size, sizeof(modular_arm_interfaces__srv__MoveTo_Response), allocator.state);
    if (!data) {
      return false;
    }
    // initialize all array elements
    size_t i;
    for (i = 0; i < size; ++i) {
      bool success = modular_arm_interfaces__srv__MoveTo_Response__init(&data[i]);
      if (!success) {
        break;
      }
    }
    if (i < size) {
      // if initialization failed finalize the already initialized array elements
      for (; i > 0; --i) {
        modular_arm_interfaces__srv__MoveTo_Response__fini(&data[i - 1]);
      }
      allocator.deallocate(data, allocator.state);
      return false;
    }
  }
  array->data = data;
  array->size = size;
  array->capacity = size;
  return true;
}

void
modular_arm_interfaces__srv__MoveTo_Response__Sequence__fini(modular_arm_interfaces__srv__MoveTo_Response__Sequence * array)
{
  if (!array) {
    return;
  }
  rcutils_allocator_t allocator = rcutils_get_default_allocator();

  if (array->data) {
    // ensure that data and capacity values are consistent
    assert(array->capacity > 0);
    // finalize all array elements
    for (size_t i = 0; i < array->capacity; ++i) {
      modular_arm_interfaces__srv__MoveTo_Response__fini(&array->data[i]);
    }
    allocator.deallocate(array->data, allocator.state);
    array->data = NULL;
    array->size = 0;
    array->capacity = 0;
  } else {
    // ensure that data, size, and capacity values are consistent
    assert(0 == array->size);
    assert(0 == array->capacity);
  }
}

modular_arm_interfaces__srv__MoveTo_Response__Sequence *
modular_arm_interfaces__srv__MoveTo_Response__Sequence__create(size_t size)
{
  rcutils_allocator_t allocator = rcutils_get_default_allocator();
  modular_arm_interfaces__srv__MoveTo_Response__Sequence * array = (modular_arm_interfaces__srv__MoveTo_Response__Sequence *)allocator.allocate(sizeof(modular_arm_interfaces__srv__MoveTo_Response__Sequence), allocator.state);
  if (!array) {
    return NULL;
  }
  bool success = modular_arm_interfaces__srv__MoveTo_Response__Sequence__init(array, size);
  if (!success) {
    allocator.deallocate(array, allocator.state);
    return NULL;
  }
  return array;
}

void
modular_arm_interfaces__srv__MoveTo_Response__Sequence__destroy(modular_arm_interfaces__srv__MoveTo_Response__Sequence * array)
{
  rcutils_allocator_t allocator = rcutils_get_default_allocator();
  if (array) {
    modular_arm_interfaces__srv__MoveTo_Response__Sequence__fini(array);
  }
  allocator.deallocate(array, allocator.state);
}

bool
modular_arm_interfaces__srv__MoveTo_Response__Sequence__are_equal(const modular_arm_interfaces__srv__MoveTo_Response__Sequence * lhs, const modular_arm_interfaces__srv__MoveTo_Response__Sequence * rhs)
{
  if (!lhs || !rhs) {
    return false;
  }
  if (lhs->size != rhs->size) {
    return false;
  }
  for (size_t i = 0; i < lhs->size; ++i) {
    if (!modular_arm_interfaces__srv__MoveTo_Response__are_equal(&(lhs->data[i]), &(rhs->data[i]))) {
      return false;
    }
  }
  return true;
}

bool
modular_arm_interfaces__srv__MoveTo_Response__Sequence__copy(
  const modular_arm_interfaces__srv__MoveTo_Response__Sequence * input,
  modular_arm_interfaces__srv__MoveTo_Response__Sequence * output)
{
  if (!input || !output) {
    return false;
  }
  if (output->capacity < input->size) {
    if (input->size > SIZE_MAX / sizeof(modular_arm_interfaces__srv__MoveTo_Response)) {
      return false;
    }
    const size_t allocation_size =
      input->size * sizeof(modular_arm_interfaces__srv__MoveTo_Response);
    rcutils_allocator_t allocator = rcutils_get_default_allocator();
    modular_arm_interfaces__srv__MoveTo_Response * data =
      (modular_arm_interfaces__srv__MoveTo_Response *)allocator.reallocate(
      output->data, allocation_size, allocator.state);
    if (!data) {
      return false;
    }
    // If reallocation succeeded, memory may or may not have been moved
    // to fulfill the allocation request, invalidating output->data.
    output->data = data;
    for (size_t i = output->capacity; i < input->size; ++i) {
      if (!modular_arm_interfaces__srv__MoveTo_Response__init(&output->data[i])) {
        // If initialization of any new item fails, roll back
        // all previously initialized items. Existing items
        // in output are to be left unmodified.
        for (; i-- > output->capacity; ) {
          modular_arm_interfaces__srv__MoveTo_Response__fini(&output->data[i]);
        }
        return false;
      }
    }
    output->capacity = input->size;
  }
  output->size = input->size;
  for (size_t i = 0; i < input->size; ++i) {
    if (!modular_arm_interfaces__srv__MoveTo_Response__copy(
        &(input->data[i]), &(output->data[i])))
    {
      return false;
    }
  }
  return true;
}


// Include directives for member types
// Member `info`
#include "service_msgs/msg/detail/service_event_info__functions.h"
// Member `request`
// Member `response`
// already included above
// #include "modular_arm_interfaces/srv/detail/move_to__functions.h"

bool
modular_arm_interfaces__srv__MoveTo_Event__init(modular_arm_interfaces__srv__MoveTo_Event * msg)
{
  if (!msg) {
    return false;
  }
  // info
  if (!service_msgs__msg__ServiceEventInfo__init(&msg->info)) {
    modular_arm_interfaces__srv__MoveTo_Event__fini(msg);
    return false;
  }
  // request
  if (!modular_arm_interfaces__srv__MoveTo_Request__Sequence__init(&msg->request, 0)) {
    modular_arm_interfaces__srv__MoveTo_Event__fini(msg);
    return false;
  }
  // response
  if (!modular_arm_interfaces__srv__MoveTo_Response__Sequence__init(&msg->response, 0)) {
    modular_arm_interfaces__srv__MoveTo_Event__fini(msg);
    return false;
  }
  return true;
}

void
modular_arm_interfaces__srv__MoveTo_Event__fini(modular_arm_interfaces__srv__MoveTo_Event * msg)
{
  if (!msg) {
    return;
  }
  // info
  service_msgs__msg__ServiceEventInfo__fini(&msg->info);
  // request
  modular_arm_interfaces__srv__MoveTo_Request__Sequence__fini(&msg->request);
  // response
  modular_arm_interfaces__srv__MoveTo_Response__Sequence__fini(&msg->response);
}

bool
modular_arm_interfaces__srv__MoveTo_Event__are_equal(const modular_arm_interfaces__srv__MoveTo_Event * lhs, const modular_arm_interfaces__srv__MoveTo_Event * rhs)
{
  if (!lhs || !rhs) {
    return false;
  }
  // info
  if (!service_msgs__msg__ServiceEventInfo__are_equal(
      &(lhs->info), &(rhs->info)))
  {
    return false;
  }
  // request
  if (!modular_arm_interfaces__srv__MoveTo_Request__Sequence__are_equal(
      &(lhs->request), &(rhs->request)))
  {
    return false;
  }
  // response
  if (!modular_arm_interfaces__srv__MoveTo_Response__Sequence__are_equal(
      &(lhs->response), &(rhs->response)))
  {
    return false;
  }
  return true;
}

bool
modular_arm_interfaces__srv__MoveTo_Event__copy(
  const modular_arm_interfaces__srv__MoveTo_Event * input,
  modular_arm_interfaces__srv__MoveTo_Event * output)
{
  if (!input || !output) {
    return false;
  }
  // info
  if (!service_msgs__msg__ServiceEventInfo__copy(
      &(input->info), &(output->info)))
  {
    return false;
  }
  // request
  if (!modular_arm_interfaces__srv__MoveTo_Request__Sequence__copy(
      &(input->request), &(output->request)))
  {
    return false;
  }
  // response
  if (!modular_arm_interfaces__srv__MoveTo_Response__Sequence__copy(
      &(input->response), &(output->response)))
  {
    return false;
  }
  return true;
}

modular_arm_interfaces__srv__MoveTo_Event *
modular_arm_interfaces__srv__MoveTo_Event__create(void)
{
  rcutils_allocator_t allocator = rcutils_get_default_allocator();
  modular_arm_interfaces__srv__MoveTo_Event * msg = (modular_arm_interfaces__srv__MoveTo_Event *)allocator.allocate(sizeof(modular_arm_interfaces__srv__MoveTo_Event), allocator.state);
  if (!msg) {
    return NULL;
  }
  memset(msg, 0, sizeof(modular_arm_interfaces__srv__MoveTo_Event));
  bool success = modular_arm_interfaces__srv__MoveTo_Event__init(msg);
  if (!success) {
    allocator.deallocate(msg, allocator.state);
    return NULL;
  }
  return msg;
}

void
modular_arm_interfaces__srv__MoveTo_Event__destroy(modular_arm_interfaces__srv__MoveTo_Event * msg)
{
  rcutils_allocator_t allocator = rcutils_get_default_allocator();
  if (msg) {
    modular_arm_interfaces__srv__MoveTo_Event__fini(msg);
  }
  allocator.deallocate(msg, allocator.state);
}


bool
modular_arm_interfaces__srv__MoveTo_Event__Sequence__init(modular_arm_interfaces__srv__MoveTo_Event__Sequence * array, size_t size)
{
  if (!array) {
    return false;
  }
  rcutils_allocator_t allocator = rcutils_get_default_allocator();
  modular_arm_interfaces__srv__MoveTo_Event * data = NULL;

  if (size) {
    if (size > SIZE_MAX / sizeof(modular_arm_interfaces__srv__MoveTo_Event)) {
      return false;
    }
    data = (modular_arm_interfaces__srv__MoveTo_Event *)allocator.zero_allocate(size, sizeof(modular_arm_interfaces__srv__MoveTo_Event), allocator.state);
    if (!data) {
      return false;
    }
    // initialize all array elements
    size_t i;
    for (i = 0; i < size; ++i) {
      bool success = modular_arm_interfaces__srv__MoveTo_Event__init(&data[i]);
      if (!success) {
        break;
      }
    }
    if (i < size) {
      // if initialization failed finalize the already initialized array elements
      for (; i > 0; --i) {
        modular_arm_interfaces__srv__MoveTo_Event__fini(&data[i - 1]);
      }
      allocator.deallocate(data, allocator.state);
      return false;
    }
  }
  array->data = data;
  array->size = size;
  array->capacity = size;
  return true;
}

void
modular_arm_interfaces__srv__MoveTo_Event__Sequence__fini(modular_arm_interfaces__srv__MoveTo_Event__Sequence * array)
{
  if (!array) {
    return;
  }
  rcutils_allocator_t allocator = rcutils_get_default_allocator();

  if (array->data) {
    // ensure that data and capacity values are consistent
    assert(array->capacity > 0);
    // finalize all array elements
    for (size_t i = 0; i < array->capacity; ++i) {
      modular_arm_interfaces__srv__MoveTo_Event__fini(&array->data[i]);
    }
    allocator.deallocate(array->data, allocator.state);
    array->data = NULL;
    array->size = 0;
    array->capacity = 0;
  } else {
    // ensure that data, size, and capacity values are consistent
    assert(0 == array->size);
    assert(0 == array->capacity);
  }
}

modular_arm_interfaces__srv__MoveTo_Event__Sequence *
modular_arm_interfaces__srv__MoveTo_Event__Sequence__create(size_t size)
{
  rcutils_allocator_t allocator = rcutils_get_default_allocator();
  modular_arm_interfaces__srv__MoveTo_Event__Sequence * array = (modular_arm_interfaces__srv__MoveTo_Event__Sequence *)allocator.allocate(sizeof(modular_arm_interfaces__srv__MoveTo_Event__Sequence), allocator.state);
  if (!array) {
    return NULL;
  }
  bool success = modular_arm_interfaces__srv__MoveTo_Event__Sequence__init(array, size);
  if (!success) {
    allocator.deallocate(array, allocator.state);
    return NULL;
  }
  return array;
}

void
modular_arm_interfaces__srv__MoveTo_Event__Sequence__destroy(modular_arm_interfaces__srv__MoveTo_Event__Sequence * array)
{
  rcutils_allocator_t allocator = rcutils_get_default_allocator();
  if (array) {
    modular_arm_interfaces__srv__MoveTo_Event__Sequence__fini(array);
  }
  allocator.deallocate(array, allocator.state);
}

bool
modular_arm_interfaces__srv__MoveTo_Event__Sequence__are_equal(const modular_arm_interfaces__srv__MoveTo_Event__Sequence * lhs, const modular_arm_interfaces__srv__MoveTo_Event__Sequence * rhs)
{
  if (!lhs || !rhs) {
    return false;
  }
  if (lhs->size != rhs->size) {
    return false;
  }
  for (size_t i = 0; i < lhs->size; ++i) {
    if (!modular_arm_interfaces__srv__MoveTo_Event__are_equal(&(lhs->data[i]), &(rhs->data[i]))) {
      return false;
    }
  }
  return true;
}

bool
modular_arm_interfaces__srv__MoveTo_Event__Sequence__copy(
  const modular_arm_interfaces__srv__MoveTo_Event__Sequence * input,
  modular_arm_interfaces__srv__MoveTo_Event__Sequence * output)
{
  if (!input || !output) {
    return false;
  }
  if (output->capacity < input->size) {
    if (input->size > SIZE_MAX / sizeof(modular_arm_interfaces__srv__MoveTo_Event)) {
      return false;
    }
    const size_t allocation_size =
      input->size * sizeof(modular_arm_interfaces__srv__MoveTo_Event);
    rcutils_allocator_t allocator = rcutils_get_default_allocator();
    modular_arm_interfaces__srv__MoveTo_Event * data =
      (modular_arm_interfaces__srv__MoveTo_Event *)allocator.reallocate(
      output->data, allocation_size, allocator.state);
    if (!data) {
      return false;
    }
    // If reallocation succeeded, memory may or may not have been moved
    // to fulfill the allocation request, invalidating output->data.
    output->data = data;
    for (size_t i = output->capacity; i < input->size; ++i) {
      if (!modular_arm_interfaces__srv__MoveTo_Event__init(&output->data[i])) {
        // If initialization of any new item fails, roll back
        // all previously initialized items. Existing items
        // in output are to be left unmodified.
        for (; i-- > output->capacity; ) {
          modular_arm_interfaces__srv__MoveTo_Event__fini(&output->data[i]);
        }
        return false;
      }
    }
    output->capacity = input->size;
  }
  output->size = input->size;
  for (size_t i = 0; i < input->size; ++i) {
    if (!modular_arm_interfaces__srv__MoveTo_Event__copy(
        &(input->data[i]), &(output->data[i])))
    {
      return false;
    }
  }
  return true;
}
