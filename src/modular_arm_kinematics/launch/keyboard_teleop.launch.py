"""Launch the keyboard teleop node (requires sim_bringup / move_to service running)."""

from launch import LaunchDescription
from launch.actions import TimerAction
from launch_ros.actions import Node


def generate_launch_description():
    return LaunchDescription([
        TimerAction(
            period=2.0,
            actions=[
                Node(
                    package="modular_arm_kinematics",
                    executable="keyboard_teleop",
                    output="screen",
                )
            ],
        ),
    ])
