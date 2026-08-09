"""Launch the teleoperation node alongside the simulated arm.

Run:
    ros2 launch modular_arm_teleop teleop.launch.py

This launches:
  1.  Gazebo + arm + controllers (via modular_arm_description)
  2.  The teleop_node that reads the Arduino leader arm over serial
      and streams joint commands.

The built-in move_to_node is NOT launched; the arm_controller is driven
directly by the teleop node.
"""

import os
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription, TimerAction
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch_ros.actions import Node


def generate_launch_description():
    description_share = get_package_share_directory("modular_arm_description")
    teleop_share = get_package_share_directory("modular_arm_teleop")

    teleop_params = os.path.join(teleop_share, "config", "teleop_params.yaml")

    gazebo_launch = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(description_share, "launch", "gazebo.launch.py")
        )
    )

    teleop_node = TimerAction(
        period=6.0,
        actions=[
            Node(
                package="modular_arm_teleop",
                executable="teleop_node",
                name="teleop_node",
                output="screen",
                parameters=[teleop_params, {"use_sim_time": True}],
            )
        ],
    )

    return LaunchDescription([gazebo_launch, teleop_node])
