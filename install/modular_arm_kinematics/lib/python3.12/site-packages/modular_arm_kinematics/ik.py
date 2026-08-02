"""Analytical inverse kinematics for the modular 4-DOF arm.

Standard decoupled approach for a yaw + 3R-planar arm:
  1. theta1 comes directly from the target's (x, y) -- it just orients
     the vertical plane the rest of the solve happens in.
  2. Since we have 4 joints but only 3 position constraints (x, y, z),
     there's one redundant DOF. We remove it by asking the caller for a
     desired end-effector pitch, turning the remaining problem into a
     classic 2-link planar arm IK (shoulder + elbow) for the wrist
     center, plus theta4 = pitch - theta2 - theta3 to hit the pitch.

Joint angle conventions match fk.py exactly -- if you change one, change
both, and update the xacro origins/axes to match.
"""
import math
from dataclasses import dataclass
from typing import List

from .fk import L0, L1, L2, L3


class Unreachable(Exception):
    """Raised when a target pose is outside the arm's workspace."""


@dataclass
class JointSolution:
    theta1: float
    theta2: float
    theta3: float
    theta4: float

    def as_list(self) -> List[float]:
        return [self.theta1, self.theta2, self.theta3, self.theta4]


def inverse_kinematics(
    x: float,
    y: float,
    z: float,
    pitch: float = -math.pi / 2,
    elbow: str = "up",
) -> JointSolution:
    """Solve for joint angles reaching (x, y, z) with the given end-effector pitch.

    Args:
        x, y, z: target end-effector position in the arm base frame (meters).
        pitch: desired absolute end-effector pitch, radians (0 = horizontal,
               -pi/2 = pointing straight down -- the usual "top-down pick" pose).
        elbow: "up" or "down" -- selects between the two valid elbow solutions.

    Raises:
        Unreachable: if the target is outside the arm's reach for the given pitch.
    """
    if elbow not in ("up", "down"):
        raise ValueError("elbow must be 'up' or 'down'")

    theta1 = math.atan2(y, x)
    r = math.hypot(x, y)

    # Work back from the tip to the wrist center by removing the last link.
    rw = r - L3 * math.cos(pitch)
    zw = (z - L0) - L3 * math.sin(pitch)

    d2 = rw * rw + zw * zw
    d = math.sqrt(d2)

    if d > (L1 + L2) or d < abs(L1 - L2):
        raise Unreachable(
            f"Target (x={x:.3f}, y={y:.3f}, z={z:.3f}) with pitch={pitch:.3f} "
            f"is outside the arm's reach (wrist distance {d:.3f}m, "
            f"reachable range [{abs(L1 - L2):.3f}, {L1 + L2:.3f}]m)."
        )

    cos_theta3 = (d2 - L1 * L1 - L2 * L2) / (2 * L1 * L2)
    cos_theta3 = max(-1.0, min(1.0, cos_theta3))  # clamp for float noise
    theta3_mag = math.acos(cos_theta3)
    theta3 = theta3_mag if elbow == "up" else -theta3_mag

    theta2 = math.atan2(zw, rw) - math.atan2(L2 * math.sin(theta3), L1 + L2 * math.cos(theta3))
    theta4 = pitch - theta2 - theta3

    return JointSolution(theta1=theta1, theta2=theta2, theta3=theta3, theta4=theta4)


if __name__ == "__main__":
    from .fk import forward_kinematics

    sol = inverse_kinematics(x=0.15, y=0.05, z=0.10, pitch=-1.0, elbow="up")
    print("IK solution:", sol)
    check = forward_kinematics(sol.theta1, sol.theta2, sol.theta3, sol.theta4)
    print("FK of that solution (should match target):", check)
