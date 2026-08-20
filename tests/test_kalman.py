import numpy as np
from src.estimation.kalman import KinematicKalmanFilter

def test_kalman_filter_noise_attenuation():
    kf = KinematicKalmanFilter(process_noise_std=0.1, measurement_noise_std=2.0, dt=1.0)
    
    true_positions = [5.0 * t for t in range(1, 20)]
    np.random.seed(42)
    measurements = [p + np.random.normal(0, 2.0) for p in true_positions]
    
    estimates = []
    for z in measurements:
        kf.predict()
        state = kf.update(z)
        estimates.append(state[0, 0])
        
    error_raw = np.mean(np.abs(np.array(measurements) - np.array(true_positions)))
    error_filtered = np.mean(np.abs(np.array(estimates) - np.array(true_positions)))
    
    assert error_filtered < error_raw
