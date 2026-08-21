import math

import numpy as np
import pytest

from src.estimation.attitude import Quaternion


def test_quaternion_identity_rotation():
    q = Quaternion(1.0, 0.0, 0.0, 0.0)
    euler = q.to_euler_angles()
    assert euler.roll_deg == 0.0
    assert euler.pitch_deg == 0.0
    assert euler.yaw_deg == 0.0

    dcm = q.to_rotation_matrix()
    assert np.allclose(dcm, np.eye(3))


def test_quaternion_90deg_yaw():
    half_angle = math.radians(45)
    q = Quaternion(math.cos(half_angle), 0.0, 0.0, math.sin(half_angle))
    euler = q.to_euler_angles()
    assert pytest.approx(euler.yaw_deg, abs=1e-2) == 90.0


def test_quaternion_pitch_singularity():
    # 90-degree pitch (gimbal boundary)
    half_angle = math.radians(45)
    q = Quaternion(math.cos(half_angle), 0.0, math.sin(half_angle), 0.0)
    euler = q.to_euler_angles()
    assert pytest.approx(euler.pitch_deg, abs=1e-2) == 90.0


def test_quaternion_multiplication():
    # 90 deg Yaw * 90 deg Pitch
    q_yaw = Quaternion(math.cos(math.radians(45)), 0.0, 0.0, math.sin(math.radians(45)))
    q_pitch = Quaternion(math.cos(math.radians(45)), 0.0, math.sin(math.radians(45)), 0.0)
    q_combined = q_yaw.multiply(q_pitch)

    assert q_combined.w > 0
    dcm = q_combined.to_rotation_matrix()
    assert dcm.shape == (3, 3)


def test_zero_norm_quaternion_rejection():
    with pytest.raises(ValueError):
        Quaternion(0.0, 0.0, 0.0, 0.0)
