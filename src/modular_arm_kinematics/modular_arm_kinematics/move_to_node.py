"""ROS2 node exposing the move_to(x, y, z) API for the modular arm.

This is the seam future modules plug into:
  - a vision module can publish a target pose it detected,
  - an LLM planner can call this service after reasoning about a command,
  - a cloud VLA model's output can be converted to an (x, y, z, pitch) call.

None of them need to know anything about joint angles or IK -- that's the
whole point of keeping this as its own package with its own service.

Run standalone (with Gazebo + controllers already running):
    ros2 run modular_arm_kinematics move_to_node

Call it (with gripper 0.0 = open, 1.0 = closed):
    ros2 service call /modular_arm/move_to modular_arm_interfaces/srv/MoveTo \
        "{x: 0.10, y: 0.05, z: 0.10, pitch: -0.3, elbow: '', gripper: 0.0, duration_sec: 2.0}"
"""
import math # MATH!

import rclpy
from rclpy.action import ActionClient
from rclpy.callback_groups import ReentrantCallbackGroup 
# ReentrantCallbackGroup allows callbacks to be called from multiple threads, which is useful for action clients that may have callbacks invoked from different threads.
from rclpy.node import Node

from control_msgs.action import FollowJointTrajectory
from trajectory_msgs.msg import JointTrajectoryPoint

from modular_arm_interfaces.srv import MoveTo

from .ik import inverse_kinematics, Unreachable

JOINT_NAMES = ["joint1", "joint2", "joint3", "joint4", "finger_left_joint", "finger_right_joint"]
ACTION_NAME = "/arm_controller/follow_joint_trajectory"
GRIPPER_MAX_TRAVEL = 0.015  # max prismatic travel per finger, must match URDF upper limit


class MoveToNode(Node):
    def __init__(self):
        super().__init__("move_to_node")

        self._action_client = ActionClient(
            self, FollowJointTrajectory, ACTION_NAME,
            callback_group=ReentrantCallbackGroup() # Basicallly, it allows the node to process multiple service requests at the same time without blocking.
        )
        self._srv = self.create_service(MoveTo, "/modular_arm/move_to", self._handle_move_to)

        self.get_logger().info(f"move_to_node ready, waiting on action server '{ACTION_NAME}'")

    def _handle_move_to(self, request: MoveTo.Request, response: MoveTo.Response) -> MoveTo.Response:
        try:
            solution = inverse_kinematics(
                x=request.x,
                y=request.y,
                z=request.z,
                pitch=request.pitch,
                elbow=request.elbow if request.elbow in ("up", "down") else None,
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
        grip_factor = max(0.0, min(1.0, request.gripper))
        finger_pos = grip_factor * GRIPPER_MAX_TRAVEL
        joint_angles += [finger_pos, finger_pos]
        duration = request.duration_sec if request.duration_sec > 0.0 else 2.0

        sent_ok, sent_message = self._send_trajectory(joint_angles, duration)
        response.success = sent_ok
        response.joint_angles = joint_angles
        response.message = sent_message
        return response

    def _send_trajectory(self, joint_angles, duration_sec: float):
        if not self._action_client.wait_for_server(timeout_sec=3.0):
            self.get_logger().error(f"Action server '{ACTION_NAME}' not available.")
            return False, f"Action server '{ACTION_NAME}' not available."

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

        self.get_logger().info(f"Sending trajectory: {[f'{a:.3f}' for a in joint_angles]}")

        # Fire-and-forget: send the goal and return immediately.  The trajectory
        # controller executes it asynchronously; we don't block a service thread
        # (blocking inside a callback busy-loops the executor and pegs CPU).
        future = self._action_client.send_goal_async(goal)
        future.add_done_callback(self._on_goal_accepted)
        return True, "Trajectory goal sent (accepted asynchronously)."

    def _on_goal_accepted(self, future):
        try:
            handle = future.result()
        except Exception as exc:
            self.get_logger().error(f"Goal response error: {exc}")
            return
        if handle is None:
            self.get_logger().error("Goal rejected by action server.")
            return
        self.get_logger().info("Goal accepted by action server.")


def main(args=None):
    rclpy.init(args=args)
    node = MoveToNode()
    # Single-threaded executor: the node only serves /modular_arm/move_to and
    # sends fire-and-forget action goals. A MultiThreadedExecutor spins idle
    # threads (visible as 80%+ CPU) even with no callbacks.
    executor = rclpy.executors.SingleThreadedExecutor()
    executor.add_node(node)
    try:
        executor.spin()
    finally:
        executor.shutdown()
        node.destroy_node()
        rclpy.shutdown()


if __name__ == "__main__":
    main()
