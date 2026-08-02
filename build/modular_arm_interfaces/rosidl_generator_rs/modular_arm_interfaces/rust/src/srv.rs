#[cfg(feature = "serde")]
use serde::{Deserialize, Serialize};




// Corresponds to modular_arm_interfaces__srv__MoveTo_Request

// This struct is not documented.
#[allow(missing_docs)]

#[allow(non_camel_case_types)]
#[cfg_attr(feature = "serde", derive(Deserialize, Serialize))]
#[derive(Clone, Debug, PartialEq, PartialOrd)]
pub struct MoveTo_Request {

    // This member is not documented.
    #[allow(missing_docs)]
    pub x: f64,


    // This member is not documented.
    #[allow(missing_docs)]
    pub y: f64,


    // This member is not documented.
    #[allow(missing_docs)]
    pub z: f64,


    // This member is not documented.
    #[allow(missing_docs)]
    pub pitch: f64,

    /// "up" or "down"
    pub elbow: std::string::String,

    /// time to execute the trajectory, e.g. 2.0
    pub duration_sec: f64,

}



impl Default for MoveTo_Request {
  fn default() -> Self {
    <Self as rosidl_runtime_rs::Message>::from_rmw_message(super::srv::rmw::MoveTo_Request::default())
  }
}

impl rosidl_runtime_rs::Message for MoveTo_Request {
  type RmwMsg = super::srv::rmw::MoveTo_Request;

  fn into_rmw_message(msg_cow: std::borrow::Cow<'_, Self>) -> std::borrow::Cow<'_, Self::RmwMsg> {
    match msg_cow {
      std::borrow::Cow::Owned(msg) => std::borrow::Cow::Owned(Self::RmwMsg {
        x: msg.x,
        y: msg.y,
        z: msg.z,
        pitch: msg.pitch,
        elbow: msg.elbow.as_str().into(),
        duration_sec: msg.duration_sec,
      }),
      std::borrow::Cow::Borrowed(msg) => std::borrow::Cow::Owned(Self::RmwMsg {
      x: msg.x,
      y: msg.y,
      z: msg.z,
      pitch: msg.pitch,
        elbow: msg.elbow.as_str().into(),
      duration_sec: msg.duration_sec,
      })
    }
  }

  fn from_rmw_message(msg: Self::RmwMsg) -> Self {
    Self {
      x: msg.x,
      y: msg.y,
      z: msg.z,
      pitch: msg.pitch,
      elbow: msg.elbow.to_string(),
      duration_sec: msg.duration_sec,
    }
  }
}


// Corresponds to modular_arm_interfaces__srv__MoveTo_Response

// This struct is not documented.
#[allow(missing_docs)]

#[allow(non_camel_case_types)]
#[cfg_attr(feature = "serde", derive(Deserialize, Serialize))]
#[derive(Clone, Debug, PartialEq, PartialOrd)]
pub struct MoveTo_Response {

    // This member is not documented.
    #[allow(missing_docs)]
    pub success: bool,


    // This member is not documented.
    #[allow(missing_docs)]
    pub message: std::string::String,

    /// [theta1, theta2, theta3, theta4] actually commanded, radians
    pub joint_angles: Vec<f64>,

}



impl Default for MoveTo_Response {
  fn default() -> Self {
    <Self as rosidl_runtime_rs::Message>::from_rmw_message(super::srv::rmw::MoveTo_Response::default())
  }
}

impl rosidl_runtime_rs::Message for MoveTo_Response {
  type RmwMsg = super::srv::rmw::MoveTo_Response;

  fn into_rmw_message(msg_cow: std::borrow::Cow<'_, Self>) -> std::borrow::Cow<'_, Self::RmwMsg> {
    match msg_cow {
      std::borrow::Cow::Owned(msg) => std::borrow::Cow::Owned(Self::RmwMsg {
        success: msg.success,
        message: msg.message.as_str().into(),
        joint_angles: msg.joint_angles.into(),
      }),
      std::borrow::Cow::Borrowed(msg) => std::borrow::Cow::Owned(Self::RmwMsg {
      success: msg.success,
        message: msg.message.as_str().into(),
        joint_angles: msg.joint_angles.as_slice().into(),
      })
    }
  }

  fn from_rmw_message(msg: Self::RmwMsg) -> Self {
    Self {
      success: msg.success,
      message: msg.message.to_string(),
      joint_angles: msg.joint_angles
          .into_iter()
          .collect(),
    }
  }
}






#[link(name = "modular_arm_interfaces__rosidl_typesupport_c")]
extern "C" {
    fn rosidl_typesupport_c__get_service_type_support_handle__modular_arm_interfaces__srv__MoveTo() -> *const std::ffi::c_void;
}

// Corresponds to modular_arm_interfaces__srv__MoveTo
#[allow(missing_docs, non_camel_case_types)]
pub struct MoveTo;

impl rosidl_runtime_rs::Service for MoveTo {
    type Request = MoveTo_Request;
    type Response = MoveTo_Response;

    fn get_type_support() -> *const std::ffi::c_void {
        // SAFETY: No preconditions for this function.
        unsafe { rosidl_typesupport_c__get_service_type_support_handle__modular_arm_interfaces__srv__MoveTo() }
    }
}


