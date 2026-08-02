// generated from rosidl_typesupport_cpp/resource/idl__type_support.cpp.em
// with input from modular_arm_interfaces:srv/MoveTo.idl
// generated code does not contain a copyright notice

#include "cstddef"
#include "rosidl_runtime_c/message_type_support_struct.h"
#include "modular_arm_interfaces/srv/detail/move_to__functions.h"
#include "modular_arm_interfaces/srv/detail/move_to__struct.hpp"
#include "rosidl_typesupport_cpp/identifier.hpp"
#include "rosidl_typesupport_cpp/message_type_support.hpp"
#include "rosidl_typesupport_c/type_support_map.h"
#include "rosidl_typesupport_cpp/message_type_support_dispatch.hpp"
#include "rosidl_typesupport_cpp/visibility_control.h"
#include "rosidl_typesupport_interface/macros.h"

namespace modular_arm_interfaces
{

namespace srv
{

namespace rosidl_typesupport_cpp
{

typedef struct _MoveTo_Request_type_support_ids_t
{
  const char * typesupport_identifier[2];
} _MoveTo_Request_type_support_ids_t;

static const _MoveTo_Request_type_support_ids_t _MoveTo_Request_message_typesupport_ids = {
  {
    "rosidl_typesupport_fastrtps_cpp",  // ::rosidl_typesupport_fastrtps_cpp::typesupport_identifier,
    "rosidl_typesupport_introspection_cpp",  // ::rosidl_typesupport_introspection_cpp::typesupport_identifier,
  }
};

typedef struct _MoveTo_Request_type_support_symbol_names_t
{
  const char * symbol_name[2];
} _MoveTo_Request_type_support_symbol_names_t;

#define STRINGIFY_(s) #s
#define STRINGIFY(s) STRINGIFY_(s)

static const _MoveTo_Request_type_support_symbol_names_t _MoveTo_Request_message_typesupport_symbol_names = {
  {
    STRINGIFY(ROSIDL_TYPESUPPORT_INTERFACE__MESSAGE_SYMBOL_NAME(rosidl_typesupport_fastrtps_cpp, modular_arm_interfaces, srv, MoveTo_Request)),
    STRINGIFY(ROSIDL_TYPESUPPORT_INTERFACE__MESSAGE_SYMBOL_NAME(rosidl_typesupport_introspection_cpp, modular_arm_interfaces, srv, MoveTo_Request)),
  }
};

typedef struct _MoveTo_Request_type_support_data_t
{
  void * data[2];
} _MoveTo_Request_type_support_data_t;

static _MoveTo_Request_type_support_data_t _MoveTo_Request_message_typesupport_data = {
  {
    0,  // will store the shared library later
    0,  // will store the shared library later
  }
};

static const type_support_map_t _MoveTo_Request_message_typesupport_map = {
  2,
  "modular_arm_interfaces",
  &_MoveTo_Request_message_typesupport_ids.typesupport_identifier[0],
  &_MoveTo_Request_message_typesupport_symbol_names.symbol_name[0],
  &_MoveTo_Request_message_typesupport_data.data[0],
};

static const rosidl_message_type_support_t MoveTo_Request_message_type_support_handle = {
  ::rosidl_typesupport_cpp::typesupport_identifier,
  reinterpret_cast<const type_support_map_t *>(&_MoveTo_Request_message_typesupport_map),
  ::rosidl_typesupport_cpp::get_message_typesupport_handle_function,
  &modular_arm_interfaces__srv__MoveTo_Request__get_type_hash,
  &modular_arm_interfaces__srv__MoveTo_Request__get_type_description,
  &modular_arm_interfaces__srv__MoveTo_Request__get_type_description_sources,
};

}  // namespace rosidl_typesupport_cpp

}  // namespace srv

}  // namespace modular_arm_interfaces

namespace rosidl_typesupport_cpp
{

template<>
ROSIDL_TYPESUPPORT_CPP_PUBLIC
const rosidl_message_type_support_t *
get_message_type_support_handle<modular_arm_interfaces::srv::MoveTo_Request>()
{
  return &::modular_arm_interfaces::srv::rosidl_typesupport_cpp::MoveTo_Request_message_type_support_handle;
}

#ifdef __cplusplus
extern "C"
{
#endif

ROSIDL_TYPESUPPORT_CPP_PUBLIC
const rosidl_message_type_support_t *
ROSIDL_TYPESUPPORT_INTERFACE__MESSAGE_SYMBOL_NAME(rosidl_typesupport_cpp, modular_arm_interfaces, srv, MoveTo_Request)() {
  return get_message_type_support_handle<modular_arm_interfaces::srv::MoveTo_Request>();
}

#ifdef __cplusplus
}
#endif
}  // namespace rosidl_typesupport_cpp

