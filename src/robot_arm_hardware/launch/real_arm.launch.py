"""Launch the real-robot arm stack: serial bridge + Cartesian move_to service.

Run the teleop in a separate terminal afterwards:
    ros2 run robot_arm_hardware keyboard_teleop

Usage:
    ros2 launch robot_arm_hardware real_arm.launch.py serial_port:=/dev/ttyACM0
"""
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
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
        parameters=[{"serial_port": serial_port}, {"baud_rate": baud_rate}],
    )

    hw_move_to = Node(
        package="robot_arm_hardware",
        executable="hw_move_to",
        name="hw_move_to",
        output="screen",
    )

    return LaunchDescription(
        [
            DeclareLaunchArgument(
                "serial_port",
                default_value="/dev/ttyACM0",
                description="Serial device for the Arduino Uno R3 servo bridge (e.g. /dev/ttyACM0 or /dev/ttyUSB0). Shown in `ros2 launch --show-args`.",
            ),
            DeclareLaunchArgument(
                "baud_rate",
                default_value="115200",
                description="Baud rate (bits per second) for the serial link. Must match the Arduino sketch Serial.begin(...).",
            ),
            hw_interface,
            hw_move_to,
        ]
    )
