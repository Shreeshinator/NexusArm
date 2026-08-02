// generated from rosidl_generator_c/resource/idl__description.c.em
// with input from modular_arm_interfaces:srv/MoveTo.idl
// generated code does not contain a copyright notice

#include "modular_arm_interfaces/srv/detail/move_to__functions.h"

ROSIDL_GENERATOR_C_PUBLIC_modular_arm_interfaces
const rosidl_type_hash_t *
modular_arm_interfaces__srv__MoveTo__get_type_hash(
  const rosidl_service_type_support_t * type_support)
{
  (void)type_support;
  static rosidl_type_hash_t hash = {1, {
      0xba, 0x76, 0x70, 0xe5, 0xa2, 0x1b, 0x63, 0xc1,
      0x2a, 0xa3, 0x7b, 0x83, 0xfa, 0x57, 0x4a, 0x2d,
      0x15, 0x46, 0xb8, 0x7e, 0x84, 0x34, 0x5e, 0x4c,
      0xc3, 0xf7, 0x34, 0xee, 0x6b, 0x18, 0x79, 0x6d,
    }};
  return &hash;
}

ROSIDL_GENERATOR_C_PUBLIC_modular_arm_interfaces
const rosidl_type_hash_t *
modular_arm_interfaces__srv__MoveTo_Request__get_type_hash(
  const rosidl_message_type_support_t * type_support)
{
  (void)type_support;
  static rosidl_type_hash_t hash = {1, {
      0xc1, 0x2a, 0xcf, 0x9c, 0x79, 0x64, 0x1a, 0x0c,
      0x0d, 0xbe, 0x29, 0x8b, 0xfc, 0x97, 0xce, 0x62,
      0x97, 0x9b, 0xf0, 0x72, 0x7c, 0xbb, 0xe5, 0x4a,
      0x06, 0x4b, 0x00, 0x97, 0xab, 0x91, 0xb5, 0x96,
    }};
  return &hash;
}

ROSIDL_GENERATOR_C_PUBLIC_modular_arm_interfaces
const rosidl_type_hash_t *
modular_arm_interfaces__srv__MoveTo_Response__get_type_hash(
  const rosidl_message_type_support_t * type_support)
{
  (void)type_support;
  static rosidl_type_hash_t hash = {1, {
      0xdf, 0x2c, 0xf3, 0x01, 0x13, 0xba, 0x9d, 0x57,
      0x61, 0xec, 0x4f, 0x9b, 0xe4, 0x48, 0xb9, 0x6a,
      0xc5, 0x2f, 0x26, 0x0f, 0x86, 0x26, 0xbc, 0xd5,
      0x76, 0x90, 0xa0, 0xb8, 0x69, 0x53, 0x13, 0x39,
    }};
  return &hash;
}

ROSIDL_GENERATOR_C_PUBLIC_modular_arm_interfaces
const rosidl_type_hash_t *
modular_arm_interfaces__srv__MoveTo_Event__get_type_hash(
  const rosidl_message_type_support_t * type_support)
{
  (void)type_support;
  static rosidl_type_hash_t hash = {1, {
      0x25, 0xa5, 0xff, 0xdd, 0x55, 0x14, 0xd3, 0xe2,
      0xda, 0x18, 0xdc, 0xb4, 0x8e, 0xa9, 0x10, 0x96,
      0xeb, 0xd2, 0xe9, 0x66, 0x65, 0x35, 0x83, 0xf2,
      0x08, 0x2b, 0x4c, 0x59, 0x80, 0x02, 0x22, 0x94,
    }};
  return &hash;
}

#include <assert.h>
#include <string.h>

// Include directives for referenced types
#include "service_msgs/msg/detail/service_event_info__functions.h"
#include "builtin_interfaces/msg/detail/time__functions.h"

// Hashes for external referenced types
#ifndef NDEBUG
static const rosidl_type_hash_t builtin_interfaces__msg__Time__EXPECTED_HASH = {1, {
    0xb1, 0x06, 0x23, 0x5e, 0x25, 0xa4, 0xc5, 0xed,
    0x35, 0x09, 0x8a, 0xa0, 0xa6, 0x1a, 0x3e, 0xe9,
    0xc9, 0xb1, 0x8d, 0x19, 0x7f, 0x39, 0x8b, 0x0e,
    0x42, 0x06, 0xce, 0xa9, 0xac, 0xf9, 0xc1, 0x97,
  }};
