from SunScreenServer.GetSecrets import get_secrets
from SunScreenServer.SunPositionCalcs import solar_azimuth_compass, DEG_TO_RAD


def sun_not_on_window(azimuth_current: float, azimuth_lower: float, azimuth_higher: float) -> bool:
    return not (azimuth_current > azimuth_lower and azimuth_current < azimuth_higher)


def should_sunscreen_open(solar_noon):
    secrets = get_secrets()
    current_azimuth = solar_azimuth_compass(
        solar_noon, secrets['LAT'] * DEG_TO_RAD)

    checks = list()

    # Check the current weather
    checks.append(sun_not_on_window(current_azimuth,
                                    secrets['AZIMUTH_SUNUP'], secrets['AZIMUTH_SUNDOWN']))

    return not any(checks)
