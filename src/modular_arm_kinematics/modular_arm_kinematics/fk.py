"""Forward kinematics for the real robot arm.

Geometry derived from robot_arm_description/urdf/robot_arm.urdf:

    joint1 (theta1): yaw about Z at base height 0.07 m.
    joint2 (theta2): shoulder pitch about Y, joint origin (-0.02, 0, 0.04).
    joint3 (theta3): elbow pitch about Y, joint origin (0.047, 0, 0.1925).
    joint4 (theta4): wrist pitch about Y, joint origin (0.141, 0, -0.001).
    gripper_link:    fixed at (0.052, 0, -0.008) from joint4.

Segments between joints are NOT collinear at zero pose; each carries a
fixed offset.  The arm works in a vertical plane selected by theta1.
Within that plane, a segment vector (a, b) (h = horizontal, z = vertical)
rotates with the joint sum phi about the Y axis as:

    R(phi)(a, b) = (a*cos(phi) + b*sin(phi), -a*sin(phi) + b*cos(phi))

End-effector pitch: 0 = horizontal, -pi/2 = pointing straight down.
pitch = -(theta2 + theta3 + theta4).

This module has no rclpy/ROS dependency on purpose.
"""
from dataclasses import dataclass
import math

# --- URDF geometry constants (keep in sync with robot_arm.urdf) ---
BASE_H = 0.07          # joint1 height (ground -> joint1)
SHOULDER = (-0.02, 0.11)  # joint2 position in (h, z) plane: (-0.02, 0.07+0.04)
SEG1 = (0.047, 0.1925)  # joint2 -> joint3 offset in (h, z) plane
SEG2 = (0.141, -0.001)  # joint3 -> joint4 offset in (h, z) plane
SEG3 = (0.052, -0.008)  # joint4 -> gripper_link offset in (h, z) plane

L1 = math.hypot(*SEG1) # * is used to unpack the tuple into two arguments for hypot
L2 = math.hypot(*SEG2)
L3 = math.hypot(*SEG3)
A1 = math.atan2(SEG1[1], SEG1[0])
A2 = math.atan2(SEG2[1], SEG2[0])
DELTA = A2 - A1 # angle between SEG1 and SEG2, used in inverse kinematics


def _rot(phi, vec):
    """Rotate a 2D (h, z) vector about the Y axis by *phi* radians."""
    a, b = vec
    return (a * math.cos(phi) + b * math.sin(phi),
            -a * math.sin(phi) + b * math.cos(phi))


@dataclass
class Pose:
    x: float
    y: float
    z: float
    pitch: float  # absolute end-effector pitch, radians, 0 = horizontal


def forward_kinematics(theta1: float, theta2: float, theta3: float, theta4: float) -> Pose:
    """Compute the gripper_link pose from joint angles (radians)."""
    s1 = _rot(theta2, SEG1)
    s2 = _rot(theta2 + theta3, SEG2)
    s3 = _rot(theta2 + theta3 + theta4, SEG3)

    h = SHOULDER[0] + s1[0] + s2[0] + s3[0]
    z = SHOULDER[1] + s1[1] + s2[1] + s3[1]

    x = h * math.cos(theta1)
    y = h * math.sin(theta1)
    pitch = -(theta2 + theta3 + theta4)

    return Pose(x=x, y=y, z=z, pitch=pitch)


if __name__ == "__main__":
    pose = forward_kinematics(0.0, 0.0, 0.0, 0.0)
    print(f"Zero pose:  x={pose.x:.3f}  z={pose.z:.3f}  pitch={pose.pitch:.3f}  (expect x=0.22 z=0.2935 pitch=0)")
