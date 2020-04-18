from time import time
from datetime import datetime
import math

DEG_TO_RAD = 0.0174532925


def solar_hour_angle(solar_noon: float, in_radians=True, reference_time=None) -> float:
    """Returns the current solar angle in degrees or radian - https://en.wikipedia.org/wiki/Hour_angle"""
    degrees_per_second = 15.0/3600.0
    if reference_time is None:
        reference_time = time()
    result = (reference_time - solar_noon) * degrees_per_second
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
    term_2 = 1.914 * math.sin(0.98565 * DEG_TO_RAD * (N - 2)) * DEG_TO_RAD
    term_3 = math.sin(23.44*DEG_TO_RAD) * math.cos(term_1 + term_2)
    return -math.asin(term_3)


def cosine_of_solar_zenith(solar_noon: float, latitude: float, reference_time=None) -> float:
    """Returns solar Zenith in Radian https://en.wikipedia.org/wiki/Solar_zenith_angle"""
    term_1 = math.sin(latitude) * math.sin(solar_declination(reference_time))
    term_2 = math.cos(latitude) * math.cos(solar_declination(reference_time)
                                           ) * math.cos(solar_hour_angle(solar_noon, reference_time=reference_time))

    return term_1 + term_2


def current_sun_azimuth(solar_noon: float, latitude: float, reference_time=None):
    """Gets the current sun azimuth https://en.wikipedia.org/wiki/Solar_azimuth_angle"""
