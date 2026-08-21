import pytest
from src.transforms.geodetic import CoordinateTransformer, GeodeticPoint
from src.transforms.inverse_geodetic import InverseCoordinateTransformer


def test_ecef_to_geodetic_roundtrip():
    original = GeodeticPoint(latitude_deg=37.7749, longitude_deg=-122.4194, altitude_m=120.0)
    ecef = CoordinateTransformer.geodetic_to_ecef(original)
    recovered = InverseCoordinateTransformer.ecef_to_geodetic(ecef)

    assert pytest.approx(recovered.latitude_deg, abs=1e-6) == original.latitude_deg
    assert pytest.approx(recovered.longitude_deg, abs=1e-6) == original.longitude_deg
    assert pytest.approx(recovered.altitude_m, abs=1e-2) == original.altitude_m


def test_ecef_polar_singularity():
    north_pole = GeodeticPoint(latitude_deg=90.0, longitude_deg=0.0, altitude_m=50.0)
    ecef = CoordinateTransformer.geodetic_to_ecef(north_pole)
    recovered = InverseCoordinateTransformer.ecef_to_geodetic(ecef)

    assert pytest.approx(recovered.latitude_deg, abs=1e-6) == 90.0
    assert pytest.approx(recovered.altitude_m, abs=1e-2) == 50.0
