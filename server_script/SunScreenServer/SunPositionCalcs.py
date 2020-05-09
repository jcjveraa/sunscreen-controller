from time import time
from datetime import datetime
from math import sin, cos, asin, acos, pi

DEG_TO_RAD = pi/180


def solar_hour_angle(solar_noon: float, in_radians=True, reference_time=None) -> float:
    """Returns the current solar angle in degrees or radian - https://en.wikipedia.org/wiki/Hour_angle"""
    degrees_per_second = 15.0/3600.0
    if reference_time is None:
        reference_time = time()
    result = (reference_time - solar_noon) * degrees_per_second
    # print("Hour angle: "+str(result))
    if in_radians:
        result *= DEG_TO_RAD
    return result


def incidence_angle(solar_azimuth_deg: float, house_angle: float, in_radians=True) -> float:
    result = solar_azimuth_deg - house_angle
    if in_radians:
        result *= DEG_TO_RAD
    return result


def solar_declination(reference_time=None) -> float:
    """Returns solar declination in Radian https://en.wikipedia.org/wiki/Position_of_the_Sun#Calculations"""
    if reference_time is None:
        reference_time = time()
    dt_object = datetime.fromtimestamp(reference_time)
    # uses tm_yday https://docs.python.org/3.8/library/time.html#time.struct_time
    N = dt_object.timetuple()[7] - 1

    term_1 = 0.98565 * DEG_TO_RAD * (N + 10)
    term_2 = 1.914 * sin(0.98565 * DEG_TO_RAD * (N - 2)) * DEG_TO_RAD
    term_3 = sin(-23.44*DEG_TO_RAD) * cos(term_1 + term_2)
    return asin(term_3)


def cosine_of_solar_zenith(solar_noon: float, latitude: float, reference_time=None) -> float:
    """Returns solar Zenith in Radian https://en.wikipedia.org/wiki/Solar_zenith_angle"""
    term_1 = sin(latitude) * sin(solar_declination(reference_time))
    term_2 = cos(latitude) * cos(solar_declination(reference_time)) * \
        cos(solar_hour_angle(solar_noon,
                             reference_time=reference_time))

    return term_1 + term_2


def solar_azimuth_compass(solar_noon: float, latitude: float, reference_time=None, in_degrees=True):
    """From https://en.wikipedia.org/wiki/Solar_azimuth_angle"""
    if reference_time is None:
        reference_time = time()
    cos_zenith = cosine_of_solar_zenith(solar_noon, latitude, reference_time)
    term_1 = sin(solar_declination(reference_time)) - \
        cos_zenith * sin(latitude)
    term_2 = sin(acos(cos_zenith)) * cos(latitude)
    result = acos(term_1/term_2)
    # acos is symetrical
    if reference_time > solar_noon:
        result = 2*pi - result
    if in_degrees:
        return result / DEG_TO_RAD
    else:
        return result