// already included above
// #include "cstddef"
// already included above
// #include "rosidl_runtime_c/message_type_support_struct.h"
// already included above
// #include "modular_arm_interfaces/srv/detail/move_to__functions.h"
// already included above
// #include "modular_arm_interfaces/srv/detail/move_to__struct.hpp"
// already included above
// #include "rosidl_typesupport_cpp/identifier.hpp"
// already included above
// #include "rosidl_typesupport_cpp/message_type_support.hpp"
// already included above
// #include "rosidl_typesupport_c/type_support_map.h"
// already included above
// #include "rosidl_typesupport_cpp/message_type_support_dispatch.hpp"
// already included above
// #include "rosidl_typesupport_cpp/visibility_control.h"
// already included above
// #include "rosidl_typesupport_interface/macros.h"

namespace modular_arm_interfaces
{

namespace srv
{

namespace rosidl_typesupport_cpp
{

typedef struct _MoveTo_Response_type_support_ids_t
{
  const char * typesupport_identifier[2];
} _MoveTo_Response_type_support_ids_t;

static const _MoveTo_Response_type_support_ids_t _MoveTo_Response_message_typesupport_ids = {
  {
    "rosidl_typesupport_fastrtps_cpp",  // ::rosidl_typesupport_fastrtps_cpp::typesupport_identifier,
    "rosidl_typesupport_introspection_cpp",  // ::rosidl_typesupport_introspection_cpp::typesupport_identifier,
  }
};

typedef struct _MoveTo_Response_type_support_symbol_names_t
{
  const char * symbol_name[2];
} _MoveTo_Response_type_support_symbol_names_t;

#define STRINGIFY_(s) #s
#define STRINGIFY(s) STRINGIFY_(s)

static const _MoveTo_Response_type_support_symbol_names_t _MoveTo_Response_message_typesupport_symbol_names = {
  {
    STRINGIFY(ROSIDL_TYPESUPPORT_INTERFACE__MESSAGE_SYMBOL_NAME(rosidl_typesupport_fastrtps_cpp, modular_arm_interfaces, srv, MoveTo_Response)),
    STRINGIFY(ROSIDL_TYPESUPPORT_INTERFACE__MESSAGE_SYMBOL_NAME(rosidl_typesupport_introspection_cpp, modular_arm_interfaces, srv, MoveTo_Response)),
  }
};

typedef struct _MoveTo_Response_type_support_data_t
{
  void * data[2];
} _MoveTo_Response_type_support_data_t;

static _MoveTo_Response_type_support_data_t _MoveTo_Response_message_typesupport_data = {
  {
    0,  // will store the shared library later
    0,  // will store the shared library later
  }
};

static const type_support_map_t _MoveTo_Response_message_typesupport_map = {
  2,
  "modular_arm_interfaces",
  &_MoveTo_Response_message_typesupport_ids.typesupport_identifier[0],
  &_MoveTo_Response_message_typesupport_symbol_names.symbol_name[0],
  &_MoveTo_Response_message_typesupport_data.data[0],
};

static const rosidl_message_type_support_t MoveTo_Response_message_type_support_handle = {
  ::rosidl_typesupport_cpp::typesupport_identifier,
  reinterpret_cast<const type_support_map_t *>(&_MoveTo_Response_message_typesupport_map),
  ::rosidl_typesupport_cpp::get_message_typesupport_handle_function,
  &modular_arm_interfaces__srv__MoveTo_Response__get_type_hash,
  &modular_arm_interfaces__srv__MoveTo_Response__get_type_description,
  &modular_arm_interfaces__srv__MoveTo_Response__get_type_description_sources,
};

}  // namespace rosidl_typesupport_cpp

}  // namespace srv

}  // namespace modular_arm_interfaces

namespace rosidl_typesupport_cpp
{

template<>
ROSIDL_TYPESUPPORT_CPP_PUBLIC
const rosidl_message_type_support_t *
get_message_type_support_handle<modular_arm_interfaces::srv::MoveTo_Response>()
{
  return &::modular_arm_interfaces::srv::rosidl_typesupport_cpp::MoveTo_Response_message_type_support_handle;
}

#ifdef __cplusplus
extern "C"
{
#endif

ROSIDL_TYPESUPPORT_CPP_PUBLIC
const rosidl_message_type_support_t *
ROSIDL_TYPESUPPORT_INTERFACE__MESSAGE_SYMBOL_NAME(rosidl_typesupport_cpp, modular_arm_interfaces, srv, MoveTo_Response)() {
  return get_message_type_support_handle<modular_arm_interfaces::srv::MoveTo_Response>();
}

#ifdef __cplusplus
}
#endif
}  // namespace rosidl_typesupport_cpp