static const rosidl_type_hash_t service_msgs__msg__ServiceEventInfo__EXPECTED_HASH = {1, {
    0x41, 0xbc, 0xbb, 0xe0, 0x7a, 0x75, 0xc9, 0xb5,
    0x2b, 0xc9, 0x6b, 0xfd, 0x5c, 0x24, 0xd7, 0xf0,
    0xfc, 0x0a, 0x08, 0xc0, 0xcb, 0x79, 0x21, 0xb3,
    0x37, 0x3c, 0x57, 0x32, 0x34, 0x5a, 0x6f, 0x45,
  }};
#endif

static char modular_arm_interfaces__srv__MoveTo__TYPE_NAME[] = "modular_arm_interfaces/srv/MoveTo";
static char builtin_interfaces__msg__Time__TYPE_NAME[] = "builtin_interfaces/msg/Time";
static char modular_arm_interfaces__srv__MoveTo_Event__TYPE_NAME[] = "modular_arm_interfaces/srv/MoveTo_Event";
static char modular_arm_interfaces__srv__MoveTo_Request__TYPE_NAME[] = "modular_arm_interfaces/srv/MoveTo_Request";
static char modular_arm_interfaces__srv__MoveTo_Response__TYPE_NAME[] = "modular_arm_interfaces/srv/MoveTo_Response";
static char service_msgs__msg__ServiceEventInfo__TYPE_NAME[] = "service_msgs/msg/ServiceEventInfo";

// Define type names, field names, and default values
static char modular_arm_interfaces__srv__MoveTo__FIELD_NAME__request_message[] = "request_message";
static char modular_arm_interfaces__srv__MoveTo__FIELD_NAME__response_message[] = "response_message";
static char modular_arm_interfaces__srv__MoveTo__FIELD_NAME__event_message[] = "event_message";

static rosidl_runtime_c__type_description__Field modular_arm_interfaces__srv__MoveTo__FIELDS[] = {
  {
    {modular_arm_interfaces__srv__MoveTo__FIELD_NAME__request_message, 15, 15},
    {
      rosidl_runtime_c__type_description__FieldType__FIELD_TYPE_NESTED_TYPE,
      0,
      0,
      {modular_arm_interfaces__srv__MoveTo_Request__TYPE_NAME, 41, 41},
    },
    {NULL, 0, 0},
  },
  {
    {modular_arm_interfaces__srv__MoveTo__FIELD_NAME__response_message, 16, 16},
    {
      rosidl_runtime_c__type_description__FieldType__FIELD_TYPE_NESTED_TYPE,
      0,
      0,
      {modular_arm_interfaces__srv__MoveTo_Response__TYPE_NAME, 42, 42},
    },
    {NULL, 0, 0},
  },
  {
    {modular_arm_interfaces__srv__MoveTo__FIELD_NAME__event_message, 13, 13},
    {
      rosidl_runtime_c__type_description__FieldType__FIELD_TYPE_NESTED_TYPE,
      0,
      0,
      {modular_arm_interfaces__srv__MoveTo_Event__TYPE_NAME, 39, 39},
    },
    {NULL, 0, 0},
  },
};

static rosidl_runtime_c__type_description__IndividualTypeDescription modular_arm_interfaces__srv__MoveTo__REFERENCED_TYPE_DESCRIPTIONS[] = {
  {
    {builtin_interfaces__msg__Time__TYPE_NAME, 27, 27},
    {NULL, 0, 0},
  },
  {
    {modular_arm_interfaces__srv__MoveTo_Event__TYPE_NAME, 39, 39},
    {NULL, 0, 0},
  },
  {
    {modular_arm_interfaces__srv__MoveTo_Request__TYPE_NAME, 41, 41},
    {NULL, 0, 0},
  },
  {
    {modular_arm_interfaces__srv__MoveTo_Response__TYPE_NAME, 42, 42},
    {NULL, 0, 0},
  },
  {
    {service_msgs__msg__ServiceEventInfo__TYPE_NAME, 33, 33},
    {NULL, 0, 0},
  },
};

