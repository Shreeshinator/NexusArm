// generated from rosidl_generator_cpp/resource/idl__builder.hpp.em
// with input from modular_arm_interfaces:srv/MoveTo.idl
// generated code does not contain a copyright notice

// IWYU pragma: private, include "modular_arm_interfaces/srv/move_to.hpp"


#ifndef MODULAR_ARM_INTERFACES__SRV__DETAIL__MOVE_TO__BUILDER_HPP_
#define MODULAR_ARM_INTERFACES__SRV__DETAIL__MOVE_TO__BUILDER_HPP_

#include <algorithm>
#include <utility>

#include "modular_arm_interfaces/srv/detail/move_to__struct.hpp"
#include "rosidl_runtime_cpp/message_initialization.hpp"


namespace modular_arm_interfaces
{

namespace srv
{

namespace builder
{

class Init_MoveTo_Request_duration_sec
{
public:
  explicit Init_MoveTo_Request_duration_sec(::modular_arm_interfaces::srv::MoveTo_Request & msg)
  : msg_(msg)
  {}
  ::modular_arm_interfaces::srv::MoveTo_Request duration_sec(::modular_arm_interfaces::srv::MoveTo_Request::_duration_sec_type arg)
  {
    msg_.duration_sec = std::move(arg);
    return std::move(msg_);
  }

private:
  ::modular_arm_interfaces::srv::MoveTo_Request msg_;
};

class Init_MoveTo_Request_elbow
{
public:
  explicit Init_MoveTo_Request_elbow(::modular_arm_interfaces::srv::MoveTo_Request & msg)
  : msg_(msg)
  {}
  Init_MoveTo_Request_duration_sec elbow(::modular_arm_interfaces::srv::MoveTo_Request::_elbow_type arg)
  {
    msg_.elbow = std::move(arg);
    return Init_MoveTo_Request_duration_sec(msg_);
  }

private:
  ::modular_arm_interfaces::srv::MoveTo_Request msg_;
};

class Init_MoveTo_Request_pitch
{
public:
  explicit Init_MoveTo_Request_pitch(::modular_arm_interfaces::srv::MoveTo_Request & msg)
  : msg_(msg)
  {}
  Init_MoveTo_Request_elbow pitch(::modular_arm_interfaces::srv::MoveTo_Request::_pitch_type arg)
  {
    msg_.pitch = std::move(arg);
    return Init_MoveTo_Request_elbow(msg_);
  }

private:
  ::modular_arm_interfaces::srv::MoveTo_Request msg_;
};

class Init_MoveTo_Request_z
{
public:
  explicit Init_MoveTo_Request_z(::modular_arm_interfaces::srv::MoveTo_Request & msg)
  : msg_(msg)
  {}
  Init_MoveTo_Request_pitch z(::modular_arm_interfaces::srv::MoveTo_Request::_z_type arg)
  {
    msg_.z = std::move(arg);
    return Init_MoveTo_Request_pitch(msg_);
  }

private:
  ::modular_arm_interfaces::srv::MoveTo_Request msg_;
};

class Init_MoveTo_Request_y
{
public:
  explicit Init_MoveTo_Request_y(::modular_arm_interfaces::srv::MoveTo_Request & msg)
  : msg_(msg)
  {}
  Init_MoveTo_Request_z y(::modular_arm_interfaces::srv::MoveTo_Request::_y_type arg)
  {
    msg_.y = std::move(arg);
    return Init_MoveTo_Request_z(msg_);
  }

private:
  ::modular_arm_interfaces::srv::MoveTo_Request msg_;
};

class Init_MoveTo_Request_x
{
public:
  Init_MoveTo_Request_x()
  : msg_(::rosidl_runtime_cpp::MessageInitialization::SKIP)
  {}
  Init_MoveTo_Request_y x(::modular_arm_interfaces::srv::MoveTo_Request::_x_type arg)
  {
    msg_.x = std::move(arg);
    return Init_MoveTo_Request_y(msg_);
  }

private:
  ::modular_arm_interfaces::srv::MoveTo_Request msg_;
};

}  // namespace builder

}  // namespace srv

template<typename MessageType>
auto build();

template<>
inline
auto build<::modular_arm_interfaces::srv::MoveTo_Request>()
{
  return modular_arm_interfaces::srv::builder::Init_MoveTo_Request_x();
}

}  // namespace modular_arm_interfaces


