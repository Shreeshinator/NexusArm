"""keyboard_teleop — real-robot Cartesian teleop (mirror of the sim one).

Drives the real arm via the /modular_arm/move_to service (served by hw_move_to,
which publishes /joint_command to the Arduino servo bridge).  Also sends
recorder start/save/discard/finish commands on /lerobot_recorder/command.

The action stream for the LeRobot recorder comes from /joint_command (published
by hw_move_to), so this node only needs to call the service and manage recording.

Controls (press keys in the SAME terminal; hold to repeat):
    w/a/s/d   X/Y coarse    i/j/k/l  X/Y fine
    q/e       Z up/down     u/o      Z fine
    r/f       pitch ±0.1    [ / ]    wrist (joint4) ±0.05
    h         return to start pose (opens gripper)
    space     gripper toggle
    x         print target
    ENTER     recorder start/save   t  discard   y  finish
    Ctrl-C    quit

Run:
    ros2 run robot_arm_hardware keyboard_teleop
"""
import math
import select
import sys
import termios
import threading
import tty

import rclpy
from rclpy.node import Node
from std_msgs.msg import Float64MultiArray, String

from modular_arm_interfaces.srv import MoveTo

from .ik import inverse_kinematics, Unreachable

COARSE = 0.01
FINE = 0.002
PITCH_STEP = 0.1
WRIST_STEP = 0.05  # rad per [ / ] press (direct wrist joint4 rotation)
MOVE_DURATION = 0.1  # seconds per retarget (non-blocking: held keys stream smoothly)
START = {"x": 0.27, "y": 0.0, "z": 0.08, "pitch": -1.57}  # reachable gripper-down start pose
# Joint order on /joint_command (matches hw_interface + Arduino firmware).
JOINT_NAMES = ["joint1", "joint2", "joint3", "joint4", "gripper_joint"]


def _read_key_blocking():
    fd = sys.stdin.fileno()
    old = termios.tcgetattr(fd)
    try:
        tty.setraw(fd)
        while True:
            r, _, _ = select.select([fd], [], [], 0.1)
            if not r:
                continue
            ch = sys.stdin.read(1)
            if ch in ("\x03", "\x04"):
                return None
            return ch
    finally:
        termios.tcsetattr(fd, termios.TCSADRAIN, old)