const rosidl_runtime_c__type_description__TypeDescription *
modular_arm_interfaces__srv__MoveTo__get_type_description(
  const rosidl_service_type_support_t * type_support)
{
  (void)type_support;
  static bool constructed = false;
  static const rosidl_runtime_c__type_description__TypeDescription description = {
    {
      {modular_arm_interfaces__srv__MoveTo__TYPE_NAME, 33, 33},
      {modular_arm_interfaces__srv__MoveTo__FIELDS, 3, 3},
    },
    {modular_arm_interfaces__srv__MoveTo__REFERENCED_TYPE_DESCRIPTIONS, 5, 5},
  };
  if (!constructed) {
    assert(0 == memcmp(&builtin_interfaces__msg__Time__EXPECTED_HASH, builtin_interfaces__msg__Time__get_type_hash(NULL), sizeof(rosidl_type_hash_t)));
    description.referenced_type_descriptions.data[0].fields = builtin_interfaces__msg__Time__get_type_description(NULL)->type_description.fields;
    description.referenced_type_descriptions.data[1].fields = modular_arm_interfaces__srv__MoveTo_Event__get_type_description(NULL)->type_description.fields;
    description.referenced_type_descriptions.data[2].fields = modular_arm_interfaces__srv__MoveTo_Request__get_type_description(NULL)->type_description.fields;
    description.referenced_type_descriptions.data[3].fields = modular_arm_interfaces__srv__MoveTo_Response__get_type_description(NULL)->type_description.fields;
    assert(0 == memcmp(&service_msgs__msg__ServiceEventInfo__EXPECTED_HASH, service_msgs__msg__ServiceEventInfo__get_type_hash(NULL), sizeof(rosidl_type_hash_t)));
    description.referenced_type_descriptions.data[4].fields = service_msgs__msg__ServiceEventInfo__get_type_description(NULL)->type_description.fields;
    constructed = true;
  }
  return &description;
}
// Define type names, field names, and default values
static char modular_arm_interfaces__srv__MoveTo_Request__FIELD_NAME__x[] = "x";
static char modular_arm_interfaces__srv__MoveTo_Request__FIELD_NAME__y[] = "y";
static char modular_arm_interfaces__srv__MoveTo_Request__FIELD_NAME__z[] = "z";
static char modular_arm_interfaces__srv__MoveTo_Request__FIELD_NAME__pitch[] = "pitch";
static char modular_arm_interfaces__srv__MoveTo_Request__FIELD_NAME__elbow[] = "elbow";
static char modular_arm_interfaces__srv__MoveTo_Request__FIELD_NAME__duration_sec[] = "duration_sec";

static rosidl_runtime_c__type_description__Field modular_arm_interfaces__srv__MoveTo_Request__FIELDS[] = {
  {
    {modular_arm_interfaces__srv__MoveTo_Request__FIELD_NAME__x, 1, 1},
    {
      rosidl_runtime_c__type_description__FieldType__FIELD_TYPE_DOUBLE,
      0,
      0,
      {NULL, 0, 0},
    },
    {NULL, 0, 0},
  },
  {
    {modular_arm_interfaces__srv__MoveTo_Request__FIELD_NAME__y, 1, 1},
    {
      rosidl_runtime_c__type_description__FieldType__FIELD_TYPE_DOUBLE,
      0,
      0,
      {NULL, 0, 0},
    },
    {NULL, 0, 0},
  },
  {
    {modular_arm_interfaces__srv__MoveTo_Request__FIELD_NAME__z, 1, 1},
    {
      rosidl_runtime_c__type_description__FieldType__FIELD_TYPE_DOUBLE,
      0,
      0,
      {NULL, 0, 0},
    },
    {NULL, 0, 0},
  },
  {
    {modular_arm_interfaces__srv__MoveTo_Request__FIELD_NAME__pitch, 5, 5},
    {
      rosidl_runtime_c__type_description__FieldType__FIELD_TYPE_DOUBLE,
      0,
      0,
      {NULL, 0, 0},
    },
    {NULL, 0, 0},
  },
  {
    {modular_arm_interfaces__srv__MoveTo_Request__FIELD_NAME__elbow, 5, 5},
    {
      rosidl_runtime_c__type_description__FieldType__FIELD_TYPE_STRING,
      0,
      0,
      {NULL, 0, 0},
    },
    {NULL, 0, 0},
  },
  {
    {modular_arm_interfaces__srv__MoveTo_Request__FIELD_NAME__duration_sec, 12, 12},
    {
      rosidl_runtime_c__type_description__FieldType__FIELD_TYPE_DOUBLE,
      0,
      0,
      {NULL, 0, 0},
    },
    {NULL, 0, 0},
  },
};

