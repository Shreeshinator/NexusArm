"""One-command real-arm bringup: hw_interface + hw_move_to + camera_bridge.

Usage (native):
    ros2 launch robot_arm_hardware real_bringup.launch.py \
      serial_port:=/dev/ttyACM0 front_url:=http://<phone-ip>:4747/video fps:=15.0

Docker (Uno Q):
    FRONT_URL=http://<phone-ip>:4747/video docker compose up --build

Cameras are optional — leave front_url/gripper_url empty to disable that thread.
"""
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node


def generate_launch_description():
    serial_port = LaunchConfiguration("serial_port")
    baud_rate = LaunchConfiguration("baud_rate")
    front_url = LaunchConfiguration("front_url")
    gripper_url = LaunchConfiguration("gripper_url")
    fps = LaunchConfiguration("fps")
    front_topic = LaunchConfiguration("front_topic")
    gripper_topic = LaunchConfiguration("gripper_topic")

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

    camera_bridge = Node(
        package="robot_arm_hardware",
        executable="camera_bridge",
        name="camera_bridge",
        output="screen",
        parameters=[
            {"front_url": front_url},
            {"gripper_url": gripper_url},
            {"front_topic": front_topic},
            {"gripper_topic": gripper_topic},
            {"fps": fps},
        ],
    )

    return LaunchDescription(
        [
            DeclareLaunchArgument(
                "serial_port",
                default_value="/dev/ttyACM0",
                description="Serial device for Uno R3 (e.g. /dev/ttyACM0 or /dev/ttyUSB0).",
            ),
            DeclareLaunchArgument(
                "baud_rate",
                default_value="115200",
                description="Baud rate — must match Serial.begin() in servo_bridge.ino (115200).",
            ),
            DeclareLaunchArgument(
                "front_url",
                default_value="",
                description="MJPEG URL for front camera (DroidCam http://<ip>:4747/video or ESP32 http://<ip>:81/stream). Empty disables.",
            ),
            DeclareLaunchArgument(
                "gripper_url",
                default_value="",
                description="MJPEG URL for gripper camera. Empty disables.",
            ),
            DeclareLaunchArgument(
                "fps",
                default_value="15.0",
                description="Max camera publish rate Hz (cap; actual ≤ measured ros2 topic hz).",
            ),
            DeclareLaunchArgument(
                "front_topic",
                default_value="/front_cam/image_raw/compressed",
                description="ROS topic for front camera.",
            ),
            DeclareLaunchArgument(
                "gripper_topic",
                default_value="/gripper_cam/image_raw/compressed",
                description="ROS topic for gripper camera.",
            ),
            hw_interface,
            hw_move_to,
            camera_bridge,
        ]
    )
