"""Analytical inverse kinematics for the real robot arm.

Standard decoupled approach for a yaw + 3R-planar arm, matching fk.py and the URDF geometry:

  1. theta1 = atan2(y, x) orients the vertical plane.
  2. With the desired pitch, the wrist centre (joint4 origin) is fixed:
       s3 angle = -pitch + A3,  length L3  (the fixed wrist->gripper offset)
  3. The remaining shoulder/elbow problem is a classic 2-link planar IK
     in the (h, z) plane, using the segment's fixed in-plane angles:
       SEG1 at in-plane angle A1, SEG2 at in-plane angle A2.

Joint angle conventions match fk.py exactly.

Raises Unreachable if no solution fits within the joint limits.
"""
import math
from dataclasses import dataclass
from typing import List

from .fk import SHOULDER, L1, L2, L3, A1, A2, DELTA, SEG3, _rot

# Joint angle limits (radians) — keep in sync with robot_arm.urdf.xacro
JOINT_LIMITS = {
    "joint1": (-3.14, 3.14),
    "joint2": (-1.57, 1.57),
    "joint3": (-1.57, 1.57),
    "joint4": (-1.57, 1.57),
}

A3 = math.atan2(SEG3[1], SEG3[0])


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
    elbow: str = None,
) -> JointSolution:
    """Solve for joint angles reaching (x, y, z) with the given end-effector pitch.

    Args:
        x, y, z: target gripper position in the arm base frame (meters).
        pitch: desired absolute end-effector pitch, radians (0 = horizontal,
               -pi/2 = pointing straight down -- the usual "top-down pick" pose).
        elbow: "up" or "down" to force that configuration, or None to
               automatically try both and return the first valid solution.

    Raises:
        Unreachable: if no valid solution exists within joint limits.
    """
    theta1 = math.atan2(y, x)
    h = x * math.cos(theta1) + y * math.sin(theta1)

    # Wrist centre: subtract the fixed wrist->gripper segment (rotated by pitch).
    # World angle of SEG3 = A3 + pitch (because Ry rotation gives A - theta, and
    # the sum theta2+theta3+theta4 = -pitch).
    s3_world_angle = A3 + pitch
    hw = h - L3 * math.cos(s3_world_angle)
    zw = z - L3 * math.sin(s3_world_angle)

    # 2-link shoulder/elbow solve in (h, z) relative to the shoulder joint.
    u = hw - SHOULDER[0]
    v = zw - SHOULDER[1]
    d2 = u * u + v * v
    d = math.sqrt(d2)

    if d > (L1 + L2) or d < abs(L1 - L2):
        raise Unreachable(
            f"Target (x={x:.3f}, y={y:.3f}, z={z:.3f}) with pitch={pitch:.3f} "
            f"is outside the arm's reach (wrist distance {d:.3f}m, "
            f"reachable range [{abs(L1 - L2):.3f}, {L1 + L2:.3f}]m)."
        )

    cos_gamma = (d2 - L1 * L1 - L2 * L2) / (2 * L1 * L2)
    cos_gamma = max(-1.0, min(1.0, cos_gamma))
    gamma_mag = math.acos(cos_gamma)

    candidates = []
    if elbow is None:
        candidates = ["up", "down"]
    elif elbow in ("up", "down"):
        candidates = [elbow]
    else:
        raise ValueError("elbow must be 'up', 'down', or None")

    errors = []
    for mode in candidates:
        gamma = gamma_mag if mode == "up" else -gamma_mag  # angle between SEG1 and SEG2

        # Standard 2-link: psi1 = world angle of SEG1
        #   u = L1*cos(psi1) + L2*cos(psi1 + beta)
        #   where beta = psi2 - psi1 = DELTA - theta3 is the elbow angle.
        psi1 = math.atan2(v, u) - math.atan2(
            L2 * math.sin(gamma), L1 + L2 * math.cos(gamma)
        )

        t2 = A1 - psi1
        t3 = DELTA - gamma
        t4 = -pitch - t2 - t3

        t2 = _wrap_angle(t2, *JOINT_LIMITS["joint2"])
        t3 = _wrap_angle(t3, *JOINT_LIMITS["joint3"])
        t4 = _wrap_angle(t4, *JOINT_LIMITS["joint4"])

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
    violations = []
    for name, (lo, hi) in JOINT_LIMITS.items():
        val = getattr(solution, "theta" + name[-1])
        if val < lo - 1e-9 or val > hi + 1e-9:
            violations.append(name)
    return violations


def _wrap_angle(val: float, lo: float, hi: float) -> float:
    for shift in (2 * math.pi, -2 * math.pi, 4 * math.pi, -4 * math.pi):
        cand = val + shift
        if lo - 1e-9 <= cand <= hi + 1e-9:
            return cand
    return val


if __name__ == "__main__":
    from .fk import forward_kinematics

    for target in [
        (0.20, 0.05, 0.25, -0.3),
        (0.24, 0.06, 0.0525, -math.pi / 2),  # pick a block
    ]:
        sol = inverse_kinematics(*target)
        pose = forward_kinematics(sol.theta1, sol.theta2, sol.theta3, sol.theta4)
        print(f"target=({target[0]:.2f},{target[1]:.2f},{target[2]:.2f},{target[3]:.2f})")
        print(f"  thetas={[round(a,3) for a in sol.as_list()]}")
        print(f"  fk    =({pose.x:.3f},{pose.y:.3f},{pose.z:.3f},{pose.pitch:.3f})")
