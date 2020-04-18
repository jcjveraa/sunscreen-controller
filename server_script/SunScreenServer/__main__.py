from . import OpenWeatherManager, SunManager, TimeManager
import math
import traceback

def move_sunscreen(direction_open: bool):
    if(direction_open):
        print("Opening!")
    else:
        print("Closing!")
    pass

def main():
    try:
        onecall = OpenWeatherManager.get_Open_Weather_JSON()
        owm_OK = OpenWeatherManager.should_sunscreen_open(onecall)
        solar_noon = OpenWeatherManager.get_solar_noon(onecall['current'])
        sm_OK = SunManager.should_sunscreen_open(solar_noon)
        tm_OK = TimeManager.should_sunscreen_open()

    except Exception as e:
        move_sunscreen(False)
        print(e)
        pass


if __name__ == '__main__':
    main()
