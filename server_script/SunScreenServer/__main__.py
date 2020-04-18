import math
import traceback
from SunScreenServer.GetSecrets import append_json, write_json
from datetime import datetime

from . import OpenWeatherManager, SunManager, TimeManager


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
        checks = [owm_OK, sm_OK, tm_OK]
        print(checks)
        check_dict = OpenWeatherManager.check_list(onecall)
        check_dict['sunmgr'] = not sm_OK
        check_dict['timemgr'] = not tm_OK
        now = datetime.now()
        check_dict['time'] = now.strftime("%d-%m-%y %H:%M:%S")
        check_dict['timestamp'] = datetime.timestamp(now)
        check_dict['result'] = all(checks)
        append_json('log.json', check_dict)
        write_json(onecall, 'file_dumps/onecall_'+str(int(check_dict['timestamp']))+'.json')

        if(all(checks)):
            move_sunscreen(True)
        else:
            move_sunscreen(False)

    except Exception as e:
        move_sunscreen(False)
        print(e)
        pass


if __name__ == '__main__':
    main()
