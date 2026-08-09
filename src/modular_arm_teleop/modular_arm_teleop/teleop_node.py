"""Teleoperation node: reads Arduino leader arm over serial, commands the simulated arm.

Serial format (CSV):  j1,j2,j3,j4,btn\\n
  j1..j4 = raw 10-bit ADC readings (0-1023) from potentiometers
  btn    = 0 (pressed = gripper close) or 1 (released = gripper open)

The node maps pot readings to follower joint angles and sends them as
FollowJointTrajectory goals to the existing arm_controller.
"""

import math
import threading
import time

import rclpy
from rclpy.action import ActionClient
from rclpy.callback_groups import ReentrantCallbackGroup
from rclpy.node import Node

from control_msgs.action import FollowJointTrajectory
from trajectory_msgs.msg import JointTrajectoryPoint

try:
    import serial
except ImportError:
    serial = None


JOINT_NAMES = ["joint1", "joint2", "joint3", "joint4", "finger_left_joint", "finger_right_joint"]
ACTION_NAME = "/arm_controller/follow_joint_trajectory"


class TeleopNode(Node):
    def __init__(self):
        super().__init__("teleop_node")

        self.declare_parameter("serial_port", "/dev/ttyACM0")
        self.declare_parameter("baud_rate", 115200)
        self.declare_parameter("publish_rate", 25.0)
        self.declare_parameter("deadband", 3)
        self.declare_parameter("trajectory_duration_ms", 100)
        self.declare_parameter("pot_min", 170)
        self.declare_parameter("pot_max", 853)

        self.declare_parameter("joint_mapping.joint1.scale", 6.28318)
        self.declare_parameter("joint_mapping.joint1.offset", -3.14159)
        self.declare_parameter("joint_mapping.joint2.scale", -2.0)
        self.declare_parameter("joint_mapping.joint2.offset", 2.0)
        self.declare_parameter("joint_mapping.joint3.scale", 1.0)
        self.declare_parameter("joint_mapping.joint3.offset", -1.5)
        self.declare_parameter("joint_mapping.joint4.scale", 1.5708)
        self.declare_parameter("joint_mapping.joint4.offset", -1.3708)

        self.declare_parameter("joint_limits.joint1", [-3.14159, 3.14159])
        self.declare_parameter("joint_limits.joint2", [-1.5708, 3.14159])
        self.declare_parameter("joint_limits.joint3", [-3.14159, 3.14159])
        self.declare_parameter("joint_limits.joint4", [-3.14159, 3.14159])

        self.declare_parameter("gripper_open_pos", 0.0)
        self.declare_parameter("gripper_close_pos", 0.0075)

        self._load_params()

        self._action_client = ActionClient(
            self,
            FollowJointTrajectory,
            ACTION_NAME,
            callback_group=ReentrantCallbackGroup(),
        )

        self._last_raw = None
        self._serial_lock = threading.Lock()
        self._serial = None
        self._running = False
        self._serial_thread = None

        self.get_logger().info(
            f"Teleop node initialised.  Awaiting action server '{ACTION_NAME}' ..."
        )

        if not self._action_client.wait_for_server(timeout_sec=10.0):
            self.get_logger().error(
                f"Action server '{ACTION_NAME}' not available after 10 s."
            )
            return

        self.get_logger().info("Action server found.  Opening serial port ...")
        self._open_serial()
        if self._serial is None:
            return

        self._running = True
        self._serial_thread = threading.Thread(target=self._serial_loop, daemon=True)
        self._serial_thread.start()
        self.get_logger().info("Teleop active - move the leader arm!")

    def _load_params(self):
        self._serial_port = (
            self.get_parameter("serial_port").get_parameter_value().string_value
        )
        self._baud_rate = (
            self.get_parameter("baud_rate").get_parameter_value().integer_value
        )
        self._publish_rate = (
            self.get_parameter("publish_rate").get_parameter_value().double_value
        )
        self._deadband = (
            self.get_parameter("deadband").get_parameter_value().integer_value
        )
        self._trajectory_duration_ms = (
            self.get_parameter("trajectory_duration_ms")
            .get_parameter_value()
            .integer_value
        )
        self._pot_min = (
            self.get_parameter("pot_min").get_parameter_value().integer_value
        )
        self._pot_max = (
            self.get_parameter("pot_max").get_parameter_value().integer_value
        )
        self._pot_range = self._pot_max - self._pot_min
        if self._pot_range <= 0:
            self._pot_range = 1

        self._mapping = {}
        for name in ["joint1", "joint2", "joint3", "joint4"]:
            scale = (
                self.get_parameter(f"joint_mapping.{name}.scale")
                .get_parameter_value()
                .double_value
            )
            offset = (
                self.get_parameter(f"joint_mapping.{name}.offset")
                .get_parameter_value()
                .double_value
            )
            self._mapping[name] = (scale, offset)

        self._limits = {}
        for name in ["joint1", "joint2", "joint3", "joint4"]:
            limits = (
                self.get_parameter(f"joint_limits.{name}")
                .get_parameter_value()
                .double_array_value
            )
            self._limits[name] = (limits[0], limits[1])

        self._gripper_open_pos = (
            self.get_parameter("gripper_open_pos")
            .get_parameter_value()
            .double_value
        )
        self._gripper_close_pos = (
            self.get_parameter("gripper_close_pos")
            .get_parameter_value()
            .double_value
        )

    def _open_serial(self):
        if serial is None:
            self.get_logger().error(
                "pyserial not installed. Run: pip install pyserial"
            )
            return
        try:
            self._serial = serial.Serial(
                self._serial_port, self._baud_rate, timeout=0.1
            )
            time.sleep(2.0)
            self._serial.reset_input_buffer()
            self.get_logger().info(f"Connected to {self._serial_port}")
        except serial.SerialException as exc:
            self.get_logger().error(f"Cannot open {self._serial_port}: {exc}")

    def _serial_loop(self):
        period = 1.0 / max(self._publish_rate, 1.0)
        buffer = ""
        last_send = 0.0

        while self._running:
            try:
                with self._serial_lock:
                    if self._serial is None or not self._serial.is_open:
                        time.sleep(0.5)
                        continue
                    while self._serial.in_waiting > 0:
                        ch = self._serial.read().decode("utf-8", errors="ignore")
                        if ch == "\n":
                            line = buffer.strip()
                            buffer = ""
                            parsed = self._parse_line(line)
                            if parsed is not None:
                                now = time.time()
                                if now - last_send >= period:
                                    self._send_command(parsed)
                                    last_send = now
                        else:
                            buffer += ch
            except (serial.SerialException, OSError) as exc:
                self.get_logger().warn(f"Serial error: {exc}")
                time.sleep(0.5)
                continue

            time.sleep(0.001)

    def _parse_line(self, line: str):
        parts = line.strip().split(",")
        if len(parts) < 5:
            return None
        try:
            j1, j2, j3, j4 = int(parts[0]), int(parts[1]), int(parts[2]), int(parts[3])
            btn = int(parts[4])
        except ValueError:
            return None
        return (j1, j2, j3, j4, btn)

    def _raw_to_angles(self, j1, j2, j3, j4, btn):
        raw = [j1, j2, j3, j4]
        angles = []
        for i, name in enumerate(["joint1", "joint2", "joint3", "joint4"]):
            unit = float(raw[i] - self._pot_min) / float(self._pot_range)
            unit = max(0.0, min(1.0, unit))

            scale, offset = self._mapping[name]
            angle = scale * unit + offset

            lo, hi = self._limits[name]
            angle = max(lo, min(hi, angle))
            angles.append(angle)

        if btn == 0:
            gripper_pos = self._gripper_close_pos
        else:
            gripper_pos = self._gripper_open_pos
        angles.append(gripper_pos)
        angles.append(gripper_pos)

        return angles

    def _send_command(self, parsed):
        if self._last_raw is not None:
            if all(abs(a - b) <= self._deadband for a, b in zip(parsed[:4], self._last_raw[:4])):
                return
        self._last_raw = parsed

        j1, j2, j3, j4, btn = parsed
        angles = self._raw_to_angles(j1, j2, j3, j4, btn)

        goal = FollowJointTrajectory.Goal()
        goal.trajectory.joint_names = JOINT_NAMES

        point = JointTrajectoryPoint()
        point.positions = angles
        point.velocities = [0.0] * len(JOINT_NAMES)
        td_ns = self._trajectory_duration_ms * 1_000_000
        point.time_from_start.sec = int(td_ns // 1_000_000_000)
        point.time_from_start.nanosec = int(td_ns % 1_000_000_000)

        goal.trajectory.points = [point]

        self._action_client.send_goal_async(goal)

    def destroy_node(self):
        self._running = False
        if self._serial_thread is not None:
            self._serial_thread.join(timeout=2.0)
        with self._serial_lock:
            if self._serial is not None:
                self._serial.close()
                self._serial = None
        super().destroy_node()


def main(args=None):
    rclpy.init(args=args)
    node = TeleopNode()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == "__main__":
    main()
