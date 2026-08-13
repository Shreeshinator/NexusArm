"""joint_keyboard_teleop — drive the real arm in JOINT space for quick testing.

Publishes std_msgs/Float64MultiArray to /joint_command (the architecture
contract), which hw_interface turns into servo PWM via the Arduino.  Use this to
verify mechanical travel and tune the servo CALIBRATION table before any
LeRobot/camera work.

Controls (press keys in the SAME terminal):
    q / a   joint1 base yaw   +/-
    w / s   joint2 shoulder   +/-
    e / d   joint3 elbow      +/-
    r / f   joint4 wrist      +/-
    g / h   gripper close/open (0.0 / 1.0)
    z       home (all zero, gripper open)
    x       print current pose
    Ctrl-C  quit

Run:
    ros2 run robot_arm_hardware joint_keyboard_teleop
"""
import select
import sys
import termios
import tty

import rclpy
from rclpy.node import Node
from std_msgs.msg import Float64MultiArray

JOINT_NAMES = ["joint1", "joint2", "joint3", "joint4", "gripper_joint"]
ARM_STEP = 0.05      # rad per keypress
HOME = [0.0, 0.0, 0.0, 0.0, 0.0]


def _read_key():
    fd = sys.stdin.fileno()
    old = termios.tcgetattr(fd)
    try:
        tty.setraw(fd)
        while True:
            r, _, _ = select.select([fd], [], [], 0.1)
            if r:
                ch = sys.stdin.read(1)
                if ch in ("\x03", "\x04"):
                    return None
                return ch
    finally:
        termios.tcsetattr(fd, termios.TCSADRAIN, old)


class JointTeleop(Node):
    def __init__(self):
        super().__init__("joint_keyboard_teleop")
        self._pub = self.create_publisher(Float64MultiArray, "/joint_command", 10)
        self._pose = list(HOME)

    def _send(self):
        msg = Float64MultiArray()
        msg.data = list(self._pose)
        self._pub.publish(msg)

    def _step(self, key):
        p = self._pose
        if key == "q":
            p[0] += ARM_STEP
        elif key == "a":
            p[0] -= ARM_STEP
        elif key == "w":
            p[1] += ARM_STEP
        elif key == "s":
            p[1] -= ARM_STEP
        elif key == "e":
            p[2] += ARM_STEP
        elif key == "d":
            p[2] -= ARM_STEP
        elif key == "r":
            p[3] += ARM_STEP
        elif key == "f":
            p[3] -= ARM_STEP
        elif key == "g":
            p[4] = 1.0
        elif key == "h":
            p[4] = 0.0
        elif key == "z":
            self._pose = list(HOME)
        elif key == "x":
            self.get_logger().info(
                f"pose j1={p[0]:.2f} j2={p[1]:.2f} j3={p[2]:.2f} "
                f"j4={p[3]:.2f} grip={p[4]:.1f}"
            )
        else:
            return False
        return True

    def run(self):
        print("=" * 56)
        print("Joint-space keyboard teleop  ->  /joint_command")
        print("  q/a base  w/s shoulder  e/d elbow  r/f wrist")
        print("  g close gripper   h open gripper   z home   x print")
        print("  Ctrl-C quit")
        print("=" * 56, flush=True)
        while rclpy.ok():
            key = _read_key()
            if key is None:
                break
            if self._step(key):
                self._send()


def main(args=None):
    rclpy.init(args=args)
    node = JointTeleop()
    try:
        node.run()
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == "__main__":
    main()
