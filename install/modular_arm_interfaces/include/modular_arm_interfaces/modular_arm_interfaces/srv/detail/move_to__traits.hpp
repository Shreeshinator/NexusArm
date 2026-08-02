// generated from rosidl_generator_cpp/resource/idl__traits.hpp.em
// with input from modular_arm_interfaces:srv/MoveTo.idl
// generated code does not contain a copyright notice

// IWYU pragma: private, include "modular_arm_interfaces/srv/move_to.hpp"


#ifndef MODULAR_ARM_INTERFACES__SRV__DETAIL__MOVE_TO__TRAITS_HPP_
#define MODULAR_ARM_INTERFACES__SRV__DETAIL__MOVE_TO__TRAITS_HPP_

#include <stdint.h>

#include <sstream>
#include <string>
#include <type_traits>

#include "modular_arm_interfaces/srv/detail/move_to__struct.hpp"
#include "rosidl_runtime_cpp/traits.hpp"

namespace modular_arm_interfaces
{

namespace srv
{

inline void to_flow_style_yaml(
  const MoveTo_Request & msg,
  std::ostream & out)
{
  out << "{";
  // member: x
  {
    out << "x: ";
    rosidl_generator_traits::value_to_yaml(msg.x, out);
    out << ", ";
  }

  // member: y
  {
    out << "y: ";
    rosidl_generator_traits::value_to_yaml(msg.y, out);
    out << ", ";
  }

  // member: z
  {
    out << "z: ";
    rosidl_generator_traits::value_to_yaml(msg.z, out);
    out << ", ";
  }

  // member: pitch
  {
    out << "pitch: ";
    rosidl_generator_traits::value_to_yaml(msg.pitch, out);
    out << ", ";
  }

  // member: elbow
  {
    out << "elbow: ";
    rosidl_generator_traits::value_to_yaml(msg.elbow, out);
    out << ", ";
  }

  // member: duration_sec
  {
    out << "duration_sec: ";
    rosidl_generator_traits::value_to_yaml(msg.duration_sec, out);
  }
  out << "}";
}  // NOLINT(readability/fn_size)

inline void to_block_style_yaml(
  const MoveTo_Request & msg,
  std::ostream & out, size_t indentation = 0)
{
  // member: x
  {
    if (indentation > 0) {
      out << std::string(indentation, ' ');
    }
    out << "x: ";
    rosidl_generator_traits::value_to_yaml(msg.x, out);
    out << "\n";
  }

  // member: y
  {
    if (indentation > 0) {
      out << std::string(indentation, ' ');
    }
    out << "y: ";
    rosidl_generator_traits::value_to_yaml(msg.y, out);
    out << "\n";
  }

  // member: z
  {
    if (indentation > 0) {
      out << std::string(indentation, ' ');
    }
    out << "z: ";
    rosidl_generator_traits::value_to_yaml(msg.z, out);
    out << "\n";
  }

  // member: pitch
  {
    if (indentation > 0) {
      out << std::string(indentation, ' ');
    }
    out << "pitch: ";
    rosidl_generator_traits::value_to_yaml(msg.pitch, out);
    out << "\n";
  }

  // member: elbow
  {
    if (indentation > 0) {
      out << std::string(indentation, ' ');
    }
    out << "elbow: ";
    rosidl_generator_traits::value_to_yaml(msg.elbow, out);
    out << "\n";
  }

  // member: duration_sec
  {
    if (indentation > 0) {
      out << std::string(indentation, ' ');
    }
    out << "duration_sec: ";
    rosidl_generator_traits::value_to_yaml(msg.duration_sec, out);
    out << "\n";
  }
}  // NOLINT(readability/fn_size)

inline std::string to_yaml(const MoveTo_Request & msg, bool use_flow_style = false)
{
  std::ostringstream out;
  if (use_flow_style) {
    to_flow_style_yaml(msg, out);
  } else {
    to_block_style_yaml(msg, out);
  }
  return out.str();
}

}  // namespace srv

}  // namespace modular_arm_interfaces

namespace rosidl_generator_traits
{

[[deprecated("use modular_arm_interfaces::srv::to_block_style_yaml() instead")]]
inline void to_yaml(
  const modular_arm_interfaces::srv::MoveTo_Request & msg,
  std::ostream & out, size_t indentation = 0)
{
  modular_arm_interfaces::srv::to_block_style_yaml(msg, out, indentation);
}

[[deprecated("use modular_arm_interfaces::srv::to_yaml() instead")]]
inline std::string to_yaml(const modular_arm_interfaces::srv::MoveTo_Request & msg)
{
  return modular_arm_interfaces::srv::to_yaml(msg);
}

template<>
inline const char * data_type<modular_arm_interfaces::srv::MoveTo_Request>()
{
  return "modular_arm_interfaces::srv::MoveTo_Request";
}

template<>
inline const char * name<modular_arm_interfaces::srv::MoveTo_Request>()
{
  return "modular_arm_interfaces/srv/MoveTo_Request";
}

template<>
struct has_fixed_size<modular_arm_interfaces::srv::MoveTo_Request>
  : std::integral_constant<bool, false> {};

template<>
struct has_bounded_size<modular_arm_interfaces::srv::MoveTo_Request>
  : std::integral_constant<bool, false> {};

template<>
struct is_message<modular_arm_interfaces::srv::MoveTo_Request>
  : std::true_type {};

}  // namespace rosidl_generator_traits

