"""Closed-form inverse geodetic transformation (ECEF to WGS84 Geodetic)."""

import math
from src.transforms.geodetic import ECEFPoint, GeodeticPoint, WGS84_A, WGS84_B, WGS84_E_SQ


class InverseCoordinateTransformer:
    """Performs inverse transformation from Cartesian ECEF coordinates to WGS84 Geodetic."""

    E_PRIME_SQ = (WGS84_A**2 - WGS84_B**2) / (WGS84_B**2)

    @classmethod
    def ecef_to_geodetic(cls, ecef: ECEFPoint) -> GeodeticPoint:
        """Converts ECEF Cartesian coordinates (x, y, z) into WGS84 latitude, longitude, and height."""
        p = math.sqrt(ecef.x_m**2 + ecef.y_m**2)

        if p < 1e-6:
            # Polar singularity handling
            lat = 90.0 if ecef.z_m > 0 else -90.0
            lon = 0.0
            alt = abs(ecef.z_m) - WGS84_B
            return GeodeticPoint(latitude_deg=lat, longitude_deg=lon, altitude_m=round(alt, 4))

        # Bowring's closed-form parametric approximation
        theta = math.atan2(ecef.z_m * WGS84_A, p * WGS84_B)

        lat_rad = math.atan2(
            ecef.z_m + cls.E_PRIME_SQ * WGS84_B * (math.sin(theta) ** 3),
            p - WGS84_E_SQ * WGS84_A * (math.cos(theta) ** 3),
        )
        lon_rad = math.atan2(ecef.y_m, ecef.x_m)

        sin_lat = math.sin(lat_rad)
        n = WGS84_A / math.sqrt(1.0 - WGS84_E_SQ * (sin_lat**2))
        alt_m = (p / math.cos(lat_rad)) - n

        return GeodeticPoint(
            latitude_deg=round(math.degrees(lat_rad), 8),
            longitude_deg=round(math.degrees(lon_rad), 8),
            altitude_m=round(alt_m, 4),
        )
