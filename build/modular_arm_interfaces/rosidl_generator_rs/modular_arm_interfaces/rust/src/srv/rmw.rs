#[cfg(feature = "serde")]
use serde::{Deserialize, Serialize};



#[link(name = "modular_arm_interfaces__rosidl_typesupport_c")]
extern "C" {
    fn rosidl_typesupport_c__get_message_type_support_handle__modular_arm_interfaces__srv__MoveTo_Request() -> *const std::ffi::c_void;
}

#[link(name = "modular_arm_interfaces__rosidl_generator_c")]
extern "C" {
    fn modular_arm_interfaces__srv__MoveTo_Request__init(msg: *mut MoveTo_Request) -> bool;
    fn modular_arm_interfaces__srv__MoveTo_Request__Sequence__init(seq: *mut rosidl_runtime_rs::Sequence<MoveTo_Request>, size: usize) -> bool;
    fn modular_arm_interfaces__srv__MoveTo_Request__Sequence__fini(seq: *mut rosidl_runtime_rs::Sequence<MoveTo_Request>);
    fn modular_arm_interfaces__srv__MoveTo_Request__Sequence__copy(in_seq: &rosidl_runtime_rs::Sequence<MoveTo_Request>, out_seq: *mut rosidl_runtime_rs::Sequence<MoveTo_Request>) -> bool;
}

// Corresponds to modular_arm_interfaces__srv__MoveTo_Request
#[cfg_attr(feature = "serde", derive(Deserialize, Serialize))]


// This struct is not documented.
#[allow(missing_docs)]

#[allow(non_camel_case_types)]
#[repr(C)]
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
    pub elbow: rosidl_runtime_rs::String,

    /// time to execute the trajectory, e.g. 2.0
    pub duration_sec: f64,

}



impl Default for MoveTo_Request {
  fn default() -> Self {
    unsafe {
      let mut msg = std::mem::zeroed();
      if !modular_arm_interfaces__srv__MoveTo_Request__init(&mut msg as *mut _) {
        panic!("Call to modular_arm_interfaces__srv__MoveTo_Request__init() failed");
      }
      msg
    }
  }
}

impl rosidl_runtime_rs::SequenceAlloc for MoveTo_Request {
  fn sequence_init(seq: &mut rosidl_runtime_rs::Sequence<Self>, size: usize) -> bool {
    // SAFETY: This is safe since the pointer is guaranteed to be valid/initialized.
    unsafe { modular_arm_interfaces__srv__MoveTo_Request__Sequence__init(seq as *mut _, size) }
  }
  fn sequence_fini(seq: &mut rosidl_runtime_rs::Sequence<Self>) {
    // SAFETY: This is safe since the pointer is guaranteed to be valid/initialized.
    unsafe { modular_arm_interfaces__srv__MoveTo_Request__Sequence__fini(seq as *mut _) }
  }
  fn sequence_copy(in_seq: &rosidl_runtime_rs::Sequence<Self>, out_seq: &mut rosidl_runtime_rs::Sequence<Self>) -> bool {
    // SAFETY: This is safe since the pointer is guaranteed to be valid/initialized.
    unsafe { modular_arm_interfaces__srv__MoveTo_Request__Sequence__copy(in_seq, out_seq as *mut _) }
  }
}