namespace modular_arm_interfaces
{

namespace srv
{

inline void to_flow_style_yaml(
  const MoveTo_Response & msg,
  std::ostream & out)
{
  out << "{";
  // member: success
  {
    out << "success: ";
    rosidl_generator_traits::value_to_yaml(msg.success, out);
    out << ", ";
  }

  // member: message
  {
    out << "message: ";
    rosidl_generator_traits::value_to_yaml(msg.message, out);
    out << ", ";
  }

  // member: joint_angles
  {
    if (msg.joint_angles.size() == 0) {
      out << "joint_angles: []";
    } else {
      out << "joint_angles: [";
      size_t pending_items = msg.joint_angles.size();
      for (auto item : msg.joint_angles) {
        rosidl_generator_traits::value_to_yaml(item, out);
        if (--pending_items > 0) {
          out << ", ";
        }
      }
      out << "]";
    }
  }
  out << "}";
}  // NOLINT(readability/fn_size)

inline void to_block_style_yaml(
  const MoveTo_Response & msg,
  std::ostream & out, size_t indentation = 0)
{
  // member: success
  {
    if (indentation > 0) {
      out << std::string(indentation, ' ');
    }
    out << "success: ";
    rosidl_generator_traits::value_to_yaml(msg.success, out);
    out << "\n";
  }

  // member: message
  {
    if (indentation > 0) {
      out << std::string(indentation, ' ');
    }
    out << "message: ";
    rosidl_generator_traits::value_to_yaml(msg.message, out);
    out << "\n";
  }

  // member: joint_angles
  {
    if (indentation > 0) {
      out << std::string(indentation, ' ');
    }
    if (msg.joint_angles.size() == 0) {
      out << "joint_angles: []\n";
    } else {
      out << "joint_angles:\n";
      for (auto item : msg.joint_angles) {
        if (indentation > 0) {
          out << std::string(indentation, ' ');
        }
        out << "- ";
        rosidl_generator_traits::value_to_yaml(item, out);
        out << "\n";
      }
    }
  }
}  // NOLINT(readability/fn_size)

inline std::string to_yaml(const MoveTo_Response & msg, bool use_flow_style = false)
{
  std::ostringstream out;
  if (use_flow_style) {
    to_flow_style_yaml(msg, out);
  } else {
    to_block_style_yaml(msg, out);
  }
  return out.str();
}

}  // namespace srv

}  // namespace modular_arm_interfaces

namespace rosidl_generator_traits
{

[[deprecated("use modular_arm_interfaces::srv::to_block_style_yaml() instead")]]
inline void to_yaml(
  const modular_arm_interfaces::srv::MoveTo_Response & msg,
  std::ostream & out, size_t indentation = 0)
{
  modular_arm_interfaces::srv::to_block_style_yaml(msg, out, indentation);
}

[[deprecated("use modular_arm_interfaces::srv::to_yaml() instead")]]
inline std::string to_yaml(const modular_arm_interfaces::srv::MoveTo_Response & msg)
{
  return modular_arm_interfaces::srv::to_yaml(msg);
}

template<>
inline const char * data_type<modular_arm_interfaces::srv::MoveTo_Response>()
{
  return "modular_arm_interfaces::srv::MoveTo_Response";
}

template<>
inline const char * name<modular_arm_interfaces::srv::MoveTo_Response>()
{
  return "modular_arm_interfaces/srv/MoveTo_Response";
}

template<>
struct has_fixed_size<modular_arm_interfaces::srv::MoveTo_Response>
  : std::integral_constant<bool, false> {};

template<>
struct has_bounded_size<modular_arm_interfaces::srv::MoveTo_Response>
  : std::integral_constant<bool, false> {};

template<>
struct is_message<modular_arm_interfaces::srv::MoveTo_Response>
  : std::true_type {};

}  // namespace rosidl_generator_traits

// Include directives for member types
// Member 'info'
#include "service_msgs/msg/detail/service_event_info__traits.hpp"

