import math
from dataclasses import dataclass

# WGS84 Ellipsoid Constants
WGS84_A = 6378137.0  # Semi-major axis (meters)
WGS84_F = 1.0 / 298.257223563  # Flattening factor
WGS84_B = WGS84_A * (1.0 - WGS84_F)
WGS84_E_SQ = 1.0 - (WGS84_B**2 / WGS84_A**2)  # First eccentricity squared


@dataclass(frozen=True)
class GeodeticPoint:
    latitude_deg: float
    longitude_deg: float
    altitude_m: float


@dataclass(frozen=True)
class ECEFPoint:
    x_m: float
    y_m: float
    z_m: float


class CoordinateTransformer:
    """Rigorous WGS84 Geodetic to Earth-Centered, Earth-Fixed (ECEF) conversions."""

    @staticmethod
    def geodetic_to_ecef(point: GeodeticPoint) -> ECEFPoint:
        lat_rad = math.radians(point.latitude_deg)
        lon_rad = math.radians(point.longitude_deg)

        sin_lat = math.sin(lat_rad)
        cos_lat = math.cos(lat_rad)
        sin_lon = math.sin(lon_rad)
        cos_lon = math.cos(lon_rad)

        # Prime vertical radius of curvature
        n_rad = WGS84_A / math.sqrt(1.0 - WGS84_E_SQ * (sin_lat**2))

        x = (n_rad + point.altitude_m) * cos_lat * cos_lon
        y = (n_rad + point.altitude_m) * cos_lat * sin_lon
        z = (n_rad * (1.0 - WGS84_E_SQ) + point.altitude_m) * sin_lat

        return ECEFPoint(x_m=round(x, 4), y_m=round(y, 4), z_m=round(z, 4))

    @staticmethod
    def haversine_distance(p1: GeodeticPoint, p2: GeodeticPoint) -> float:
        """Great-circle distance over mean spherical Earth surface."""
        r = 6371000.0  # Mean radius in meters
        d_lat = math.radians(p2.latitude_deg - p1.latitude_deg)
        d_lon = math.radians(p2.longitude_deg - p1.longitude_deg)
        lat1 = math.radians(p1.latitude_deg)
        lat2 = math.radians(p2.latitude_deg)

        a = (math.sin(d_lat / 2) ** 2) + math.cos(lat1) * math.cos(lat2) * (
            math.sin(d_lon / 2) ** 2
        )
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
        return r * c