const rosidl_runtime_c__type_description__TypeDescription *
modular_arm_interfaces__srv__MoveTo_Request__get_type_description(
  const rosidl_message_type_support_t * type_support)
{
  (void)type_support;
  static bool constructed = false;
  static const rosidl_runtime_c__type_description__TypeDescription description = {
    {
      {modular_arm_interfaces__srv__MoveTo_Request__TYPE_NAME, 41, 41},
      {modular_arm_interfaces__srv__MoveTo_Request__FIELDS, 6, 6},
    },
    {NULL, 0, 0},
  };
  if (!constructed) {
    constructed = true;
  }
  return &description;
}
// Define type names, field names, and default values
static char modular_arm_interfaces__srv__MoveTo_Response__FIELD_NAME__success[] = "success";
static char modular_arm_interfaces__srv__MoveTo_Response__FIELD_NAME__message[] = "message";
static char modular_arm_interfaces__srv__MoveTo_Response__FIELD_NAME__joint_angles[] = "joint_angles";

static rosidl_runtime_c__type_description__Field modular_arm_interfaces__srv__MoveTo_Response__FIELDS[] = {
  {
    {modular_arm_interfaces__srv__MoveTo_Response__FIELD_NAME__success, 7, 7},
    {
      rosidl_runtime_c__type_description__FieldType__FIELD_TYPE_BOOLEAN,
      0,
      0,
      {NULL, 0, 0},
    },
    {NULL, 0, 0},
  },
  {
    {modular_arm_interfaces__srv__MoveTo_Response__FIELD_NAME__message, 7, 7},
    {
      rosidl_runtime_c__type_description__FieldType__FIELD_TYPE_STRING,
      0,
      0,
      {NULL, 0, 0},
    },
    {NULL, 0, 0},
  },
  {
    {modular_arm_interfaces__srv__MoveTo_Response__FIELD_NAME__joint_angles, 12, 12},
    {
      rosidl_runtime_c__type_description__FieldType__FIELD_TYPE_DOUBLE_UNBOUNDED_SEQUENCE,
      0,
      0,
      {NULL, 0, 0},
    },
    {NULL, 0, 0},
  },
};

const rosidl_runtime_c__type_description__TypeDescription *
modular_arm_interfaces__srv__MoveTo_Response__get_type_description(
  const rosidl_message_type_support_t * type_support)
{
  (void)type_support;
  static bool constructed = false;
  static const rosidl_runtime_c__type_description__TypeDescription description = {
    {
      {modular_arm_interfaces__srv__MoveTo_Response__TYPE_NAME, 42, 42},
      {modular_arm_interfaces__srv__MoveTo_Response__FIELDS, 3, 3},
    },
    {NULL, 0, 0},
  };
  if (!constructed) {
    constructed = true;
  }
  return &description;
}
// Define type names, field names, and default values
static char modular_arm_interfaces__srv__MoveTo_Event__FIELD_NAME__info[] = "info";
static char modular_arm_interfaces__srv__MoveTo_Event__FIELD_NAME__request[] = "request";
static char modular_arm_interfaces__srv__MoveTo_Event__FIELD_NAME__response[] = "response";

static rosidl_runtime_c__type_description__Field modular_arm_interfaces__srv__MoveTo_Event__FIELDS[] = {
  {
    {modular_arm_interfaces__srv__MoveTo_Event__FIELD_NAME__info, 4, 4},
    {
      rosidl_runtime_c__type_description__FieldType__FIELD_TYPE_NESTED_TYPE,
      0,
      0,
      {service_msgs__msg__ServiceEventInfo__TYPE_NAME, 33, 33},
    },
    {NULL, 0, 0},
  },
  {
    {modular_arm_interfaces__srv__MoveTo_Event__FIELD_NAME__request, 7, 7},
    {
      rosidl_runtime_c__type_description__FieldType__FIELD_TYPE_NESTED_TYPE_BOUNDED_SEQUENCE,
      1,
      0,
      {modular_arm_interfaces__srv__MoveTo_Request__TYPE_NAME, 41, 41},
    },
    {NULL, 0, 0},
  },
  {
    {modular_arm_interfaces__srv__MoveTo_Event__FIELD_NAME__response, 8, 8},
    {
      rosidl_runtime_c__type_description__FieldType__FIELD_TYPE_NESTED_TYPE_BOUNDED_SEQUENCE,
      1,
      0,
      {modular_arm_interfaces__srv__MoveTo_Response__TYPE_NAME, 42, 42},
    },
    {NULL, 0, 0},
  },
};

