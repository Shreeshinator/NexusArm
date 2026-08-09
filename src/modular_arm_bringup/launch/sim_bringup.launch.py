"""One-command bringup: Gazebo Harmonic + arm + ros2_control + move_to API + cameras + Foxglove.

Run:
    ros2 launch modular_arm_bringup sim_bringup.launch.py

Then in another terminal:
    ros2 service call /modular_arm/move_to modular_arm_interfaces/srv/MoveTo \
        "{x: 0.10, y: 0.05, z: 0.10, pitch: -0.3, elbow: '', gripper: 0.0, duration_sec: 2.0}"
"""
import os
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription, TimerAction
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch_ros.actions import Node


def generate_launch_description():
    description_share = get_package_share_directory("modular_arm_description")

    gazebo_launch = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(description_share, "launch", "gazebo.launch.py")
        )
    )

    foxglove = Node(
        package="foxglove_bridge",
        executable="foxglove_bridge",
        name="foxglove_bridge",
        output="screen",
        parameters=[{"use_sim_time": True}],
    )

    move_to_node = TimerAction(
        period=6.0,
        actions=[
            Node(
                package="modular_arm_kinematics",
                executable="move_to_node",
                output="screen",
                parameters=[{"use_sim_time": True}],
            )
        ],
    )

    return LaunchDescription([
        gazebo_launch,
        foxglove,
        move_to_node,
    ])
