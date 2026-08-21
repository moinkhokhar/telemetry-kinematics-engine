"""Spherical and Great Circle Geodesy calculations (Initial Bearing, Cross-Track Distance)."""

import math

from src.transforms.geodetic import WGS84_A, GeodeticPoint


class GeodesyEngine:
    """Performs spherical navigation calculations along ellipsoidal paths."""

    @staticmethod
    def initial_bearing(origin: GeodeticPoint, destination: GeodeticPoint) -> float:
        """Computes initial forward azimuth / bearing in degrees (0 to 360)."""
        lat1 = math.radians(origin.latitude_deg)
        lat2 = math.radians(destination.latitude_deg)
        d_lon = math.radians(destination.longitude_deg - origin.longitude_deg)

        y = math.sin(d_lon) * math.cos(lat2)
        x = math.cos(lat1) * math.sin(lat2) - math.sin(lat1) * math.cos(lat2) * math.cos(d_lon)

        bearing_rad = math.atan2(y, x)
        bearing_deg = (math.degrees(bearing_rad) + 360.0) % 360.0
        return round(bearing_deg, 4)

    @staticmethod
    def cross_track_distance(
        point: GeodeticPoint, start: GeodeticPoint, end: GeodeticPoint
    ) -> float:
        """Computes shortest spherical cross-track distance (in meters) from a path."""
        d13 = GeodesyEngine._haversine_angular_distance(start, point)
        theta13 = math.radians(GeodesyEngine.initial_bearing(start, point))
        theta12 = math.radians(GeodesyEngine.initial_bearing(start, end))

        d_xt = math.asin(math.sin(d13) * math.sin(theta13 - theta12))
        return round(d_xt * WGS84_A, 4)

    @staticmethod
    def _haversine_angular_distance(p1: GeodeticPoint, p2: GeodeticPoint) -> float:
        lat1 = math.radians(p1.latitude_deg)
        lat2 = math.radians(p2.latitude_deg)
        d_lat = lat2 - lat1
        d_lon = math.radians(p2.longitude_deg - p1.longitude_deg)

        a = (math.sin(d_lat / 2.0) ** 2) + math.cos(lat1) * math.cos(lat2) * (
            math.sin(d_lon / 2.0) ** 2
        )
        return 2.0 * math.atan2(math.sqrt(a), math.sqrt(1.0 - a))
