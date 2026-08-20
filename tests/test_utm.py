import pytest
from src.core.exceptions import CoordinateOutOfBoundsError
from src.transforms.utm import UTMConverter


def test_utm_projection_eiffel_tower():
    # Eiffel Tower: 48.8584° N, 2.2945° E (UTM Zone 31N)
    utm = UTMConverter.latlon_to_utm(48.8584, 2.2945)
    assert utm.zone_number == 31
    assert utm.zone_letter == "N"
    assert 448000.0 < utm.easting < 449000.0
    assert 5411000.0 < utm.northing < 5413000.0


def test_utm_out_of_bounds_validation():
    with pytest.raises(CoordinateOutOfBoundsError):
        UTMConverter.latlon_to_utm(89.0, 10.0)

    with pytest.raises(CoordinateOutOfBoundsError):
        UTMConverter.latlon_to_utm(45.0, 195.0)
