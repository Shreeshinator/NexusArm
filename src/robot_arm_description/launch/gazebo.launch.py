"""Launch the arm in Gazebo Harmonic (gz sim) with ros2_control active, a
workspace world, and camera bridges.  For the full stack with move_to API and
Foxglove, use sim_bringup.launch.py in modular_arm_bringup instead.

Run:
    ros2 launch robot_arm_description gazebo.launch.py
"""
import os
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription, RegisterEventHandler, TimerAction
from launch.event_handlers import OnProcessExit
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import Command
from launch_ros.parameter_descriptions import ParameterValue
from launch_ros.actions import Node


def generate_launch_description():
    """
    Launches Gazebo Harmonic with a workspace world, spawns the arm,
    loads controllers, and bridges cameras to ROS topics.
    """
    pkg_share = get_package_share_directory("robot_arm_description")

    xacro_path = os.path.join(pkg_share, "urdf", "robot_arm.urdf.xacro")
    world_path = os.path.join(pkg_share, "worlds", "workspace.sdf")

    # GZ_SIM_RESOURCE_PATH: GZ prepends a "model://" prefix, so to find
    # model://robot_arm_description/meshes/X.stl we point at the share/ dir
    # that contains the robot_arm_description subdirectory.
    gz_resource_path = os.pathsep.join([
        os.environ.get("GZ_SIM_RESOURCE_PATH", ""),
        os.path.normpath(os.path.join(pkg_share, "..")),
    ]).strip(os.pathsep)
    os.environ["GZ_SIM_RESOURCE_PATH"] = gz_resource_path

    ros_gz_sim_share = get_package_share_directory("ros_gz_sim")

    robot_description = {
        "robot_description": ParameterValue(
            Command(["xacro ", xacro_path]), value_type=str
        )
    }

    gz_sim = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(ros_gz_sim_share, "launch", "gz_sim.launch.py")
        ),
        launch_arguments={"gz_args": f"-r -s -v3 {world_path}"}.items(),
    )

    robot_state_publisher = Node(
        package="robot_state_publisher",
        executable="robot_state_publisher",
        output="screen",
        parameters=[robot_description, {"use_sim_time": True}],
    )

    spawn_entity = Node(
        package="ros_gz_sim",
        executable="create",
        arguments=["-topic", "robot_description", "-name", "modular_arm", "-x", "-0.03", "-z", "0.0"],
        output="screen",
    )

    clock_bridge = Node(
        package="ros_gz_bridge",
        executable="parameter_bridge",
        arguments=["/clock@rosgraph_msgs/msg/Clock[gz.msgs.Clock"],
        output="screen",
    )

    # Camera bridges: Gz image + camera_info -> ROS topics
    camera_bridges = []

    # Static front camera (world model, always present -> bridge starts immediately)
    for cam_name in ("cam_front",):
        gz_prefix = f"/world/workspace/model/{cam_name}/link/camera_link/sensor/camera"
        cam_bridges = [
            Node(
                package="ros_gz_bridge",
                executable="parameter_bridge",
                arguments=[f"{gz_prefix}/image@sensor_msgs/msg/Image[gz.msgs.Image"],
                remappings=[(f"{gz_prefix}/image", f"/{cam_name}/image_raw")],
                output="screen",
            ),
            Node(
                package="ros_gz_bridge",
                executable="parameter_bridge",
                arguments=[
                    f"{gz_prefix}/camera_info@sensor_msgs/msg/CameraInfo[gz.msgs.CameraInfo"
                ],
                remappings=[
                    (f"{gz_prefix}/camera_info", f"/{cam_name}/camera_info")
                ],
                output="screen",
            ),
        ]
        camera_bridges.extend(cam_bridges) # extend is used to add the list of cam_bridges to camera_bridges

    # Wrist camera (mounted on robot model "modular_arm").  Its sensor only
    # exists AFTER the robot is spawned, so these bridges MUST start after
    # spawn_entity exits — otherwise they race ahead, subscribe to a topic
    # that doesn't exist yet, and /wrist_camera/image_raw stays empty.
    wrist_prefix = "/world/workspace/model/modular_arm/link/link4/sensor/wrist_camera"
    wrist_bridges = [
        Node(
            package="ros_gz_bridge",
            executable="parameter_bridge",
            arguments=[f"{wrist_prefix}/image@sensor_msgs/msg/Image[gz.msgs.Image"],
            remappings=[(f"{wrist_prefix}/image", "/wrist_camera/image_raw")],
            output="screen",
        ),
        Node(
            package="ros_gz_bridge",
            executable="parameter_bridge",
            arguments=[
                f"{wrist_prefix}/camera_info@sensor_msgs/msg/CameraInfo[gz.msgs.CameraInfo"
            ],
            remappings=[
                (f"{wrist_prefix}/camera_info", "/wrist_camera/camera_info")
            ],
            output="screen",
        ),
    ]

    delayed_wrist_bridges = RegisterEventHandler(
        event_handler=OnProcessExit(
            target_action=spawn_entity,
            on_exit=[TimerAction(period=1.0, actions=wrist_bridges)],
        )
    )

    joint_state_broadcaster_spawner = Node(
        package="controller_manager",
        executable="spawner",
        arguments=["joint_state_broadcaster", "--controller-manager-timeout", "60"],
        output="screen",
    )

    arm_controller_spawner = Node(
        package="controller_manager",
        executable="spawner",
        arguments=["arm_controller", "--controller-manager-timeout", "60"],
        output="screen",
    )

    # Delay controllers so gz_ros2_control hardware is fully initialized
    delayed_broadcaster = RegisterEventHandler(
        event_handler=OnProcessExit(
            target_action=spawn_entity,
            on_exit=[TimerAction(period=3.0, actions=[joint_state_broadcaster_spawner])],
        )
    )

    delayed_arm_controller = RegisterEventHandler(
        event_handler=OnProcessExit(
            target_action=spawn_entity,
            on_exit=[TimerAction(period=5.0, actions=[arm_controller_spawner])],
        )
    )

    return LaunchDescription([
        gz_sim,
        robot_state_publisher,
        clock_bridge,
        spawn_entity,
        *camera_bridges,
        delayed_wrist_bridges,
        delayed_broadcaster,
        delayed_arm_controller,
    ])
