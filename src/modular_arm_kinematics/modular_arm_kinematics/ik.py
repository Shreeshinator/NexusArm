"""Analytical inverse kinematics for the modular 4-DOF arm.

Standard decoupled approach for a yaw + 3R-planar arm:
  1. theta1 comes directly from the target's (x, y) -- it just orients
     the vertical plane the rest of the solve happens in.
  2. Since we have 4 joints but only 3 position constraints (x, y, z),
     there's one redundant DOF. We remove it by asking the caller for a
     desired end-effector pitch, turning the remaining problem into a
     classic 2-link planar arm IK (shoulder + elbow) for the wrist
     center, plus theta4 = pitch - theta2 - theta3 to hit the pitch.
     Why is theta4 = pitch - theta2 - theta3? Because the end-effector pitch is the sum of the three joint angles in the plane, and we want to solve for theta4 given the other two. Why is the end-effector pitch the sum of the three joint angles? Because the end-effector pitch is defined as the angle of the end-effector relative to the horizontal plane, and each joint contributes to that angle. Therefore, to achieve a desired pitch, we need to account for the contributions of theta2 and theta3 when calculating theta4.

Joint angle conventions match fk.py exactly -- if you change one, change
both, and update the xacro origins/axes to match.
"""
import math
from dataclasses import dataclass # dataclass contains only data, no methods, and is immutable by default 
from typing import List # for the return type of JointSolution.as_list()

from .fk import L0, L1, L2, L3  # the lengths of the arm segments

# Joint angle limits (radians) — keep in sync with modular_arm.urdf.xacro
JOINT_LIMITS = {
    "joint1": (-3.14159, 3.14159),
    "joint2": (-1.5708, 3.14159),
    "joint3": (-3.14159, 3.14159),
    "joint4": (-3.14159, 3.14159),
}


class Unreachable(Exception): # inherit from Exception to create a custom exception
    """Raised when a target pose is outside the arm's workspace."""


@dataclass # stores only data, no methods, and is immutable by default
class JointSolution:
    theta1: float # the base yaw angle, which is the angle of the first joint that rotates the arm around the vertical axis
    theta2: float # the shoulder pitch angle, which is the angle of the second joint that moves the arm up and down in the vertical plane
    theta3: float # the elbow pitch angle, which is the angle of the third joint that moves the arm up and down in the vertical plane
    theta4: float # the wrist pitch angle, which is the angle of the fourth joint that moves the end-effector up and down in the vertical plane

    def as_list(self) -> List[float]: # returns the joint angles as a list
        return [self.theta1, self.theta2, self.theta3, self.theta4]


