# generated from rosidl_cmake/cmake/rosidl_cmake_aggregate_target-extras.cmake.in

# Create a convenience aggregate target modular_arm_interfaces::modular_arm_interfaces
# that links all generated interface targets, so downstream packages can use
# a single modern CMake target name instead of ${modular_arm_interfaces_TARGETS}.
if(modular_arm_interfaces_TARGETS AND NOT TARGET modular_arm_interfaces::modular_arm_interfaces)
  add_library(modular_arm_interfaces::modular_arm_interfaces INTERFACE IMPORTED)
  set_target_properties(modular_arm_interfaces::modular_arm_interfaces PROPERTIES
    INTERFACE_LINK_LIBRARIES "${modular_arm_interfaces_TARGETS}")
endif()