static rosidl_runtime_c__type_description__IndividualTypeDescription modular_arm_interfaces__srv__MoveTo_Event__REFERENCED_TYPE_DESCRIPTIONS[] = {
  {
    {builtin_interfaces__msg__Time__TYPE_NAME, 27, 27},
    {NULL, 0, 0},
  },
  {
    {modular_arm_interfaces__srv__MoveTo_Request__TYPE_NAME, 41, 41},
    {NULL, 0, 0},
  },
  {
    {modular_arm_interfaces__srv__MoveTo_Response__TYPE_NAME, 42, 42},
    {NULL, 0, 0},
  },
  {
    {service_msgs__msg__ServiceEventInfo__TYPE_NAME, 33, 33},
    {NULL, 0, 0},
  },
};

const rosidl_runtime_c__type_description__TypeDescription *
modular_arm_interfaces__srv__MoveTo_Event__get_type_description(
  const rosidl_message_type_support_t * type_support)
{
  (void)type_support;
  static bool constructed = false;
  static const rosidl_runtime_c__type_description__TypeDescription description = {
    {
      {modular_arm_interfaces__srv__MoveTo_Event__TYPE_NAME, 39, 39},
      {modular_arm_interfaces__srv__MoveTo_Event__FIELDS, 3, 3},
    },
    {modular_arm_interfaces__srv__MoveTo_Event__REFERENCED_TYPE_DESCRIPTIONS, 4, 4},
  };
  if (!constructed) {
    assert(0 == memcmp(&builtin_interfaces__msg__Time__EXPECTED_HASH, builtin_interfaces__msg__Time__get_type_hash(NULL), sizeof(rosidl_type_hash_t)));
    description.referenced_type_descriptions.data[0].fields = builtin_interfaces__msg__Time__get_type_description(NULL)->type_description.fields;
    description.referenced_type_descriptions.data[1].fields = modular_arm_interfaces__srv__MoveTo_Request__get_type_description(NULL)->type_description.fields;
    description.referenced_type_descriptions.data[2].fields = modular_arm_interfaces__srv__MoveTo_Response__get_type_description(NULL)->type_description.fields;
    assert(0 == memcmp(&service_msgs__msg__ServiceEventInfo__EXPECTED_HASH, service_msgs__msg__ServiceEventInfo__get_type_hash(NULL), sizeof(rosidl_type_hash_t)));
    description.referenced_type_descriptions.data[3].fields = service_msgs__msg__ServiceEventInfo__get_type_description(NULL)->type_description.fields;
    constructed = true;
  }
  return &description;
}

static char toplevel_type_raw_source[] =
  "# Request: target end-effector position in the arm base frame (meters),\n"
  "# desired end-effector pitch (radians, 0 = horizontal, -pi/2 = pointing straight down),\n"
  "# and elbow configuration.\n"
  "float64 x\n"
  "float64 y\n"
  "float64 z\n"
  "float64 pitch\n"
  "string elbow            # \"up\" or \"down\"\n"
  "float64 duration_sec    # time to execute the trajectory, e.g. 2.0\n"
  "---\n"
  "bool success\n"
  "string message\n"
  "float64[] joint_angles  # [theta1, theta2, theta3, theta4] actually commanded, radians";

static char srv_encoding[] = "srv";
static char implicit_encoding[] = "implicit";

// Define all individual source functions

const rosidl_runtime_c__type_description__TypeSource *
modular_arm_interfaces__srv__MoveTo__get_individual_type_description_source(
  const rosidl_service_type_support_t * type_support)
{
  (void)type_support;
  static const rosidl_runtime_c__type_description__TypeSource source = {
    {modular_arm_interfaces__srv__MoveTo__TYPE_NAME, 33, 33},
    {srv_encoding, 3, 3},
    {toplevel_type_raw_source, 458, 458},
  };
  return &source;
}

const rosidl_runtime_c__type_description__TypeSource *
modular_arm_interfaces__srv__MoveTo_Request__get_individual_type_description_source(
  const rosidl_message_type_support_t * type_support)
{
  (void)type_support;
  static const rosidl_runtime_c__type_description__TypeSource source = {
    {modular_arm_interfaces__srv__MoveTo_Request__TYPE_NAME, 41, 41},
    {implicit_encoding, 8, 8},
    {NULL, 0, 0},
  };
  return &source;
}

