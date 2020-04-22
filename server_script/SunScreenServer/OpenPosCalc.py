from SunScreenServer.SunPositionCalcs import cosine_of_solar_zenith
from math import acos, tan, pi


def get_open_percentage_required(solar_noon: float, latitude: float, reference_time=None) -> int:
    """Retuns the percentage that the sunscreen should open"""
    elevation_angle = 0.5*pi - \
        acos(cosine_of_solar_zenith(solar_noon, latitude, reference_time))

    return open_percentage_required(elevation_angle)


def open_percentage_required(elevation_angle=None) -> int:
    """Factors veru specific for my set up, to be generalized"""
    tan_of_elevation_angle = tan(elevation_angle)
    a = 8
    b = 62
    c = 255
    d = 299
    result = (c - tan_of_elevation_angle*a)/(d*tan_of_elevation_angle+b)
    # Return result between 0 and 100
    return int(min(100, max(0, 100 * result)))
