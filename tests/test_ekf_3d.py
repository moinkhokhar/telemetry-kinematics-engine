import numpy as np

from src.estimation.ekf_3d import SpatialKalmanFilter


def test_spatial_kalman_trajectory_convergence():
    filter_3d = SpatialKalmanFilter(dt=0.1, process_noise_accel=0.2, measurement_noise_pos=1.0)

    # Simulate 3D linear trajectory with added Gaussian noise
    true_trajectory = np.array([[t * 2.0, t * 1.5, 100.0 + t * 0.5] for t in range(25)])
    np.random.seed(42)
    measurements = true_trajectory + np.random.normal(0, 1.0, true_trajectory.shape)

    estimated_trajectory = []
    for z in measurements:
        filter_3d.predict()
        filter_3d.update(z)
        estimated_trajectory.append(filter_3d.estimated_position)

    raw_error = np.mean(np.linalg.norm(measurements - true_trajectory, axis=1))
    filtered_error = np.mean(
        np.linalg.norm(np.array(estimated_trajectory) - true_trajectory, axis=1)
    )

    assert filtered_error < raw_error
    vx, vy, vz = filter_3d.estimated_velocity
    assert abs(vx) > 0.0
