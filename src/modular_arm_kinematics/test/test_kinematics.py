import math
import pytest

from modular_arm_kinematics.fk import forward_kinematics
from modular_arm_kinematics.ik import inverse_kinematics, Unreachable


def test_fk_ik_roundtrip():
    targets = [
        (0.15, 0.05, 0.10, -1.0, "up"),
        (0.10, -0.08, 0.15, -0.5, "down"),
        (0.20, 0.0, 0.06, 0.0, "up"),
    ]
    for x, y, z, pitch, elbow in targets:
        sol = inverse_kinematics(x, y, z, pitch=pitch, elbow=elbow)
        pose = forward_kinematics(sol.theta1, sol.theta2, sol.theta3, sol.theta4)
        assert math.isclose(pose.x, x, abs_tol=1e-6)
        assert math.isclose(pose.y, y, abs_tol=1e-6)
        assert math.isclose(pose.z, z, abs_tol=1e-6)
        assert math.isclose(pose.pitch, pitch, abs_tol=1e-6)


def test_unreachable_target_raises():
    with pytest.raises(Unreachable):
        inverse_kinematics(x=5.0, y=5.0, z=5.0, pitch=0.0)
