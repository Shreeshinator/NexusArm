import math
import pytest

from modular_arm_kinematics.fk import forward_kinematics
from modular_arm_kinematics.ik import inverse_kinematics, Unreachable


def _angle_close(a, b):
    """True if a and b are equivalent modulo 2π."""
    d = abs(a - b) % (2 * math.pi)
    return d < 1e-6 or d > 2 * math.pi - 1e-6


def test_fk_ik_roundtrip_explicit_elbow():
    targets = [
        (0.12, 0.0, 0.10, 0.0, "up"),
        (0.08, 0.0, 0.15, -0.5, "down"),
    ]
    for x, y, z, pitch, elbow in targets:
        sol = inverse_kinematics(x, y, z, pitch=pitch, elbow=elbow)
        pose = forward_kinematics(sol.theta1, sol.theta2, sol.theta3, sol.theta4)
        assert math.isclose(pose.x, x, abs_tol=1e-6)
        assert math.isclose(pose.y, y, abs_tol=1e-6)
        assert math.isclose(pose.z, z, abs_tol=1e-6)
        assert _angle_close(pose.pitch, pitch)


def test_fk_ik_roundtrip_auto_elbow():
    targets = [
        (0.10, 0.05, 0.10, -0.3),
        (0.12, 0.0, 0.08, 0.5),
        (0.08, 0.0, 0.15, -0.5),
    ]
    for x, y, z, pitch in targets:
        sol = inverse_kinematics(x, y, z, pitch=pitch)
        pose = forward_kinematics(sol.theta1, sol.theta2, sol.theta3, sol.theta4)
        assert math.isclose(pose.x, x, abs_tol=1e-6)
        assert math.isclose(pose.y, y, abs_tol=1e-6)
        assert math.isclose(pose.z, z, abs_tol=1e-6)
        assert _angle_close(pose.pitch, pitch)


def test_steep_pitch_reachable_with_wrapping():
    sol = inverse_kinematics(x=0.15, y=0.05, z=0.10, pitch=-1.0)
    pose = forward_kinematics(sol.theta1, sol.theta2, sol.theta3, sol.theta4)
    assert math.isclose(pose.x, 0.15, abs_tol=1e-6)
    assert math.isclose(pose.y, 0.05, abs_tol=1e-6)
    assert math.isclose(pose.z, 0.10, abs_tol=1e-6)
    assert _angle_close(pose.pitch, -1.0)


def test_mild_pitch_reachable_with_auto():
    sol = inverse_kinematics(x=0.10, y=0.05, z=0.10, pitch=-0.3)
    pose = forward_kinematics(sol.theta1, sol.theta2, sol.theta3, sol.theta4)
    assert math.isclose(pose.x, 0.10, abs_tol=1e-6)
    assert math.isclose(pose.y, 0.05, abs_tol=1e-6)
    assert math.isclose(pose.z, 0.10, abs_tol=1e-6)
    assert _angle_close(pose.pitch, -0.3)


def test_zero_pose_is_behind_base():
    pose = forward_kinematics(0, 0, 0, 0)
    assert pose.x < 0, "shoulder should point backward at rest"
    assert math.isclose(pose.y, 0, abs_tol=1e-10)
    assert math.isclose(pose.z, 0.06, abs_tol=1e-10)


def test_shoulder_forward_pose():
    pose = forward_kinematics(0, math.pi, 0, 0)
    assert pose.x > 0, "shoulder should point forward when θ2=π"


def test_unreachable_distance_raises():
    with pytest.raises(Unreachable):
        inverse_kinematics(x=5.0, y=5.0, z=5.0, pitch=0.0)
