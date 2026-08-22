"""Keyboard teleop for the SIMULATED arm (Gazebo) via the /modular_arm/move_to service.

NOT for the real robot -- the real-robot teleop lives in the robot_arm_hardware
package (ros2 run robot_arm_hardware keyboard_teleop).

Moves the arm in Cartesian increments and toggles the gripper.  Also publishes
the *commanded* joint angles on /joint_commands (JointState) so a LeRobot
recorder can use them as the action feature.

Run:
    ros2 run modular_arm_kinematics keyboard_teleop
"""
import select # for select.select() to seek for keyboard input without blocking 
import sys    # for sys.stdin to read keyboard input 
import termios  # for termios.tcgetattr() and termios.tcsetattr() to change terminal settings

import threading # threading needed to protect shared state (target and gripper) between the keyboard thread and the ROS2 callbacks

import tty # for tty.setraw() to set the terminal to raw mode so we can read one key at a time without waiting for Enter

import rclpy
from rclpy.node import Node
from sensor_msgs.msg import JointState
from std_msgs.msg import String

from modular_arm_interfaces.srv import MoveTo

JOINT_NAMES = ["joint1", "joint2", "joint3", "joint4", "finger_left_joint", "finger_right_joint"]

COARSE = 0.02
FINE = 0.005
PITCH_STEP = 0.2

START = {"x": 0.27, "y": 0.0, "z": 0.08, "pitch": -1.57}


def _read_key_blocking():
    """Read one key press, returning an uppercase token or None on Ctrl-C."""
    fd = sys.stdin.fileno() # fd is the file descriptor for stdin (keyboard input, usually 0)
    old = termios.tcgetattr(fd) # get the current terminal settings for stdin, because we will change them to raw mode to read one key at a time
    try:
        tty.setraw(fd) # set the terminal to raw mode, so we can read one key at a time without waiting for Enter
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
        self._pub = self.create_publisher(JointState, "/joint_commands", 10)
        self._rec_pub = self.create_publisher(String, "/lerobot_recorder/command", 10)

        self.target = dict(START)
        self.gripper = 0.0
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
        req.duration_sec = 0.5

        future = self._client.call_async(req)
        # Don't block the keyboard thread forever; use a wait helper.
        rclpy.spin_until_future_complete(self, future, timeout_sec=5.0)
        if not future.done():
            self.get_logger().warn("move_to call timed out")
            return
        resp = future.result()
        if resp is None:
            self.get_logger().warn("move_to call failed (no response)")
            return
        if not resp.success:
            self.get_logger().warn(f"move_to rejected: {resp.message}")
            return
        if len(resp.joint_angles) == len(JOINT_NAMES):
            js = JointState()
            js.name = list(JOINT_NAMES)
            js.position = list(resp.joint_angles)
            self._pub.publish(js)

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
        elif key == " ":
            self.gripper = 1.0 if self.gripper < 0.5 else 0.0
            self.get_logger().info(f"gripper -> {self.gripper:.1f}")
        elif key == "x":
            self.get_logger().info(
                f"target x={t['x']:.3f} y={t['y']:.3f} z={t['z']:.3f} pitch={t['pitch']:.3f} "
                f"gripper={self.gripper:.1f}")
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
        print("Keyboard teleop  (+ recorder control)")
        print("  w/a/s/d  X/Y coarse    i/j/k/l  X/Y fine")
        print("  q/e      Z up/down     u/o      Z fine")
        print("  r/f      pitch ±0.2    space    gripper toggle")
        print("  x        print target")
        print("  ENTER    recorder start/save   t  discard   y  finish")
        print("  Ctrl-C   quit")
        print("=" * 60, flush=True)
        while self.running and rclpy.ok():
            key = _read_key_blocking()
            if key is None:
                break
            if self._step(key):
                self._send()


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
