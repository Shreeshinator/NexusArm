"""Launch the arm in Gazebo Harmonic (gz sim) with ros2_control active.

Run:
    ros2 launch modular_arm_description gazebo.launch.py
"""
import os
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription, RegisterEventHandler
from launch.event_handlers import OnProcessExit
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import Command
from launch_ros.actions import Node


def generate_launch_description():
    pkg_share = get_package_share_directory("modular_arm_description") # get the path to the package share directory
    xacro_path = os.path.join(pkg_share, "urdf", "modular_arm.urdf.xacro") # get the path to the xacro file
    ros_gz_sim_share = get_package_share_directory("ros_gz_sim") # get the path to the ros_gz_sim package share directory

    robot_description = {
        "robot_description": Command(["xacro ", xacro_path]) # Execute the xacro command to generate the URDF from the xacro file
    }

    # Start Gazebo Harmonic with an empty world
    gz_sim = IncludeLaunchDescription( # Include the launch description for Gazebo Harmonic
        PythonLaunchDescriptionSource( # for actually launching Gazebo Harmonic
            os.path.join(ros_gz_sim_share, "launch", "gz_sim.launch.py")
        ),
        launch_arguments={"gz_args": "-r -v3 empty.sdf"}.items(),
    )

    robot_state_publisher = Node(
        package="robot_state_publisher",
        executable="robot_state_publisher",
        output="screen",
        parameters=[robot_description, {"use_sim_time": True}],
    )

    # Spawn the robot into the running Gazebo world from /robot_description
    spawn_entity = Node(
        package="ros_gz_sim",
        executable="create",
        arguments=["-topic", "robot_description", "-name", "modular_arm", "-z", "0.0"],
        output="screen",
    )

    # Bridge sim clock so ROS nodes (controllers, rclpy nodes) use Gazebo time
    clock_bridge = Node(
        package="ros_gz_bridge",
        executable="parameter_bridge",
        arguments=["/clock@rosgraph_msgs/msg/Clock[gz.msgs.Clock"],
        output="screen",
    )

    joint_state_broadcaster_spawner = Node(
        package="controller_manager",
        executable="spawner",
        arguments=["joint_state_broadcaster"],
        output="screen",
    )

    arm_controller_spawner = Node(
        package="controller_manager",
        executable="spawner",
        arguments=["arm_controller"],
        output="screen",
    )

    # Load controllers only after the robot has actually been spawned,
    # otherwise the controller_manager service isn't up yet.
    delayed_broadcaster = RegisterEventHandler(
        event_handler=OnProcessExit(
            target_action=spawn_entity,
            on_exit=[joint_state_broadcaster_spawner],
        )
    )
    delayed_arm_controller = RegisterEventHandler(
        event_handler=OnProcessExit(
            target_action=joint_state_broadcaster_spawner,
            on_exit=[arm_controller_spawner],
        )
    )

    return LaunchDescription([
        gz_sim,
        robot_state_publisher,
        clock_bridge,
        spawn_entity,
        delayed_broadcaster,
        delayed_arm_controller,
    ])
