import math
import pytest
from src.estimation.attitude import Quaternion


def test_quaternion_identity_rotation():
    q = Quaternion(1.0, 0.0, 0.0, 0.0)
    euler = q.to_euler_angles()
    assert euler.roll_deg == 0.0
    assert euler.pitch_deg == 0.0
    assert euler.yaw_deg == 0.0


def test_quaternion_90deg_yaw():
    # 90-degree yaw rotation around Z-axis
    half_angle = math.radians(45)
    q = Quaternion(math.cos(half_angle), 0.0, 0.0, math.sin(half_angle))
    euler = q.to_euler_angles()
    assert pytest.approx(euler.yaw_deg, abs=1e-2) == 90.0


def test_zero_norm_quaternion_rejection():
    with pytest.raises(ValueError):
        Quaternion(0.0, 0.0, 0.0, 0.0)
