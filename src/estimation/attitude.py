"""3D Attitude Kinematics and Quaternion Rotation Engine."""

import math
from dataclasses import dataclass
import numpy as np


@dataclass(frozen=True)
class EulerAngles:
    """Euler attitude representation in degrees (Roll, Pitch, Yaw)."""

    roll_deg: float
    pitch_deg: float
    yaw_deg: float


class Quaternion:
    """Unit quaternion [w, x, y, z] for 3D spatial rotation without gimbal lock."""

    def __init__(self, w: float, x: float, y: float, z: float) -> None:
        norm = math.sqrt(w**2 + x**2 + y**2 + z**2)
        if norm < 1e-12:
            raise ValueError("Quaternion norm cannot be zero")
        self.w = w / norm
        self.x = x / norm
        self.y = y / norm
        self.z = z / norm

    def to_rotation_matrix(self) -> np.ndarray:
        """Computes the 3x3 Direction Cosine Matrix (DCM)."""
        w, x, y, z = self.w, self.x, self.y, self.z
        return np.array(
            [
                [1 - 2 * (y**2 + z**2), 2 * (x * y - z * w), 2 * (x * z + y * w)],
                [2 * (x * y + z * w), 1 - 2 * (x**2 + z**2), 2 * (y * z - x * w)],
                [2 * (x * z - y * w), 2 * (y * z + x * w), 1 - 2 * (x**2 + y**2)],
            ],
            dtype=np.float64,
        )

    def to_euler_angles(self) -> EulerAngles:
        """Extracts Tait-Bryan angles (Z-Y-X sequence)."""
        w, x, y, z = self.w, self.x, self.y, self.z

        # Roll (x-axis rotation)
        sinr_cosp = 2 * (w * x + y * z)
        cosr_cosp = 1 - 2 * (x**2 + y**2)
        roll = math.atan2(sinr_cosp, cosr_cosp)

        # Pitch (y-axis rotation)
        sinp = 2 * (w * y - z * x)
        pitch = math.copysign(math.pi / 2, sinp) if abs(sinp) >= 1 else math.asin(sinp)

        # Yaw (z-axis rotation)
        siny_cosp = 2 * (w * z + x * y)
        cosy_cosp = 1 - 2 * (y**2 + z**2)
        yaw = math.atan2(siny_cosp, cosy_cosp)

        return EulerAngles(
            roll_deg=round(math.degrees(roll), 4),
            pitch_deg=round(math.degrees(pitch), 4),
            yaw_deg=round(math.degrees(yaw), 4),
        )

    def multiply(self, other: "Quaternion") -> "Quaternion":
        """Calculates Hamilton quaternion product."""
        w = self.w * other.w - self.x * other.x - self.y * other.y - self.z * other.z
        x = self.w * other.x + self.x * other.w + self.y * other.z - self.z * other.y
        y = self.w * other.y - self.x * other.z + self.y * other.w + self.z * other.x
        z = self.w * other.z + self.x * other.y - self.y * other.x + self.z * other.w
        return Quaternion(w, x, y, z)
