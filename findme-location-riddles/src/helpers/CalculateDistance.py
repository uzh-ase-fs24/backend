import math


def haversine_distance(coord1, coord2):
    """
    Calculate the great circle distance between two coordinates on the Earth's surface.

    Parameters:
    - coord1 (tuple): Latitude and longitude of the first point (degrees).
    - coord2 (tuple): Latitude and longitude of the second point (degrees).

    Returns:
    - float: Distance between two coordinates in kilometers.
    """
    # Coordinates in decimal degrees (e.g., 37.7749, -122.4194)
    lat1, lon1 = coord1
    lat2, lon2 = coord2

    # Radius of the Earth in kilometers
    R = 6371.0

    # Convert decimal degrees to radians
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    delta_phi = math.radians(lat2 - lat1)
    delta_lambda = math.radians(lon2 - lon1)

    # Haversine formula
    a = math.sin(delta_phi / 2.0) ** 2 + math.cos(phi1) * math.cos(phi2) * math.sin(delta_lambda / 2.0) ** 2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))

    # Distance in kilometers
    distance = R * c
    return distance