// already included above
// #include "cstddef"
// already included above
// #include "rosidl_runtime_c/message_type_support_struct.h"
// already included above
// #include "modular_arm_interfaces/srv/detail/move_to__functions.h"
// already included above
// #include "modular_arm_interfaces/srv/detail/move_to__struct.hpp"
// already included above
// #include "rosidl_typesupport_cpp/identifier.hpp"
// already included above
// #include "rosidl_typesupport_cpp/message_type_support.hpp"
// already included above
// #include "rosidl_typesupport_c/type_support_map.h"
// already included above
// #include "rosidl_typesupport_cpp/message_type_support_dispatch.hpp"
// already included above
// #include "rosidl_typesupport_cpp/visibility_control.h"
// already included above
// #include "rosidl_typesupport_interface/macros.h"

namespace modular_arm_interfaces
{

namespace srv
{

namespace rosidl_typesupport_cpp
{

typedef struct _MoveTo_Event_type_support_ids_t
{
  const char * typesupport_identifier[2];
} _MoveTo_Event_type_support_ids_t;

static const _MoveTo_Event_type_support_ids_t _MoveTo_Event_message_typesupport_ids = {
  {
    "rosidl_typesupport_fastrtps_cpp",  // ::rosidl_typesupport_fastrtps_cpp::typesupport_identifier,
    "rosidl_typesupport_introspection_cpp",  // ::rosidl_typesupport_introspection_cpp::typesupport_identifier,
  }
};

typedef struct _MoveTo_Event_type_support_symbol_names_t
{
  const char * symbol_name[2];
} _MoveTo_Event_type_support_symbol_names_t;

#define STRINGIFY_(s) #s
#define STRINGIFY(s) STRINGIFY_(s)

static const _MoveTo_Event_type_support_symbol_names_t _MoveTo_Event_message_typesupport_symbol_names = {
  {
    STRINGIFY(ROSIDL_TYPESUPPORT_INTERFACE__MESSAGE_SYMBOL_NAME(rosidl_typesupport_fastrtps_cpp, modular_arm_interfaces, srv, MoveTo_Event)),
    STRINGIFY(ROSIDL_TYPESUPPORT_INTERFACE__MESSAGE_SYMBOL_NAME(rosidl_typesupport_introspection_cpp, modular_arm_interfaces, srv, MoveTo_Event)),
  }
};

typedef struct _MoveTo_Event_type_support_data_t
{
  void * data[2];
} _MoveTo_Event_type_support_data_t;

static _MoveTo_Event_type_support_data_t _MoveTo_Event_message_typesupport_data = {
  {
    0,  // will store the shared library later
    0,  // will store the shared library later
  }
};

static const type_support_map_t _MoveTo_Event_message_typesupport_map = {
  2,
  "modular_arm_interfaces",
  &_MoveTo_Event_message_typesupport_ids.typesupport_identifier[0],
  &_MoveTo_Event_message_typesupport_symbol_names.symbol_name[0],
  &_MoveTo_Event_message_typesupport_data.data[0],
};

static const rosidl_message_type_support_t MoveTo_Event_message_type_support_handle = {
  ::rosidl_typesupport_cpp::typesupport_identifier,
  reinterpret_cast<const type_support_map_t *>(&_MoveTo_Event_message_typesupport_map),
  ::rosidl_typesupport_cpp::get_message_typesupport_handle_function,
  &modular_arm_interfaces__srv__MoveTo_Event__get_type_hash,
  &modular_arm_interfaces__srv__MoveTo_Event__get_type_description,
  &modular_arm_interfaces__srv__MoveTo_Event__get_type_description_sources,
};

}  // namespace rosidl_typesupport_cpp

}  // namespace srv

}  // namespace modular_arm_interfaces

namespace rosidl_typesupport_cpp
{

template<>
ROSIDL_TYPESUPPORT_CPP_PUBLIC
const rosidl_message_type_support_t *
get_message_type_support_handle<modular_arm_interfaces::srv::MoveTo_Event>()
{
  return &::modular_arm_interfaces::srv::rosidl_typesupport_cpp::MoveTo_Event_message_type_support_handle;
}

#ifdef __cplusplus
extern "C"
{
#endif

ROSIDL_TYPESUPPORT_CPP_PUBLIC
const rosidl_message_type_support_t *
ROSIDL_TYPESUPPORT_INTERFACE__MESSAGE_SYMBOL_NAME(rosidl_typesupport_cpp, modular_arm_interfaces, srv, MoveTo_Event)() {
  return get_message_type_support_handle<modular_arm_interfaces::srv::MoveTo_Event>();
}

#ifdef __cplusplus
}
#endif
}  // namespace rosidl_typesupport_cpp

