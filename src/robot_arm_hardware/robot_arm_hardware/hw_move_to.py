"""hw_move_to — real-robot Cartesian control service (drop-in for move_to_node).

Mirror of modular_arm_kinematics/move_to_node, but instead of sending a
FollowJointTrajectory goal to the simulated /arm_controller, it publishes the
solved joint angles on /joint_command (std_msgs/Float64MultiArray, 5 values:
[joint1, joint2, joint3, joint4, gripper]) which hw_interface forwards to the
Arduino servo bridge.  The shoulder's two opposed servos are handled entirely
in firmware, so this node sees the same 4 arm joints as the sim.

It smoothly interpolates from the current pose to the target over duration_sec
(publishing /joint_command at ~30 Hz) so the real servos don't jerk.

Run on the real robot instead of move_to_node:
    ros2 run robot_arm_hardware hw_move_to
"""
import math
import threading
import time

import rclpy
from rclpy.node import Node
from std_msgs.msg import Float64MultiArray

from modular_arm_interfaces.srv import MoveTo

from .ik import inverse_kinematics, Unreachable

# Order MUST match the Arduino servo_bridge.ino and the architecture contract.
JOINT_NAMES = ["joint1", "joint2", "joint3", "joint4", "gripper_joint"]
CMD_RATE = 30.0  # Hz at which we stream interpolated /joint_command


class HwMoveTo(Node):
    def __init__(self):
        super().__init__("hw_move_to")

        self._pub = self.create_publisher(Float64MultiArray, "/joint_command", 10)
        self._srv = self.create_service(MoveTo, "/modular_arm/move_to", self._handle_move_to)

        self._current = [0.0, 0.0, 0.0, 0.0, 0.0]  # [4 arm angles, gripper]
        self._lock = threading.Lock()
        self._running = True

        self.get_logger().info("hw_move_to ready on /modular_arm/move_to")

    def _handle_move_to(self, request: MoveTo.Request, response: MoveTo.Response) -> MoveTo.Response:
        try:
            sol = inverse_kinematics(
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

        grip = max(0.0, min(1.0, request.gripper))
        target = sol.as_list() + [grip]  # 5 values: 4 arm + gripper(0..1)
        duration = request.duration_sec if request.duration_sec > 0.0 else 1.0

        self._exec_trajectory(target, duration)

        response.success = True
        response.joint_angles = target
        response.message = "Trajectory sent to /joint_command."
        return response

    def _exec_trajectory(self, target, duration):
        with self._lock:
            start = list(self._current)
        steps = max(1, int(round(duration * CMD_RATE)))
        dt = 1.0 / CMD_RATE
        for i in range(1, steps + 1):
            if not self._running or not rclpy.ok():
                break
            a = i / steps
            pose = [start[k] + (target[k] - start[k]) * a for k in range(5)]
            self._publish(pose)
            with self._lock:
                self._current = pose
            time.sleep(dt)
        # Ensure we land exactly on target.
        self._publish(target)
        with self._lock:
            self._current = list(target)

    def _publish(self, pose):
        msg = Float64MultiArray()
        msg.data = pose
        self._pub.publish(msg)

    def destroy_node(self):
        self._running = False
        super().destroy_node()


def main(args=None):
    rclpy.init(args=args)
    node = HwMoveTo()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == "__main__":
    main()