impl rosidl_runtime_rs::Message for MoveTo_Request {
  type RmwMsg = Self;
  fn into_rmw_message(msg_cow: std::borrow::Cow<'_, Self>) -> std::borrow::Cow<'_, Self::RmwMsg> { msg_cow }
  fn from_rmw_message(msg: Self::RmwMsg) -> Self { msg }
}

impl rosidl_runtime_rs::RmwMessage for MoveTo_Request where Self: Sized {
  const TYPE_NAME: &'static str = "modular_arm_interfaces/srv/MoveTo_Request";
  fn get_type_support() -> *const std::ffi::c_void {
    // SAFETY: No preconditions for this function.
    unsafe { rosidl_typesupport_c__get_message_type_support_handle__modular_arm_interfaces__srv__MoveTo_Request() }
  }
}


#[link(name = "modular_arm_interfaces__rosidl_typesupport_c")]
extern "C" {
    fn rosidl_typesupport_c__get_message_type_support_handle__modular_arm_interfaces__srv__MoveTo_Response() -> *const std::ffi::c_void;
}

#[link(name = "modular_arm_interfaces__rosidl_generator_c")]
extern "C" {
    fn modular_arm_interfaces__srv__MoveTo_Response__init(msg: *mut MoveTo_Response) -> bool;
    fn modular_arm_interfaces__srv__MoveTo_Response__Sequence__init(seq: *mut rosidl_runtime_rs::Sequence<MoveTo_Response>, size: usize) -> bool;
    fn modular_arm_interfaces__srv__MoveTo_Response__Sequence__fini(seq: *mut rosidl_runtime_rs::Sequence<MoveTo_Response>);
    fn modular_arm_interfaces__srv__MoveTo_Response__Sequence__copy(in_seq: &rosidl_runtime_rs::Sequence<MoveTo_Response>, out_seq: *mut rosidl_runtime_rs::Sequence<MoveTo_Response>) -> bool;
}

// Corresponds to modular_arm_interfaces__srv__MoveTo_Response
#[cfg_attr(feature = "serde", derive(Deserialize, Serialize))]


// This struct is not documented.
#[allow(missing_docs)]

#[allow(non_camel_case_types)]
#[repr(C)]
#[derive(Clone, Debug, PartialEq, PartialOrd)]
pub struct MoveTo_Response {

    // This member is not documented.
    #[allow(missing_docs)]
    pub success: bool,


    // This member is not documented.
    #[allow(missing_docs)]
    pub message: rosidl_runtime_rs::String,

    /// [theta1, theta2, theta3, theta4] actually commanded, radians
    pub joint_angles: rosidl_runtime_rs::Sequence<f64>,

}



impl Default for MoveTo_Response {
  fn default() -> Self {
    unsafe {
      let mut msg = std::mem::zeroed();
      if !modular_arm_interfaces__srv__MoveTo_Response__init(&mut msg as *mut _) {
        panic!("Call to modular_arm_interfaces__srv__MoveTo_Response__init() failed");
      }
      msg
    }
  }
}

impl rosidl_runtime_rs::SequenceAlloc for MoveTo_Response {
  fn sequence_init(seq: &mut rosidl_runtime_rs::Sequence<Self>, size: usize) -> bool {
    // SAFETY: This is safe since the pointer is guaranteed to be valid/initialized.
    unsafe { modular_arm_interfaces__srv__MoveTo_Response__Sequence__init(seq as *mut _, size) }
  }
  fn sequence_fini(seq: &mut rosidl_runtime_rs::Sequence<Self>) {
    // SAFETY: This is safe since the pointer is guaranteed to be valid/initialized.
    unsafe { modular_arm_interfaces__srv__MoveTo_Response__Sequence__fini(seq as *mut _) }
  }
  fn sequence_copy(in_seq: &rosidl_runtime_rs::Sequence<Self>, out_seq: &mut rosidl_runtime_rs::Sequence<Self>) -> bool {
    // SAFETY: This is safe since the pointer is guaranteed to be valid/initialized.
    unsafe { modular_arm_interfaces__srv__MoveTo_Response__Sequence__copy(in_seq, out_seq as *mut _) }
  }
}

impl rosidl_runtime_rs::Message for MoveTo_Response {
  type RmwMsg = Self;
  fn into_rmw_message(msg_cow: std::borrow::Cow<'_, Self>) -> std::borrow::Cow<'_, Self::RmwMsg> { msg_cow }
  fn from_rmw_message(msg: Self::RmwMsg) -> Self { msg }
}

impl rosidl_runtime_rs::RmwMessage for MoveTo_Response where Self: Sized {
  const TYPE_NAME: &'static str = "modular_arm_interfaces/srv/MoveTo_Response";
  fn get_type_support() -> *const std::ffi::c_void {
    // SAFETY: No preconditions for this function.
    unsafe { rosidl_typesupport_c__get_message_type_support_handle__modular_arm_interfaces__srv__MoveTo_Response() }
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


