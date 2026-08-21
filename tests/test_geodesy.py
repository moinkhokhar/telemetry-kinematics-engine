import pytest

from src.transforms.geodesy import GeodesyEngine
from src.transforms.geodetic import GeodeticPoint


def test_initial_bearing_london_to_paris() -> None:
    london = GeodeticPoint(latitude_deg=51.5074, longitude_deg=-0.1278, altitude_m=0.0)
    paris = GeodeticPoint(latitude_deg=48.8566, longitude_deg=2.3522, altitude_m=0.0)

    bearing = GeodesyEngine.initial_bearing(london, paris)
    assert 140.0 < bearing < 160.0


def test_initial_bearing_due_north() -> None:
    origin = GeodeticPoint(latitude_deg=0.0, longitude_deg=0.0, altitude_m=0.0)
    destination = GeodeticPoint(latitude_deg=10.0, longitude_deg=0.0, altitude_m=0.0)

    bearing = GeodesyEngine.initial_bearing(origin, destination)
    assert bearing == 0.0


def test_cross_track_distance_on_line() -> None:
    start = GeodeticPoint(latitude_deg=0.0, longitude_deg=0.0, altitude_m=0.0)
    end = GeodeticPoint(latitude_deg=10.0, longitude_deg=0.0, altitude_m=0.0)
    midpoint = GeodeticPoint(latitude_deg=5.0, longitude_deg=0.0, altitude_m=0.0)

    xt_dist = GeodesyEngine.cross_track_distance(midpoint, start, end)
    assert pytest.approx(xt_dist, abs=1.0) == 0.0