class KeyboardTeleop(Node):
    def __init__(self):
        super().__init__("keyboard_teleop")
        self._client = self.create_client(MoveTo, "/modular_arm/move_to")
        self._rec_pub = self.create_publisher(String, "/lerobot_recorder/command", 10)
        # Direct wrist (joint4) moves bypass IK and publish the full joint pose
        # straight to /joint_command (the same topic hw_interface reads).
        self._joint_pub = self.create_publisher(Float64MultiArray, "/joint_command", 10)

        self.target = dict(START)
        self.gripper = 0.0
        # Last joint solution the service returned ([j1..j4, gripper]);
        # used as the base for direct wrist moves.
        self.last_joints = [0.0, 0.0, 0.0, 0.0, 0.0]
        self.lock = threading.Lock()
        self.running = True
        self._recording = False

        while not self._client.wait_for_service(timeout_sec=1.0):
            self.get_logger().info("waiting for /modular_arm/move_to service ...")

        self.get_logger().info("move_to service found.  Ready.")

    def _rec_cmd(self, cmd):
        msg = String()
        msg.data = cmd
        self._rec_pub.publish(msg)
        self.get_logger().info(f"[recorder] {cmd}")

    def _toggle_record(self):
        if self._recording:
            self._rec_cmd("save")
            self._recording = False
        else:
            self._rec_cmd("start")
            self._recording = True

    def _send(self):
        with self.lock:
            target = dict(self.target)
            gripper = self.gripper
        req = MoveTo.Request()
        req.x = target["x"]
        req.y = target["y"]
        req.z = target["z"]
        req.pitch = target["pitch"]
        req.elbow = ""
        req.gripper = gripper
        req.duration_sec = MOVE_DURATION

        future = self._client.call_async(req)
        rclpy.spin_until_future_complete(self, future, timeout_sec=1.0)
        if not future.done():
            self.get_logger().warn("move_to call timed out")
            return False
        resp = future.result()
        if resp is None or not resp.success:
            self.get_logger().warn(f"move_to rejected: {getattr(resp, 'message', 'no response')}")
            return False
        # Remember the solved joint pose so direct wrist moves build on it.
        if len(resp.joint_angles) == 5:
            with self.lock:
                self.last_joints = list(resp.joint_angles)
        return True

    def _publish_wrist(self):
        """Publish the full joint pose with joint4 adjusted, straight to
        /joint_command. hw_interface clamps to firmware limits and the arm
        moves smoothly; the recorder still sees the commanded action."""
        msg = Float64MultiArray()
        msg.data = list(self.last_joints)
        self._joint_pub.publish(msg)

    def _tilt_wrist(self, sign):
        """Direct wrist (joint4) rotation: tilt the gripper without moving the
        rest of the arm (no IK redistribution). The wrist is published straight
        to /joint_command, so return False to skip _send().

        To keep the gripper orientation (end-effector pitch) consistent across
        the NEXT Cartesian move, the stored target pitch is synced:
        pitch = -(t2+t3+t4), so a +delta in joint4 means -delta in pitch.
        (joint4 itself will redistribute slightly on the next move -- that is
        unavoidable when x/z/pitch are all fixed -- but the gripper orientation
        you set with [ / ] is preserved.)

        No-op when joint4 is at its limit, or when the resulting pitch would
        make the next Cartesian move unreachable (avoids 'out of reach')."""
        with self.lock:
            new_j4 = max(-1.57, min(1.57, self.last_joints[3] + sign * WRIST_STEP))
            if new_j4 == self.last_joints[3]:
                return False  # at joint4 limit: nothing to do
            delta = new_j4 - self.last_joints[3]
            new_pitch = self.target["pitch"] - delta
            try:
                inverse_kinematics(
                    self.target["x"], self.target["y"], self.target["z"], new_pitch
                )
            except Unreachable:
                return False  # would dead-end the next move
            self.last_joints[3] = new_j4
            self.target["pitch"] = new_pitch
            self._publish_wrist()
        return False

    def _revert(self, prev_target, prev_gripper):
        self.target = prev_target
        self.gripper = prev_gripper

    def _step(self, key):
        t = self.target
        if key == "w":
            t["x"] += COARSE
        elif key == "s":
            t["x"] -= COARSE
        elif key == "a":
            t["y"] += COARSE
        elif key == "d":
            t["y"] -= COARSE
        elif key == "q":
            t["z"] += COARSE
        elif key == "e":
            t["z"] -= COARSE
        elif key == "i":
            t["x"] += FINE
        elif key == "k":
            t["x"] -= FINE
        elif key == "j":
            t["y"] += FINE
        elif key == "l":
            t["y"] -= FINE
        elif key == "u":
            t["z"] += FINE
        elif key == "o":
            t["z"] -= FINE
        elif key == "r":
            t["pitch"] += PITCH_STEP
        elif key == "f":
            t["pitch"] -= PITCH_STEP
        elif key == "h":  # home: return to reachable gripper-down START pose + open gripper
            t["x"] = START["x"]
            t["y"] = START["y"]
            t["z"] = START["z"]
            t["pitch"] = START["pitch"]
            self.gripper = 0.0
        elif key == "[":
            # Direct wrist (joint4) rotation: tilt the gripper without moving
            # the rest of the arm (no IK redistribution). Already published
            # straight to /joint_command, so return False to skip _send().
            # Keep target["pitch"] in sync (pitch = -(t2+t3+t4)) so the next
            # Cartesian move re-solves IK with the new wrist angle instead of
            # snapping joint4 back to its pre-tilt value.
            return self._tilt_wrist(+1)
        elif key == "]":
            return self._tilt_wrist(-1)
        elif key == " ":
            self.gripper = 1.0 if self.gripper < 0.5 else 0.0
            self.get_logger().info(f"gripper -> {self.gripper:.1f}")
        elif key == "x":
            self.get_logger().info(
                f"target x={t['x']:.3f} y={t['y']:.3f} z={t['z']:.3f} "
                f"pitch={t['pitch']:.3f} gripper={self.gripper:.1f}")
        elif key in ("\r", "\n"):
            self._toggle_record()
        elif key == "t":
            self._rec_cmd("discard")
            self._recording = False
        elif key == "y":
            self._rec_cmd("finish")
            self.running = False
        else:
            return False
        return True

    def run(self):
        print("=" * 60)
        print("Keyboard teleop (real)  ->  /modular_arm/move_to")
        print("  w/a/s/d  X/Y coarse    i/j/k/l  X/Y fine")
        print("  q/e      Z up/down     u/o      Z fine")
        print("  r/f      pitch ±0.1    [ / ]    wrist (joint4) ±0.05")
        print("  h        return to start pose (opens gripper)")
        print("  space    gripper toggle")
        print("  x        print target")
        print("  ENTER    recorder start/save   t  discard   y  finish")
        print("  Ctrl-C   quit")
        print("=" * 60, flush=True)
        self.get_logger().info(
            "Moving to reachable gripper-down start pose "
            f"({START['x']}, {START['y']}, {START['z']}, pitch {START['pitch']}) ..."
        )
        if not self._send():
            self.get_logger().error("Startup move to gripper-down pose FAILED. Check IK reachability / service.")
        while self.running and rclpy.ok():
            key = _read_key_blocking()
            if key is None:
                break
            with self.lock:
                prev_target = dict(self.target)
                prev_gripper = self.gripper
            if self._step(key):
                if not self._send():
                    self._revert(prev_target, prev_gripper)
                    self.get_logger().info("move rejected; target reverted")


def main(args=None):
    rclpy.init(args=args)
    node = KeyboardTeleop()
    try:
        node.run()
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == "__main__":
    main()
