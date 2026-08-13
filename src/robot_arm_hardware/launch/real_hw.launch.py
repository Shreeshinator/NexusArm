"""Launch the real-robot hardware bridge (Arduino Uno R3 servo bridge).

Usage:
    ros2 launch robot_arm_hardware real_hw.launch.py serial_port:=/dev/ttyACM0
"""
from launch import LaunchDescription
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node


def generate_launch_description():
    serial_port = LaunchConfiguration("serial_port", default="/dev/ttyACM0")
    baud_rate = LaunchConfiguration("baud_rate", default="115200")

    hw_interface = Node(
        package="robot_arm_hardware",
        executable="hw_interface",
        name="real_hw_interface",
        output="screen",
        parameters=[
            {"serial_port": serial_port},
            {"baud_rate": baud_rate},
        ],
    )

    return LaunchDescription([hw_interface])
