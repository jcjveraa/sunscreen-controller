from SunScreenServer import OpenWeatherManager as owm
from SunScreenServer import SunPositionCalcs as spc
from SunScreenServer import SunManager as sm
import math

def move_sunscreen(direction_open: bool):
    pass

try:
    onecall = owm.get_Open_Weather_JSON()
    owm_OK = owm.should_sunscreen_open(onecall)
    solar_noon = owm.get_solar_noon(onecall['current'])
    sm_OK = sm.should_sunscreen_open(solar_noon)


except Exception as e:
    move_sunscreen(False)
    print(e)
    pass
