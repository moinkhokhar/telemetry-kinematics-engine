import pytest
from src.transforms.geodetic import CoordinateTransformer, GeodeticPoint

def test_null_island_ecef_projection():
    origin = GeodeticPoint(latitude_deg=0.0, longitude_deg=0.0, altitude_m=0.0)
    ecef = CoordinateTransformer.geodetic_to_ecef(origin)
    assert pytest.approx(ecef.x_m, abs=1.0) == 6378137.0
    assert pytest.approx(ecef.y_m, abs=1.0) == 0.0
    assert pytest.approx(ecef.z_m, abs=1.0) == 0.0

def test_haversine_known_distance():
    london = GeodeticPoint(51.5074, -0.1278, 0.0)
    paris = GeodeticPoint(48.8566, 2.3522, 0.0)
    dist = CoordinateTransformer.haversine_distance(london, paris)
    assert 340000.0 < dist < 350000.0