namespace modular_arm_interfaces
{

namespace srv
{

namespace builder
{

class Init_MoveTo_Response_joint_angles
{
public:
  explicit Init_MoveTo_Response_joint_angles(::modular_arm_interfaces::srv::MoveTo_Response & msg)
  : msg_(msg)
  {}
  ::modular_arm_interfaces::srv::MoveTo_Response joint_angles(::modular_arm_interfaces::srv::MoveTo_Response::_joint_angles_type arg)
  {
    msg_.joint_angles = std::move(arg);
    return std::move(msg_);
  }

private:
  ::modular_arm_interfaces::srv::MoveTo_Response msg_;
};

class Init_MoveTo_Response_message
{
public:
  explicit Init_MoveTo_Response_message(::modular_arm_interfaces::srv::MoveTo_Response & msg)
  : msg_(msg)
  {}
  Init_MoveTo_Response_joint_angles message(::modular_arm_interfaces::srv::MoveTo_Response::_message_type arg)
  {
    msg_.message = std::move(arg);
    return Init_MoveTo_Response_joint_angles(msg_);
  }

private:
  ::modular_arm_interfaces::srv::MoveTo_Response msg_;
};

class Init_MoveTo_Response_success
{
public:
  Init_MoveTo_Response_success()
  : msg_(::rosidl_runtime_cpp::MessageInitialization::SKIP)
  {}
  Init_MoveTo_Response_message success(::modular_arm_interfaces::srv::MoveTo_Response::_success_type arg)
  {
    msg_.success = std::move(arg);
    return Init_MoveTo_Response_message(msg_);
  }

private:
  ::modular_arm_interfaces::srv::MoveTo_Response msg_;
};

}  // namespace builder

}  // namespace srv

template<typename MessageType>
auto build();

template<>
inline
auto build<::modular_arm_interfaces::srv::MoveTo_Response>()
{
  return modular_arm_interfaces::srv::builder::Init_MoveTo_Response_success();
}

}  // namespace modular_arm_interfaces


namespace modular_arm_interfaces
{

namespace srv
{

namespace builder
{

class Init_MoveTo_Event_response
{
public:
  explicit Init_MoveTo_Event_response(::modular_arm_interfaces::srv::MoveTo_Event & msg)
  : msg_(msg)
  {}
  ::modular_arm_interfaces::srv::MoveTo_Event response(::modular_arm_interfaces::srv::MoveTo_Event::_response_type arg)
  {
    msg_.response = std::move(arg);
    return std::move(msg_);
  }

private:
  ::modular_arm_interfaces::srv::MoveTo_Event msg_;
};

class Init_MoveTo_Event_request
{
public:
  explicit Init_MoveTo_Event_request(::modular_arm_interfaces::srv::MoveTo_Event & msg)
  : msg_(msg)
  {}
  Init_MoveTo_Event_response request(::modular_arm_interfaces::srv::MoveTo_Event::_request_type arg)
  {
    msg_.request = std::move(arg);
    return Init_MoveTo_Event_response(msg_);
  }

private:
  ::modular_arm_interfaces::srv::MoveTo_Event msg_;
};

class Init_MoveTo_Event_info
{
public:
  Init_MoveTo_Event_info()
  : msg_(::rosidl_runtime_cpp::MessageInitialization::SKIP)
  {}
  Init_MoveTo_Event_request info(::modular_arm_interfaces::srv::MoveTo_Event::_info_type arg)
  {
    msg_.info = std::move(arg);
    return Init_MoveTo_Event_request(msg_);
  }

private:
  ::modular_arm_interfaces::srv::MoveTo_Event msg_;
};

}  // namespace builder

}  // namespace srv

template<typename MessageType>
auto build();

template<>
inline
auto build<::modular_arm_interfaces::srv::MoveTo_Event>()
{
  return modular_arm_interfaces::srv::builder::Init_MoveTo_Event_info();
}

}  // namespace modular_arm_interfaces

#endif  // MODULAR_ARM_INTERFACES__SRV__DETAIL__MOVE_TO__BUILDER_HPP_
