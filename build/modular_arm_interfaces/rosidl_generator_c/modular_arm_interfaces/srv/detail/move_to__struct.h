// generated from rosidl_generator_c/resource/idl__struct.h.em
// with input from modular_arm_interfaces:srv/MoveTo.idl
// generated code does not contain a copyright notice

// IWYU pragma: private, include "modular_arm_interfaces/srv/move_to.h"


#ifndef MODULAR_ARM_INTERFACES__SRV__DETAIL__MOVE_TO__STRUCT_H_
#define MODULAR_ARM_INTERFACES__SRV__DETAIL__MOVE_TO__STRUCT_H_

#ifdef __cplusplus
extern "C"
{
#endif

#include <stdbool.h>
#include <stddef.h>
#include <stdint.h>


// Constants defined in the message

// Include directives for member types
// Member 'elbow'
#include "rosidl_runtime_c/string.h"

/// Struct defined in srv/MoveTo in the package modular_arm_interfaces.
typedef struct modular_arm_interfaces__srv__MoveTo_Request
{
  double x;
  double y;
  double z;
  double pitch;
  /// "up" or "down"
  rosidl_runtime_c__String elbow;
  /// time to execute the trajectory, e.g. 2.0
  double duration_sec;
} modular_arm_interfaces__srv__MoveTo_Request;

// Struct for a sequence of modular_arm_interfaces__srv__MoveTo_Request.
typedef struct modular_arm_interfaces__srv__MoveTo_Request__Sequence
{
  modular_arm_interfaces__srv__MoveTo_Request * data;
  /// The number of valid items in data
  size_t size;
  /// The number of allocated items in data
  size_t capacity;
} modular_arm_interfaces__srv__MoveTo_Request__Sequence;

// Constants defined in the message

// Include directives for member types
// Member 'message'
// already included above
// #include "rosidl_runtime_c/string.h"
// Member 'joint_angles'
#include "rosidl_runtime_c/primitives_sequence.h"

/// Struct defined in srv/MoveTo in the package modular_arm_interfaces.
typedef struct modular_arm_interfaces__srv__MoveTo_Response
{
  bool success;
  rosidl_runtime_c__String message;
  /// [theta1, theta2, theta3, theta4] actually commanded, radians
  rosidl_runtime_c__double__Sequence joint_angles;
} modular_arm_interfaces__srv__MoveTo_Response;

// Struct for a sequence of modular_arm_interfaces__srv__MoveTo_Response.
typedef struct modular_arm_interfaces__srv__MoveTo_Response__Sequence
{
  modular_arm_interfaces__srv__MoveTo_Response * data;
  /// The number of valid items in data
  size_t size;
  /// The number of allocated items in data
  size_t capacity;
} modular_arm_interfaces__srv__MoveTo_Response__Sequence;

// Constants defined in the message

// Include directives for member types
// Member 'info'
#include "service_msgs/msg/detail/service_event_info__struct.h"

// constants for array fields with an upper bound
// request
enum
{
  modular_arm_interfaces__srv__MoveTo_Event__request__MAX_SIZE = 1
};
// response
enum
{
  modular_arm_interfaces__srv__MoveTo_Event__response__MAX_SIZE = 1
};

/// Struct defined in srv/MoveTo in the package modular_arm_interfaces.
typedef struct modular_arm_interfaces__srv__MoveTo_Event
{
  service_msgs__msg__ServiceEventInfo info;
  modular_arm_interfaces__srv__MoveTo_Request__Sequence request;
  modular_arm_interfaces__srv__MoveTo_Response__Sequence response;
} modular_arm_interfaces__srv__MoveTo_Event;

// Struct for a sequence of modular_arm_interfaces__srv__MoveTo_Event.
typedef struct modular_arm_interfaces__srv__MoveTo_Event__Sequence
{
  modular_arm_interfaces__srv__MoveTo_Event * data;
  /// The number of valid items in data
  size_t size;
  /// The number of allocated items in data
  size_t capacity;
} modular_arm_interfaces__srv__MoveTo_Event__Sequence;

#ifdef __cplusplus
}
#endif

#endif  // MODULAR_ARM_INTERFACES__SRV__DETAIL__MOVE_TO__STRUCT_H_
