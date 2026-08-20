"""hw_move_to — real-robot Cartesian control service (drop-in for move_to_node).

Mirror of modular_arm_kinematics/move_to_node, but instead of sending a
FollowJointTrajectory goal to the simulated /arm_controller, it publishes the
solved joint angles on /joint_command (std_msgs/Float64MultiArray, 5 values:
[joint1, joint2, joint3, joint4, gripper]) which hw_interface forwards to the
Arduino servo bridge.  The shoulder's two opposed servos are handled entirely
in firmware, so this node sees the same 4 arm joints as the sim.

It smoothly interpolates from the current pose to the target over duration_sec
(publishing /joint_command at ~50 Hz) so the real servos don't jerk.

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
CMD_RATE = 50.0  # Hz at which we stream interpolated /joint_command


class HwMoveTo(Node):
    def __init__(self):
        super().__init__("hw_move_to")

        self._pub = self.create_publisher(Float64MultiArray, "/joint_command", 10)
        self._srv = self.create_service(MoveTo, "/modular_arm/move_to", self._handle_move_to)

        self._current = [0.0, 0.0, 0.0, 0.0, 0.0]  # [4 arm angles, gripper]
        self._lock = threading.Lock() # lock is used to ensure that only one thread can access the shared resource (in this case, the _current joint angles) at a time. This prevents race conditions and ensures thread safety when multiple threads
        self._running = True

        # Non-blocking trajectory: the service callback only *starts* a plan;
        # a timer steps through it so rapid retargets (held keys / streaming)
        # flow smoothly instead of queueing behind a blocking loop.
        self._plan = None
        self._timer = self.create_timer(1.0 / CMD_RATE, self._tick)

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

        grip = max(0.0, min(1.0, request.gripper)) # clamp gripper to [0, 1]
        target = sol.as_list() + [grip]  # 5 values: 4 arm + gripper(0..1)
        duration = request.duration_sec if request.duration_sec > 0.0 else 1.0

        self._start_plan(target, duration) # stream the trajectory to /joint_command

        response.success = True
        response.joint_angles = target
        response.message = "Trajectory sent to /joint_command."
        return response

    def _start_plan(self, target, duration):
        """Begin interpolating toward *target*; the timer continues the motion."""
        steps = max(1, int(round(duration * CMD_RATE)))
        with self._lock:
            start = list(self._current)
            self._plan = {
                "start": start,
                "target": list(target),
                "steps": steps,
                "i": 0,
                "t0": time.monotonic(),
            }

    def _tick(self):
        """Timer callback: publish one interpolated step (smoothstep-eased)."""
        # Snapshot plan + increment i atomically under lock — no torn dict.
        with self._lock:
            plan = self._plan
            if plan is None:
                return
            if not self._running or not rclpy.ok():
                return
            plan["i"] += 1
            i = plan["i"]
            steps = plan["steps"]
            start = plan["start"]
            target = plan["target"]
        # Compute outside lock (no shared state) to keep lock short.
        # Smoothstep easing: zero velocity at start and end -> no jerk.
        a = min(i / steps, 1.0)
        a = a * a * (3.0 - 2.0 * a)
        pose = [start[k] + (target[k] - start[k]) * a for k in range(5)]
        self._publish(pose)
        with self._lock:
            self._current = pose
            if i >= steps:
                # Land exactly on target and end the plan.
                self._current = list(target)
                self._plan = None
                publish_target = True
            else:
                publish_target = False
        if publish_target:
            self._publish(target)

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
