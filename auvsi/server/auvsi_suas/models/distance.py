"""Functions for computing distance."""

import math
from auvsi_suas.models import units


def haversine(lon1, lat1, lon2, lat2):
    """
    Calculate the great circle distance between two points
    on the earth (specified in decimal degrees).

    Reference:
    http://stackoverflow.com/questions/4913349/haversine-formula-in-python-bearing-and-distance-between-two-gps-points

    Args:
        lon1, lat1: The latitude and longitude of position 1
        lon2, lat2: The latitude and longitude of position 2

    Returns:
        The distance in kilometers
    """
    # convert decimal degrees to radians
    lon1 = math.radians(lon1)
    lat1 = math.radians(lat1)
    lon2 = math.radians(lon2)
    lat2 = math.radians(lat2)

    # haversine formula
    dlon = lon2 - lon1
    dlat = lat2 - lat1
    hav_a = (math.sin(dlat / 2) ** 2 + math.cos(lat1) * math.cos(lat2) *
             math.sin(dlon / 2) ** 2)
    hav_c = 2 * math.asin(math.sqrt(hav_a))

    # 6367 km is the radius of the Earth
    dist_km = 6371 * hav_c
    return dist_km


def distance_to(
    latitude_1, longitude_1, altitude_1, latitude_2, longitude_2, altitude_2
):
    """Get the distance in feet between the two positions.

    Args:
        latitude_1: The latitude of the first position.
        longitude_1: The longitude of the first position.
        altitude_1: The altitude in feet of the first position.
        latitude_2: The latitude of the second position.
        longitude_2: The longitude of the second position.
        altitude_2: The altitude in feet of the second position.
    """
    gps_dist_km = haversine(longitude_1, latitude_1, longitude_2, latitude_2)
    gps_dist_ft = units.kilometers_to_feet(gps_dist_km)
    alt_dist_ft = abs(altitude_1 - altitude_2)
    return math.hypot(gps_dist_ft, alt_dist_ft)