def inverse_kinematics(
    x: float,
    y: float,
    z: float,
    pitch: float = -math.pi / 2,
    elbow: str = None,
) -> JointSolution:
    """Solve for joint angles reaching (x, y, z) with the given end-effector pitch.

    Args:
        x, y, z: target end-effector position in the arm base frame (meters).
        pitch: desired absolute end-effector pitch, radians (0 = horizontal,
               -pi/2 = pointing straight down -- the usual "top-down pick" pose).
        elbow: "up" or "down" to force that configuration, or None to
               automatically try both and return the first valid solution.

    Raises:
        Unreachable: if no valid solution exists within joint limits.
    """
    theta1 = math.atan2(y, x)
    h = x * math.cos(theta1) + y * math.sin(theta1)

    # Wrist centre. With the backward convention: h = hw - L3·cos(pitch).
    hw = h + L3 * math.cos(pitch)
    zw = (z - L0) - L3 * math.sin(pitch)

    d2 = hw * hw + zw * zw
    d = math.sqrt(d2)

    if d > (L1 + L2) or d < abs(L1 - L2):
        raise Unreachable(
            f"Target (x={x:.3f}, y={y:.3f}, z={z:.3f}) with pitch={pitch:.3f} "
            f"is outside the arm's reach (wrist distance {d:.3f}m, "
            f"reachable range [{abs(L1 - L2):.3f}, {L1 + L2:.3f}]m)."
        )

    cos_theta3 = (d2 - L1 * L1 - L2 * L2) / (2 * L1 * L2)
    cos_theta3 = max(-1.0, min(1.0, cos_theta3))
    theta3_mag = math.acos(cos_theta3)

    candidates = []
    if elbow is None:
        candidates = ["up", "down"]
    elif elbow in ("up", "down"):
        candidates = [elbow]
    else:
        raise ValueError("elbow must be 'up', 'down', or None")

    errors = []
    for mode in candidates:
        theta3 = theta3_mag if mode == "up" else -theta3_mag
        theta2 = math.atan2(zw, -hw) - math.atan2(
            L2 * math.sin(theta3), L1 + L2 * math.cos(theta3)
        )
        theta4 = pitch - theta2 - theta3

        # Wrap angles by ±2π to fit within joint limits.  The forward
        # kinematics only depends on sin/cos of cumulative angles, so
        # wrapping an individual joint by 2π leaves the end-effector
        # pose unchanged while keeping the joint within its limit.
        t2 = _wrap_angle(theta2, *JOINT_LIMITS["joint2"])
        t3 = _wrap_angle(theta3, *JOINT_LIMITS["joint3"])
        t4 = _wrap_angle(theta4, *JOINT_LIMITS["joint4"])

        solution = JointSolution(theta1=theta1, theta2=t2, theta3=t3, theta4=t4)
        invalid_joints = _validate_limits(solution)
        if not invalid_joints:
            return solution
        errors.append(
            f"Elbow '{mode}' violates {', '.join(invalid_joints)}: "
            f"θ=({solution.theta1:.3f},{solution.theta2:.3f},"
            f"{solution.theta3:.3f},{solution.theta4:.3f})"
        )

    raise Unreachable(
        f"No valid solution for (x={x:.3f}, y={y:.3f}, z={z:.3f}, "
        f"pitch={pitch:.3f}). " + "; ".join(errors)
    )


def _validate_limits(solution: JointSolution):
    """Return list of joint names that violate limits, or empty list if all OK."""
    violations = []
    for name, (lo, hi) in JOINT_LIMITS.items():
        val = getattr(solution, "theta" + name[-1])
        if val < lo - 1e-9 or val > hi + 1e-9:
            violations.append(name)
    return violations


def _wrap_angle(val: float, lo: float, hi: float) -> float:
    """Wrap *val* by ±2π to fit within [lo, hi]; return original if no wrap helps."""
    for shift in (2 * math.pi, -2 * math.pi, 4 * math.pi, -4 * math.pi):
        cand = val + shift
        if lo - 1e-9 <= cand <= hi + 1e-9:
            return cand
    return val


if __name__ == "__main__":
    from .fk import forward_kinematics

    # Auto elbow mode (try both, pick valid)
    sol = inverse_kinematics(x=0.15, y=0.05, z=0.10, pitch=-0.3)
    print("IK solution (auto):", sol)
    check = forward_kinematics(sol.theta1, sol.theta2, sol.theta3, sol.theta4)
    print("FK of that solution:", check)

    # Force elbow down (also valid for this target)
    sol2 = inverse_kinematics(x=0.15, y=0.05, z=0.10, pitch=-0.3, elbow="down")
    print("IK solution (down):", sol2)

    # Elbow up with steep pitch violates joint4 — auto mode will pick elbow down
    try:
        sol3 = inverse_kinematics(x=0.15, y=0.05, z=0.10, pitch=-1.0, elbow="up")
        print("IK solution (up):", sol3)
    except Exception as e:
        print(f"elbow=up, pitch=-1.0: {e}")

    print("auto, pitch=-1.0:", inverse_kinematics(x=0.15, y=0.05, z=0.10, pitch=-1.0))
