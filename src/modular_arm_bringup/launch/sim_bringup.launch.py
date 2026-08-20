"""
One-command bringup: Gazebo Harmonic + arm + ros2_control + move_to API + cameras + Foxglove.

Run:
    ros2 launch modular_arm_bringup sim_bringup.launch.py

Then in another terminal:
    ros2 service call /modular_arm/move_to modular_arm_interfaces/srv/MoveTo \
        "{x: 0.10, y: 0.05, z: 0.10, pitch: -0.3, elbow: '', gripper: 0.0, duration_sec: 2.0}"
"""
import os # for path joining
from ament_index_python.packages import get_package_share_directory # for finding package share directories

from launch import LaunchDescription # for creating launch descriptions
from launch.actions import IncludeLaunchDescription, TimerAction # for including other launch files and scheduling actions
from launch.launch_description_sources import PythonLaunchDescriptionSource # for including launch files written in Python
from launch_ros.actions import Node # for launching ROS 2 nodes


def generate_launch_description():
    description_share = get_package_share_directory("robot_arm_description")

    gazebo_launch = IncludeLaunchDescription( # include the Gazebo launch file from the robot_arm_description package
        PythonLaunchDescriptionSource(
            os.path.join(description_share, "launch", "gazebo.launch.py")
        )
    )

    # Foxglove bridge is started after a delay to ensure everything else is alive
    foxglove = TimerAction(
        period=8.0,  # 8 seconds seems good, you can adjust.
        actions=[
            Node(
                package="foxglove_bridge",
                executable="foxglove_bridge",
                name="foxglove_bridge",
                output="screen",
                parameters=[{"use_sim_time": True}],
            )
        ],
    )

    move_to_node = TimerAction( # Start the move_to_node after a delay to ensure Gazebo and other nodes are up
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

    return LaunchDescription([ # return the launch description
        gazebo_launch,
        foxglove,
        move_to_node,
    ])