namespace modular_arm_interfaces
{

namespace srv
{

inline void to_flow_style_yaml(
  const MoveTo_Event & msg,
  std::ostream & out)
{
  out << "{";
  // member: info
  {
    out << "info: ";
    to_flow_style_yaml(msg.info, out);
    out << ", ";
  }

  // member: request
  {
    if (msg.request.size() == 0) {
      out << "request: []";
    } else {
      out << "request: [";
      size_t pending_items = msg.request.size();
      for (auto item : msg.request) {
        to_flow_style_yaml(item, out);
        if (--pending_items > 0) {
          out << ", ";
        }
      }
      out << "]";
    }
    out << ", ";
  }

  // member: response
  {
    if (msg.response.size() == 0) {
      out << "response: []";
    } else {
      out << "response: [";
      size_t pending_items = msg.response.size();
      for (auto item : msg.response) {
        to_flow_style_yaml(item, out);
        if (--pending_items > 0) {
          out << ", ";
        }
      }
      out << "]";
    }
  }
  out << "}";
}  // NOLINT(readability/fn_size)

inline void to_block_style_yaml(
  const MoveTo_Event & msg,
  std::ostream & out, size_t indentation = 0)
{
  // member: info
  {
    if (indentation > 0) {
      out << std::string(indentation, ' ');
    }
    out << "info:\n";
    to_block_style_yaml(msg.info, out, indentation + 2);
  }

  // member: request
  {
    if (indentation > 0) {
      out << std::string(indentation, ' ');
    }
    if (msg.request.size() == 0) {
      out << "request: []\n";
    } else {
      out << "request:\n";
      for (auto item : msg.request) {
        if (indentation > 0) {
          out << std::string(indentation, ' ');
        }
        out << "-\n";
        to_block_style_yaml(item, out, indentation + 2);
      }
    }
  }

  // member: response
  {
    if (indentation > 0) {
      out << std::string(indentation, ' ');
    }
    if (msg.response.size() == 0) {
      out << "response: []\n";
    } else {
      out << "response:\n";
      for (auto item : msg.response) {
        if (indentation > 0) {
          out << std::string(indentation, ' ');
        }
        out << "-\n";
        to_block_style_yaml(item, out, indentation + 2);
      }
    }
  }
}  // NOLINT(readability/fn_size)

inline std::string to_yaml(const MoveTo_Event & msg, bool use_flow_style = false)
{
  std::ostringstream out;
  if (use_flow_style) {
    to_flow_style_yaml(msg, out);
  } else {
    to_block_style_yaml(msg, out);
  }
  return out.str();
}

}  // namespace srv

}  // namespace modular_arm_interfaces

namespace rosidl_generator_traits
{

[[deprecated("use modular_arm_interfaces::srv::to_block_style_yaml() instead")]]
inline void to_yaml(
  const modular_arm_interfaces::srv::MoveTo_Event & msg,
  std::ostream & out, size_t indentation = 0)
{
  modular_arm_interfaces::srv::to_block_style_yaml(msg, out, indentation);
}

[[deprecated("use modular_arm_interfaces::srv::to_yaml() instead")]]
inline std::string to_yaml(const modular_arm_interfaces::srv::MoveTo_Event & msg)
{
  return modular_arm_interfaces::srv::to_yaml(msg);
}

template<>
inline const char * data_type<modular_arm_interfaces::srv::MoveTo_Event>()
{
  return "modular_arm_interfaces::srv::MoveTo_Event";
}

template<>
inline const char * name<modular_arm_interfaces::srv::MoveTo_Event>()
{
  return "modular_arm_interfaces/srv/MoveTo_Event";
}

template<>
struct has_fixed_size<modular_arm_interfaces::srv::MoveTo_Event>
  : std::integral_constant<bool, false> {};

template<>
struct has_bounded_size<modular_arm_interfaces::srv::MoveTo_Event>
  : std::integral_constant<bool, has_bounded_size<modular_arm_interfaces::srv::MoveTo_Request>::value && has_bounded_size<modular_arm_interfaces::srv::MoveTo_Response>::value && has_bounded_size<service_msgs::msg::ServiceEventInfo>::value> {};

template<>
struct is_message<modular_arm_interfaces::srv::MoveTo_Event>
  : std::true_type {};

}  // namespace rosidl_generator_traits

namespace rosidl_generator_traits
{

template<>
inline const char * data_type<modular_arm_interfaces::srv::MoveTo>()
{
  return "modular_arm_interfaces::srv::MoveTo";
}

template<>
inline const char * name<modular_arm_interfaces::srv::MoveTo>()
{
  return "modular_arm_interfaces/srv/MoveTo";
}

template<>
struct has_fixed_size<modular_arm_interfaces::srv::MoveTo>
  : std::integral_constant<
    bool,
    has_fixed_size<modular_arm_interfaces::srv::MoveTo_Request>::value &&
    has_fixed_size<modular_arm_interfaces::srv::MoveTo_Response>::value
  >
{
};

template<>
struct has_bounded_size<modular_arm_interfaces::srv::MoveTo>
  : std::integral_constant<
    bool,
    has_bounded_size<modular_arm_interfaces::srv::MoveTo_Request>::value &&
    has_bounded_size<modular_arm_interfaces::srv::MoveTo_Response>::value
  >
{
};

template<>
struct is_service<modular_arm_interfaces::srv::MoveTo>
  : std::true_type
{
};

template<>
struct is_service_request<modular_arm_interfaces::srv::MoveTo_Request>
  : std::true_type
{
};

template<>
struct is_service_response<modular_arm_interfaces::srv::MoveTo_Response>
  : std::true_type
{
};

}  // namespace rosidl_generator_traits

#endif  // MODULAR_ARM_INTERFACES__SRV__DETAIL__MOVE_TO__TRAITS_HPP_
