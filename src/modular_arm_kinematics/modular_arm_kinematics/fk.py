"""Forward kinematics for the modular 4-DOF arm.

Geometry (must match modular_arm_description/urdf/modular_arm.urdf.xacro):

    joint1 (theta1): yaw about Z at the base, sets the vertical plane
                      the rest of the arm operates in.
    joint2 (theta2): shoulder pitch.  theta2=0 → upper arm points
                      *backward* (-X).  Positive → sweeps upward toward +Z.
    joint3 (theta3): elbow pitch, relative to link2.
    joint4 (theta4): wrist pitch, relative to link3.

Within the plane selected by theta1, the arm is a 3-link planar chain
(L1, L2, L3) whose links point at *cumulative* absolute angles:
    phi2 = theta2
    phi3 = theta2 + theta3
    phi4 = theta2 + theta3 + theta4   (this is also the end-effector pitch)

Because the shoulder rests backward at theta2=0, the horizontal projection
of each link carries a minus sign:
    h = -(L1*cos(phi2) + L2*cos(phi3) + L3*cos(phi4))

This module has no rclpy/ROS dependency on purpose: it should be usable
standalone (unit tests, notebooks, a future LLM planner, etc.).
"""
from dataclasses import dataclass
import math

# Link lengths (meters) -- keep in sync with the xacro properties L0..L3.
L0 = 0.06  # ground -> shoulder height
L1 = 0.12  # shoulder -> elbow
L2 = 0.12  # elbow -> wrist
L3 = 0.08  # wrist -> end-effector tip


@dataclass
class Pose:
    x: float
    y: float
    z: float
    pitch: float  # absolute end-effector pitch, radians, 0 = horizontal


def forward_kinematics(theta1: float, theta2: float, theta3: float, theta4: float) -> Pose:
    """Compute end-effector pose from joint angles (radians)."""
    phi2 = theta2
    phi3 = theta2 + theta3
    phi4 = theta2 + theta3 + theta4

    h = -(L1 * math.cos(phi2) + L2 * math.cos(phi3) + L3 * math.cos(phi4))
    z = L0 + (L1 * math.sin(phi2)) + (L2 * math.sin(phi3)) + (L3 * math.sin(phi4))

    x = h * math.cos(theta1)
    y = h * math.sin(theta1)

    return Pose(x=x, y=y, z=z, pitch=phi4)


if __name__ == "__main__":
    # Zero pose: shoulder backward, arm straight behind base.
    pose = forward_kinematics(theta1=0.0, theta2=0.0, theta3=0.0, theta4=0.0)
    print(f"Zero pose:  x={pose.x:.2f}  (expect -{L1+L2+L3:.2f})")
    # Shoulder pitched forward: theta2 = pi.
    pose2 = forward_kinematics(theta1=0.0, theta2=math.pi, theta3=0.0, theta4=0.0)
    print(f"Forward:    x={pose2.x:.2f}  (expect +{L1+L2+L3:.2f})")
