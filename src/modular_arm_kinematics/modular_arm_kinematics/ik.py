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

from .fk import L0, L1, L2, L3 # the lengths of the arm segments


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
    x: float, # x coordinate of the target position
    y: float, # y 
    z: float, # z 
    pitch: float = -math.pi / 2,
    elbow: str = "up",
) -> JointSolution: # returns a JointSolution object containing the four joint angles
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
    # raise ValueError if elbow is not "up" or "down". If it is not, the function will continue to execute, but the result will be invalid. This is a safeguard to ensure that the function is used correctly.

    theta1 = math.atan2(y, x) # base yaw
    r = math.hypot(x, y) # distance from the base to the target in the horizontal plane 

    # work back from the target to the wrist center, which is L3 away from the end-effector along the pitch direction

    rw = r - L3 * math.cos(pitch) # distance from the wrist to the target in the horizontal plane

    """
    Distance from the wrist to the target in the horizontal plane. r is the distance from the base to the target in the horizontal plane, and L3 * cos(pitch) is the horizontal distance from the wrist to the end-effector. By subtracting these two distances, we get the distance from the wrist to the target in the horizontal plane.
    """

    zw = (z - L0) - L3 * math.sin(pitch) # distance from the wrist to the target in the vertical plane
    """
    Distance from the wrist to the target in the vertical plane. z - L0 (the base) is the vertical distance from the base to the target, and L3 * sin(pitch) is the vertical distance from the wrist to the end-effector. By subtracting these two distances, we get the distance from the wrist to the target in the vertical plane.
    """

    d2 = rw * rw + zw * zw
    d = math.sqrt(d2) # The final distance from the wrist to the target in 3D space, which is the hypotenuse of the right triangle formed by rw and zw. This distance is used to determine if the target is reachable by the arm.

    if d > (L1 + L2) or d < abs(L1 - L2):
        raise Unreachable(
            f"Target (x={x:.3f}, y={y:.3f}, z={z:.3f}) with pitch={pitch:.3f} "
            f"is outside the arm's reach (wrist distance {d:.3f}m, "
            f"reachable range [{abs(L1 - L2):.3f}, {L1 + L2:.3f}]m)."
        )

    cos_theta3 = (d2 - L1 * L1 - L2 * L2) / (2 * L1 * L2) # law of cosines for findig the elbow angle
    cos_theta3 = max(-1.0, min(1.0, cos_theta3))  # clamp for float noise
    theta3_mag = math.acos(cos_theta3) # actual elbow angle

    theta3 = theta3_mag if elbow == "up" else -theta3_mag # THIS is the elbow up/down selection -- the acos function returns the angle in the range [0, pi], which corresponds to the "up" configuration. If the user wants the "down" configuration, we simply negate the angle.

    theta2 = math.atan2(zw, rw) - math.atan2(L2 * math.sin(theta3), L1 + L2 * math.cos(theta3)) # find the shoulder angle using the law of cosines and the law of sines by subtracting the distance from the wrist to the elbow. The first term is the angle from the horizontal to the line connecting the shoulder to the wrist, and the second term is the angle from that line to the line connecting the shoulder to the elbow. The difference between these two angles gives us the shoulder angle.

    theta4 = pitch - theta2 - theta3

    return JointSolution(theta1=theta1, theta2=theta2, theta3=theta3, theta4=theta4)


if __name__ == "__main__":
    from .fk import forward_kinematics # import the forward kinematics function from the fk module

    sol = inverse_kinematics(x=0.15, y=0.05, z=0.10, pitch=-1.0, elbow="up")
    print("IK solution:", sol)
    check = forward_kinematics(sol.theta1, sol.theta2, sol.theta3, sol.theta4)
    print("FK of that solution (should match target):", check)
