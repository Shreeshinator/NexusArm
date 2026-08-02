from launch import LaunchDescription
from launch_ros.actions import Node


def generate_launch_description():
    return LaunchDescription([
        Node(
            package="modular_arm_kinematics",
            executable="move_to_node",
            output="screen",
        ),
    ])
