import numpy as np

class KinematicKalmanFilter:
    """Linear state estimator tracking 1D position and velocity with constant velocity motion model."""

    def __init__(self, process_noise_std: float, measurement_noise_std: float, dt: float = 0.1):
        self.dt = dt
        
        # State vector: [position, velocity]^T
        self.x = np.zeros((2, 1), dtype=np.float64)
        
        # State Transition Matrix (F)
        self.F = np.array([
            [1.0, self.dt],
            [0.0, 1.0]
        ], dtype=np.float64)
        
        # Measurement Matrix (H): only position is directly measured
        self.H = np.array([[1.0, 0.0]], dtype=np.float64)
        
        # Process Covariance Matrix (Q)
        q_var = process_noise_std ** 2
        self.Q = np.array([
            [(0.25 * self.dt**4) * q_var, (0.5 * self.dt**3) * q_var],
            [(0.5 * self.dt**3) * q_var, (self.dt**2) * q_var]
        ], dtype=np.float64)
        
        # Measurement Noise Covariance (R)
        self.R = np.array([[measurement_noise_std ** 2]], dtype=np.float64)
        
        # Estimation Error Covariance (P)
        self.P = np.eye(2, dtype=np.float64) * 500.0

    def predict(self) -> np.ndarray:
        """Propagate state and covariance forward by dt."""
        self.x = self.F @ self.x
        self.P = (self.F @ self.P @ self.F.T) + self.Q
        return self.x

    def update(self, measurement: float) -> np.ndarray:
        """Incorporate new noisy scalar observation."""
        z = np.array([[measurement]], dtype=np.float64)
        y = z - (self.H @ self.x)  # Measurement residual
        s = (self.H @ self.P @ self.H.T) + self.R  # Residual covariance
        k = self.P @ self.H.T @ np.linalg.inv(s)   # Optimal Kalman Gain

        self.x = self.x + (k @ y)
        self.P = (np.eye(2) - (k @ self.H)) @ self.P
        return self.x