const rosidl_runtime_c__type_description__TypeSource *
modular_arm_interfaces__srv__MoveTo_Response__get_individual_type_description_source(
  const rosidl_message_type_support_t * type_support)
{
  (void)type_support;
  static const rosidl_runtime_c__type_description__TypeSource source = {
    {modular_arm_interfaces__srv__MoveTo_Response__TYPE_NAME, 42, 42},
    {implicit_encoding, 8, 8},
    {NULL, 0, 0},
  };
  return &source;
}

const rosidl_runtime_c__type_description__TypeSource *
modular_arm_interfaces__srv__MoveTo_Event__get_individual_type_description_source(
  const rosidl_message_type_support_t * type_support)
{
  (void)type_support;
  static const rosidl_runtime_c__type_description__TypeSource source = {
    {modular_arm_interfaces__srv__MoveTo_Event__TYPE_NAME, 39, 39},
    {implicit_encoding, 8, 8},
    {NULL, 0, 0},
  };
  return &source;
}

const rosidl_runtime_c__type_description__TypeSource__Sequence *
modular_arm_interfaces__srv__MoveTo__get_type_description_sources(
  const rosidl_service_type_support_t * type_support)
{
  (void)type_support;
  static rosidl_runtime_c__type_description__TypeSource sources[6];
  static const rosidl_runtime_c__type_description__TypeSource__Sequence source_sequence = {sources, 6, 6};
  static bool constructed = false;
  if (!constructed) {
    sources[0] = *modular_arm_interfaces__srv__MoveTo__get_individual_type_description_source(NULL),
    sources[1] = *builtin_interfaces__msg__Time__get_individual_type_description_source(NULL);
    sources[2] = *modular_arm_interfaces__srv__MoveTo_Event__get_individual_type_description_source(NULL);
    sources[3] = *modular_arm_interfaces__srv__MoveTo_Request__get_individual_type_description_source(NULL);
    sources[4] = *modular_arm_interfaces__srv__MoveTo_Response__get_individual_type_description_source(NULL);
    sources[5] = *service_msgs__msg__ServiceEventInfo__get_individual_type_description_source(NULL);
    constructed = true;
  }
  return &source_sequence;
}

const rosidl_runtime_c__type_description__TypeSource__Sequence *
modular_arm_interfaces__srv__MoveTo_Request__get_type_description_sources(
  const rosidl_message_type_support_t * type_support)
{
  (void)type_support;
  static rosidl_runtime_c__type_description__TypeSource sources[1];
  static const rosidl_runtime_c__type_description__TypeSource__Sequence source_sequence = {sources, 1, 1};
  static bool constructed = false;
  if (!constructed) {
    sources[0] = *modular_arm_interfaces__srv__MoveTo_Request__get_individual_type_description_source(NULL),
    constructed = true;
  }
  return &source_sequence;
}

const rosidl_runtime_c__type_description__TypeSource__Sequence *
modular_arm_interfaces__srv__MoveTo_Response__get_type_description_sources(
  const rosidl_message_type_support_t * type_support)
{
  (void)type_support;
  static rosidl_runtime_c__type_description__TypeSource sources[1];
  static const rosidl_runtime_c__type_description__TypeSource__Sequence source_sequence = {sources, 1, 1};
  static bool constructed = false;
  if (!constructed) {
    sources[0] = *modular_arm_interfaces__srv__MoveTo_Response__get_individual_type_description_source(NULL),
    constructed = true;
  }
  return &source_sequence;
}

const rosidl_runtime_c__type_description__TypeSource__Sequence *
modular_arm_interfaces__srv__MoveTo_Event__get_type_description_sources(
  const rosidl_message_type_support_t * type_support)
{
  (void)type_support;
  static rosidl_runtime_c__type_description__TypeSource sources[5];
  static const rosidl_runtime_c__type_description__TypeSource__Sequence source_sequence = {sources, 5, 5};
  static bool constructed = false;
  if (!constructed) {
    sources[0] = *modular_arm_interfaces__srv__MoveTo_Event__get_individual_type_description_source(NULL),
    sources[1] = *builtin_interfaces__msg__Time__get_individual_type_description_source(NULL);
    sources[2] = *modular_arm_interfaces__srv__MoveTo_Request__get_individual_type_description_source(NULL);
    sources[3] = *modular_arm_interfaces__srv__MoveTo_Response__get_individual_type_description_source(NULL);
    sources[4] = *service_msgs__msg__ServiceEventInfo__get_individual_type_description_source(NULL);
    constructed = true;
  }
  return &source_sequence;
}
