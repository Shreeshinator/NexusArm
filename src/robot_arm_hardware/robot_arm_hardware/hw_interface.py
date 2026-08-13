"""hw_interface — real-robot bridge for the Arduino Uno R3 servo bridge.

Subscribes to /joint_command (std_msgs/Float64MultiArray, 5 values:
[joint1, joint2, joint3, joint4, gripper]) and forwards each command as a
newline-terminated CSV line to the Arduino over serial.  Republishes the last
commanded values as /joint_states (the real servos have no position feedback,
so this is the commanded pose — the accepted approximation from the arch doc).

This is the ONLY piece that differs between sim and real; everything upstream
(move_to, teleop, LeRobot recorder) sees identical topics.  To run on Uno Q,
bind the R3's serial device into the Docker container and set the
serial_port parameter to the in-container device path.

Run:
    ros2 run robot_arm_hardware hw_interface --ros-args -p serial_port:=/dev/ttyACM0
"""
import time

import rclpy
from rclpy.node import Node
from sensor_msgs.msg import JointState
from std_msgs.msg import Float64MultiArray

try:
    import serial
except ImportError:
    serial = None

# Order MUST match the Arduino sketch and the architecture contract.
JOINT_NAMES = ["joint1", "joint2", "joint3", "joint4", "gripper_joint"]


class HWInterface(Node):
    def __init__(self):
        super().__init__("real_hw_interface")

        self.declare_parameter("serial_port", "/dev/ttyACM0")
        self.declare_parameter("baud_rate", 115200)
        self.declare_parameter("publish_rate", 20.0)

        self._port = self.get_parameter("serial_port").get_parameter_value().string_value
        self._baud = self.get_parameter("baud_rate").get_parameter_value().integer_value
        self._rate = self.get_parameter("publish_rate").get_parameter_value().double_value

        if serial is None:
            raise RuntimeError("pyserial not installed. Run: pip install pyserial")

        try:
            self._ser = serial.Serial(self._port, self._baud, timeout=0.1)
            time.sleep(2.0)
            self._ser.reset_input_buffer()
        except serial.SerialException as exc:
            raise RuntimeError(f"Cannot open {self._port}: {exc}")

        self._cmd = [0.0] * 5
        self._sub = self.create_subscription(
            Float64MultiArray, "/joint_command", self._on_cmd, 10
        )
        self._pub = self.create_publisher(JointState, "/joint_states", 10)
        self._timer = self.create_timer(1.0 / max(self._rate, 1.0), self._publish_state)
        self.get_logger().info(f"hw_interface ready on {self._port} @ {self._baud}")

    def _on_cmd(self, msg: Float64MultiArray):
        if len(msg.data) != 5:
            self.get_logger().warn(
                f"/joint_command expected 5 values, got {len(msg.data)}; ignoring"
            )
            return
        self._cmd = [float(x) for x in msg.data]
        line = ",".join(f"{x:.5f}" for x in self._cmd) + "\n"
        try:
            self._ser.write(line.encode("ascii"))
        except serial.SerialException as exc:
            self.get_logger().error(f"Serial write failed: {exc}")

    def _publish_state(self):
        js = JointState()
        js.name = list(JOINT_NAMES)
        js.position = list(self._cmd)
        self._pub.publish(js)

    def destroy_node(self):
        if getattr(self, "_ser", None) is not None and self._ser.is_open:
            self._ser.close()
        super().destroy_node()


def main(args=None):
    rclpy.init(args=args)
    node = HWInterface()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == "__main__":
    main()
