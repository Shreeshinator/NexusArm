"""ROS2 node exposing the move_to(x, y, z) API for the modular arm.

This is the seam future modules plug into:
  - a vision module can publish a target pose it detected,
  - an LLM planner can call this service after reasoning about a command,
  - a cloud VLA model's output can be converted to an (x, y, z, pitch) call.

None of them need to know anything about joint angles or IK -- that's the
whole point of keeping this as its own package with its own service.

Run standalone (with Gazebo + controllers already running):
    ros2 run modular_arm_kinematics move_to_node

Call it:
    ros2 service call /modular_arm/move_to modular_arm_interfaces/srv/MoveTo \
        "{x: 0.15, y: 0.05, z: 0.10, pitch: -1.0, elbow: 'up', duration_sec: 2.0}"
"""
import math

import rclpy
from rclpy.action import ActionClient
from rclpy.node import Node

from control_msgs.action import FollowJointTrajectory
from trajectory_msgs.msg import JointTrajectoryPoint

from modular_arm_interfaces.srv import MoveTo

from .ik import inverse_kinematics, Unreachable

JOINT_NAMES = ["joint1", "joint2", "joint3", "joint4"]
ACTION_NAME = "/arm_controller/follow_joint_trajectory"


class MoveToNode(Node):
    def __init__(self):
        super().__init__("move_to_node")

        self._action_client = ActionClient(self, FollowJointTrajectory, ACTION_NAME)
        self._srv = self.create_service(MoveTo, "/modular_arm/move_to", self._handle_move_to)

        self.get_logger().info(f"move_to_node ready, waiting on action server '{ACTION_NAME}'")

    def _handle_move_to(self, request: MoveTo.Request, response: MoveTo.Response) -> MoveTo.Response:
        try:
            solution = inverse_kinematics(
                x=request.x,
                y=request.y,
                z=request.z,
                pitch=request.pitch,
                elbow=request.elbow or "up",
            )
        except Unreachable as exc:
            response.success = False
            response.message = str(exc)
            response.joint_angles = []
            return response
        except ValueError as exc:
            response.success = False
            response.message = str(exc)
            response.joint_angles = []
            return response

        joint_angles = solution.as_list()
        duration = request.duration_sec if request.duration_sec > 0.0 else 2.0

        sent_ok = self._send_trajectory(joint_angles, duration)
        response.success = sent_ok
        response.joint_angles = joint_angles
        response.message = (
            "Trajectory goal sent." if sent_ok
            else "Failed to reach the arm_controller action server."
        )
        return response

    def _send_trajectory(self, joint_angles, duration_sec: float) -> bool:
        if not self._action_client.wait_for_server(timeout_sec=3.0):
            self.get_logger().error(f"Action server '{ACTION_NAME}' not available.")
            return False

        goal = FollowJointTrajectory.Goal()
        goal.trajectory.joint_names = JOINT_NAMES

        point = JointTrajectoryPoint()
        point.positions = joint_angles
        point.velocities = [0.0] * len(joint_angles)
        sec = int(duration_sec)
        nanosec = int((duration_sec - sec) * 1e9)
        point.time_from_start.sec = sec
        point.time_from_start.nanosec = nanosec

        goal.trajectory.points = [point]

        self.get_logger().info(f"Sending trajectory goal: {joint_angles}")
        self._action_client.send_goal_async(goal)
        return True


def main(args=None):
    rclpy.init(args=args)
    node = MoveToNode()
    try:
        rclpy.spin(node)
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == "__main__":
    main()
