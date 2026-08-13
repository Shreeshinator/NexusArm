cmake_minimum_required(VERSION 3.8)
project(robot_arm_description)

find_package(ament_cmake REQUIRED)

install(DIRECTORY urdf launch config rviz worlds meshes
  DESTINATION share/${PROJECT_NAME}
)

ament_package()
