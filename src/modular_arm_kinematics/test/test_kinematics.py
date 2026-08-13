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
        (0.20, 0.0, 0.25, 0.0, "down"),
        (0.15, 0.0, 0.28, -0.3, "down"),
    ]
    for x, y, z, pitch, elbow in targets:
        sol = inverse_kinematics(x, y, z, pitch=pitch, elbow=elbow)
        pose = forward_kinematics(sol.theta1, sol.theta2, sol.theta3, sol.theta4)
        assert math.isclose(pose.x, x, abs_tol=1e-6)
        assert math.isclose(pose.y, y, abs_tol=1e-6)
        assert math.isclose(pose.z, z, abs_tol=1e-6)
        assert _angle_close(pose.pitch, pitch)


def test_elbow_up_unreachable_for_forward_targets():
    # With this arm's geometry and ±90° pitch limits, forward reaches are
    # only possible with the elbow in the "down" configuration.
    with pytest.raises(Unreachable):
        inverse_kinematics(x=0.20, y=0.0, z=0.25, pitch=0.0, elbow="up")


def test_fk_ik_roundtrip_auto_elbow():
    targets = [
        (0.20, 0.05, 0.25, -0.3),
        (0.10, 0.02, 0.30, 0.3),
        (0.22, 0.04, 0.22, -0.2),
        (0.18, -0.03, 0.30, -0.5),
    ]
    for x, y, z, pitch in targets:
        sol = inverse_kinematics(x, y, z, pitch=pitch)
        pose = forward_kinematics(sol.theta1, sol.theta2, sol.theta3, sol.theta4)
        assert math.isclose(pose.x, x, abs_tol=1e-6)
        assert math.isclose(pose.y, y, abs_tol=1e-6)
        assert math.isclose(pose.z, z, abs_tol=1e-6)
        assert _angle_close(pose.pitch, pitch)


def test_steep_pitch_reachable():
    sol = inverse_kinematics(x=0.24, y=0.06, z=0.0525, pitch=-math.pi / 2)
    pose = forward_kinematics(sol.theta1, sol.theta2, sol.theta3, sol.theta4)
    assert math.isclose(pose.x, 0.24, abs_tol=1e-6)
    assert math.isclose(pose.y, 0.06, abs_tol=1e-6)
    assert math.isclose(pose.z, 0.0525, abs_tol=1e-6)
    assert _angle_close(pose.pitch, -math.pi / 2)


def test_mild_pitch_reachable_with_auto():
    sol = inverse_kinematics(x=0.20, y=0.05, z=0.25, pitch=-0.3)
    pose = forward_kinematics(sol.theta1, sol.theta2, sol.theta3, sol.theta4)
    assert math.isclose(pose.x, 0.20, abs_tol=1e-6)
    assert math.isclose(pose.y, 0.05, abs_tol=1e-6)
    assert math.isclose(pose.z, 0.25, abs_tol=1e-6)
    assert _angle_close(pose.pitch, -0.3)


def test_zero_pose_points_forward():
    pose = forward_kinematics(0, 0, 0, 0)
    assert pose.x > 0, "zero pose should point forward along +X"
    assert math.isclose(pose.y, 0, abs_tol=1e-10)
    assert math.isclose(pose.x, 0.22, abs_tol=1e-3)
    assert math.isclose(pose.z, 0.2935, abs_tol=1e-3)


def test_unreachable_distance_raises():
    with pytest.raises(Unreachable):
        inverse_kinematics(x=5.0, y=5.0, z=5.0, pitch=0.0)
