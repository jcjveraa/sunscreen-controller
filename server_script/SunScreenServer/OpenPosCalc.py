from SunScreenServer.SunPositionCalcs import cosine_of_solar_zenith, DEG_TO_RAD, solar_azimuth_compass, incidence_angle
from SunScreenServer.GetSecrets import get_secrets
from math import acos, tan, pi, cos, ceil


def get_open_percentage_required(solar_noon: float, latitude: float = None, reference_time=None, adjustment=0) -> int:
    """Retuns the percentage that the sunscreen should open"""
    if latitude is None:
        secrets = get_secrets()
        latitude = float(secrets['LAT']) * DEG_TO_RAD
    elevation_angle = 0.5*pi - \
        acos(cosine_of_solar_zenith(solar_noon, latitude, reference_time))
    azimuth_deg = solar_azimuth_compass(solar_noon, latitude, reference_time)
    house_incidence_angle_rad = incidence_angle(
        azimuth_deg, secrets['HOUSE_FACING_DEG'])

    result = open_percentage_required(
        elevation_angle, house_incidence_angle_rad, adjustment)
    print(result)
    # If we are in mode 1, take bigger steps
    if (secrets['CURRENT_MODE'] == 1):
        result = round_to_nearest(result, 50)
    print(result)
    return result


def open_percentage_required(elevation_angle: float, house_incidence_angle_rad: float, adjustment=0) -> int:
    """Factors veru specific for my set up, to be generalized"""
    # print("Elevation: " + str(elevation_angle))
    tan_of_height_angle = tan(elevation_angle)/cos(house_incidence_angle_rad)
    a = 8
    b = 62
    c = 255
    d = 299
    result = (c - tan_of_height_angle*a)/(d*tan_of_height_angle+b)
    # Return result between 0 and 100
    return int(min(100, max(0, 100 * result + adjustment)) )


# return n rounded to the nearest multiple of m
def round_to_nearest(x, base):
    return base * ceil(x/base)
