"""Universal Transverse Mercator (UTM) coordinate transformations on the WGS84 ellipsoid."""

import math
from dataclasses import dataclass
from src.core.exceptions import CoordinateOutOfBoundsError


@dataclass(frozen=True)
class UTMPoint:
    """Represents a projected 2D UTM coordinate."""

    easting: float
    northing: float
    zone_number: int
    zone_letter: str


class UTMConverter:
    """Calculates conformal Transverse Mercator projections on the WGS84 reference ellipsoid."""

    A = 6378137.0
    F = 1.0 / 298.257223563
    K0 = 0.9996

    @classmethod
    def latlon_to_utm(cls, latitude: float, longitude: float) -> UTMPoint:
        """Converts geodetic latitude/longitude in decimal degrees to UTM coordinates."""
        if not -80.0 <= latitude <= 84.0:
            raise CoordinateOutOfBoundsError(
                f"Latitude {latitude}° out of standard UTM limits (-80° to 84°)"
            )
        if not -180.0 <= longitude <= 180.0:
            raise CoordinateOutOfBoundsError(
                f"Longitude {longitude}° out of valid bounds (-180° to 180°)"
            )

        zone_number = int((longitude + 180.0) / 6.0) + 1
        lon_origin = (zone_number - 1) * 6 - 180 + 3
        lon_origin_rad = math.radians(lon_origin)

        lat_rad = math.radians(latitude)
        lon_rad = math.radians(longitude)

        e_sq = 2 * cls.F - cls.F**2
        e_prime_sq = e_sq / (1.0 - e_sq)

        n = cls.A / math.sqrt(1.0 - e_sq * (math.sin(lat_rad) ** 2))
        t = math.tan(lat_rad) ** 2
        c = e_prime_sq * (math.cos(lat_rad) ** 2)
        a = math.cos(lat_rad) * (lon_rad - lon_origin_rad)

        m = cls.A * (
            (1.0 - e_sq / 4.0 - 3.0 * (e_sq**2) / 64.0 - 5.0 * (e_sq**3) / 256.0) * lat_rad
            - (3.0 * e_sq / 8.0 + 3.0 * (e_sq**2) / 32.0 + 45.0 * (e_sq**3) / 1024.0)
            * math.sin(2.0 * lat_rad)
            + (15.0 * (e_sq**2) / 256.0 + 45.0 * (e_sq**3) / 1024.0) * math.sin(4.0 * lat_rad)
            - (35.0 * (e_sq**3) / 3072.0) * math.sin(6.0 * lat_rad)
        )

        easting = (
            cls.K0
            * n
            * (
                a
                + (1.0 - t + c) * (a**3) / 6.0
                + (5.0 - 18.0 * t + t**2 + 72.0 * c - 58.0 * e_prime_sq) * (a**5) / 120.0
            )
            + 500000.0
        )

        northing = cls.K0 * (
            m
            + n
            * math.tan(lat_rad)
            * (
                (a**2) / 2.0
                + (5.0 - t + 9.0 * c + 4.0 * (c**2)) * (a**4) / 24.0
                + (61.0 - 58.0 * t + t**2 + 600.0 * c - 330.0 * e_prime_sq) * (a**6) / 720.0
            )
        )

        if latitude < 0:
            northing += 10000000.0

        zone_letter = "N" if latitude >= 0 else "S"
        return UTMPoint(
            easting=round(easting, 4),
            northing=round(northing, 4),
            zone_number=zone_number,
            zone_letter=zone_letter,
        )
