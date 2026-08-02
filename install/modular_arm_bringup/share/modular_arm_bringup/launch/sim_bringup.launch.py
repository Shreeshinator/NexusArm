"""One-command bringup: Gazebo Harmonic + arm + ros2_control + move_to API.

Run:
    ros2 launch modular_arm_bringup sim_bringup.launch.py

Then in another terminal:
    ros2 service call /modular_arm/move_to modular_arm_interfaces/srv/MoveTo \
        "{x: 0.15, y: 0.05, z: 0.10, pitch: -1.0, elbow: 'up', duration_sec: 2.0}"
"""
import os # for os.path.join
from ament_index_python.packages import get_package_share_directory # for get_package_share_directory
from launch import LaunchDescription # for LaunchDescription
from launch.actions import IncludeLaunchDescription, TimerAction # for IncludeLaunchDescription, TimerAction
from launch.launch_description_sources import PythonLaunchDescriptionSource # for PythonLaunchDescriptionSource which is used to include other launch files
from launch_ros.actions import Node # for Node


def generate_launch_description():
    description_share = get_package_share_directory("modular_arm_description") # find the share directory of the modular_arm_description package

    gazebo_launch = IncludeLaunchDescription( # IncludeLaunchDescription is used to include another launch file for Gazebo simulation
        PythonLaunchDescriptionSource( # this does the actual inclusion of the launch file
            os.path.join(description_share, "launch", "gazebo.launch.py")
        )
    )

    # Give the controllers a few seconds to spawn before the move_to node
    # starts hammering on the action server.
    move_to_node = TimerAction( # starts the move_to_node after a delay of 6 seconds to ensure that the controllers are ready
        period=6.0,
        actions=[
            Node(
                package="modular_arm_kinematics",
                executable="move_to_node",
                output="screen",
            )
        ],
    )

    return LaunchDescription([
        gazebo_launch,
        move_to_node,
    ])
