"""6-DOF Spatial State Estimator tracking 3D position and velocity."""

import numpy as np

from src.core.exceptions import FilterDivergenceError


class SpatialKalmanFilter:
    """Tracks 3D Cartesian position and velocity [px, py, pz, vx, vy, vz]^T."""

    def __init__(
        self,
        dt: float = 0.1,
        process_noise_accel: float = 0.5,
        measurement_noise_pos: float = 1.5,
    ) -> None:
        self.dt = dt
        self.x = np.zeros((6, 1), dtype=np.float64)

        # State transition matrix F (6x6)
        self.F = np.eye(6, dtype=np.float64)
        self.F[0, 3] = dt
        self.F[1, 4] = dt
        self.F[2, 5] = dt

        # Measurement observation matrix H (3x6)
        self.H = np.zeros((3, 6), dtype=np.float64)
        self.H[0, 0] = 1.0
        self.H[1, 1] = 1.0
        self.H[2, 2] = 1.0

        # Process noise covariance Q
        q_var = process_noise_accel**2
        q11 = (0.25 * (dt**4)) * q_var
        q12 = (0.5 * (dt**3)) * q_var
        q22 = (dt**2) * q_var

        self.Q = np.zeros((6, 6), dtype=np.float64)
        for i in range(3):
            self.Q[i, i] = q11
            self.Q[i + 3, i + 3] = q22
            self.Q[i, i + 3] = q12
            self.Q[i + 3, i] = q12

        # Measurement noise covariance R (3x3)
        self.R = np.eye(3, dtype=np.float64) * (measurement_noise_pos**2)

        # State estimation error covariance P (6x6)
        self.P = np.eye(6, dtype=np.float64) * 100.0

    def predict(self) -> np.ndarray:
        """Propagates state vector and error covariance forward in time."""
        self.x = self.F @ self.x
        self.P = (self.F @ self.P @ self.F.T) + self.Q
        return self.x

    def update(self, pos_measurement: np.ndarray) -> np.ndarray:
        """Fuses observed 3D position vector [px, py, pz]."""
        z = np.asarray(pos_measurement, dtype=np.float64).reshape((3, 1))
        residual = z - (self.H @ self.x)
        s = (self.H @ self.P @ self.H.T) + self.R

        try:
            k_gain = self.P @ self.H.T @ np.linalg.inv(s)
        except np.linalg.LinAlgError as exc:
            raise FilterDivergenceError("Singular residual covariance in Kalman update") from exc

        self.x = self.x + (k_gain @ residual)
        i_kh = np.eye(6, dtype=np.float64) - (k_gain @ self.H)
        self.P = (i_kh @ self.P @ i_kh.T) + (k_gain @ self.R @ k_gain.T)
        return self.x

    @property
    def estimated_position(self) -> tuple[float, float, float]:
        """Returns the current 3D position tuple (px, py, pz)."""
        return float(self.x[0, 0]), float(self.x[1, 0]), float(self.x[2, 0])

    @property
    def estimated_velocity(self) -> tuple[float, float, float]:
        """Returns the current 3D velocity tuple (vx, vy, vz)."""
        return float(self.x[3, 0]), float(self.x[4, 0]), float(self.x[5, 0])