// already included above
// #include "cstddef"
#include "rosidl_runtime_c/service_type_support_struct.h"
#include "rosidl_typesupport_cpp/service_type_support.hpp"
// already included above
// #include "modular_arm_interfaces/srv/detail/move_to__struct.hpp"
// already included above
// #include "rosidl_typesupport_cpp/identifier.hpp"
// already included above
// #include "rosidl_typesupport_c/type_support_map.h"
#include "rosidl_typesupport_cpp/service_type_support_dispatch.hpp"
// already included above
// #include "rosidl_typesupport_cpp/visibility_control.h"
// already included above
// #include "rosidl_typesupport_interface/macros.h"

namespace modular_arm_interfaces
{

namespace srv
{

namespace rosidl_typesupport_cpp
{

typedef struct _MoveTo_type_support_ids_t
{
  const char * typesupport_identifier[2];
} _MoveTo_type_support_ids_t;

static const _MoveTo_type_support_ids_t _MoveTo_service_typesupport_ids = {
  {
    "rosidl_typesupport_fastrtps_cpp",  // ::rosidl_typesupport_fastrtps_cpp::typesupport_identifier,
    "rosidl_typesupport_introspection_cpp",  // ::rosidl_typesupport_introspection_cpp::typesupport_identifier,
  }
};

typedef struct _MoveTo_type_support_symbol_names_t
{
  const char * symbol_name[2];
} _MoveTo_type_support_symbol_names_t;
#define STRINGIFY_(s) #s
#define STRINGIFY(s) STRINGIFY_(s)

static const _MoveTo_type_support_symbol_names_t _MoveTo_service_typesupport_symbol_names = {
  {
    STRINGIFY(ROSIDL_TYPESUPPORT_INTERFACE__SERVICE_SYMBOL_NAME(rosidl_typesupport_fastrtps_cpp, modular_arm_interfaces, srv, MoveTo)),
    STRINGIFY(ROSIDL_TYPESUPPORT_INTERFACE__SERVICE_SYMBOL_NAME(rosidl_typesupport_introspection_cpp, modular_arm_interfaces, srv, MoveTo)),
  }
};

typedef struct _MoveTo_type_support_data_t
{
  void * data[2];
} _MoveTo_type_support_data_t;

static _MoveTo_type_support_data_t _MoveTo_service_typesupport_data = {
  {
    0,  // will store the shared library later
    0,  // will store the shared library later
  }
};

static const type_support_map_t _MoveTo_service_typesupport_map = {
  2,
  "modular_arm_interfaces",
  &_MoveTo_service_typesupport_ids.typesupport_identifier[0],
  &_MoveTo_service_typesupport_symbol_names.symbol_name[0],
  &_MoveTo_service_typesupport_data.data[0],
};

static const rosidl_service_type_support_t MoveTo_service_type_support_handle = {
  ::rosidl_typesupport_cpp::typesupport_identifier,
  reinterpret_cast<const type_support_map_t *>(&_MoveTo_service_typesupport_map),
  ::rosidl_typesupport_cpp::get_service_typesupport_handle_function,
  ::rosidl_typesupport_cpp::get_message_type_support_handle<modular_arm_interfaces::srv::MoveTo_Request>(),
  ::rosidl_typesupport_cpp::get_message_type_support_handle<modular_arm_interfaces::srv::MoveTo_Response>(),
  ::rosidl_typesupport_cpp::get_message_type_support_handle<modular_arm_interfaces::srv::MoveTo_Event>(),
  &::rosidl_typesupport_cpp::service_create_event_message<modular_arm_interfaces::srv::MoveTo>,
  &::rosidl_typesupport_cpp::service_destroy_event_message<modular_arm_interfaces::srv::MoveTo>,
  &modular_arm_interfaces__srv__MoveTo__get_type_hash,
  &modular_arm_interfaces__srv__MoveTo__get_type_description,
  &modular_arm_interfaces__srv__MoveTo__get_type_description_sources,
};

}  // namespace rosidl_typesupport_cpp

}  // namespace srv

}  // namespace modular_arm_interfaces

namespace rosidl_typesupport_cpp
{

template<>
ROSIDL_TYPESUPPORT_CPP_PUBLIC
const rosidl_service_type_support_t *
get_service_type_support_handle<modular_arm_interfaces::srv::MoveTo>()
{
  return &::modular_arm_interfaces::srv::rosidl_typesupport_cpp::MoveTo_service_type_support_handle;
}

}  // namespace rosidl_typesupport_cpp

#ifdef __cplusplus
extern "C"
{
#endif

ROSIDL_TYPESUPPORT_CPP_PUBLIC
const rosidl_service_type_support_t *
ROSIDL_TYPESUPPORT_INTERFACE__SERVICE_SYMBOL_NAME(rosidl_typesupport_cpp, modular_arm_interfaces, srv, MoveTo)() {
  return ::rosidl_typesupport_cpp::get_service_type_support_handle<modular_arm_interfaces::srv::MoveTo>();
}

#ifdef __cplusplus
}
#endif
