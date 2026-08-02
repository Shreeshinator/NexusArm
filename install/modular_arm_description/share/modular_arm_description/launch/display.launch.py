"""Launch the arm in RViz only, with joint_state_publisher_gui sliders.
Good for a first sanity check of the URDF before touching Gazebo.

Run:
    ros2 launch modular_arm_description display.launch.py
"""
import os
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.substitutions import Command, LaunchConfiguration
from launch_ros.parameter_descriptions import ParameterValue
from launch_ros.actions import Node


def generate_launch_description():
    pkg_share = get_package_share_directory("modular_arm_description")
    xacro_path = os.path.join(pkg_share, "urdf", "modular_arm.urdf.xacro")
    rviz_config = os.path.join(pkg_share, "rviz", "view_arm.rviz")

    use_sim_time = LaunchConfiguration("use_sim_time")

    robot_description = {
    "robot_description": ParameterValue(Command(["xacro ", xacro_path]), value_type=str)
    }

    return LaunchDescription([
        DeclareLaunchArgument("use_sim_time", default_value="false"),

        Node(
            package="robot_state_publisher",
            executable="robot_state_publisher",
            output="screen",
            parameters=[robot_description, {"use_sim_time": use_sim_time}],
        ),
        Node(
            package="joint_state_publisher_gui",
            executable="joint_state_publisher_gui",
            output="screen",
        ),
        Node(
            package="rviz2",
            executable="rviz2",
            arguments=["-d", rviz_config],
            output="screen",
        ),
    ])
