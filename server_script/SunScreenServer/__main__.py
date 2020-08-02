import math
import traceback
from datetime import datetime

from SunScreenServer import Windmanager

from . import OpenPosCalc, OpenWeatherManager, SunManager, TimeManager
from .GetSecrets import append_json, get_secrets, write_json
from .ScreenMover import move_sunscreen


def main():
    try:
        secrets = get_secrets()
        onecall = OpenWeatherManager.get_Open_Weather_JSON()
        owm_OK = OpenWeatherManager.should_sunscreen_open(onecall)
        solar_noon = OpenWeatherManager.get_solar_noon(onecall['current'])
        sm_OK = SunManager.should_sunscreen_open(solar_noon)
        tm_OK = TimeManager.should_sunscreen_open()
        wind_OK = not Windmanager.screen_should_close()
        checks = [owm_OK, sm_OK, tm_OK, wind_OK]
        print(checks)
        check_dict = OpenWeatherManager.check_list(onecall)
        check_dict['sunmgr'] = not sm_OK
        check_dict['timemgr'] = not tm_OK
        check_dict['windmgr'] = not wind_OK
        now = datetime.now()
        check_dict['time'] = now.strftime("%d-%m-%y %H:%M:%S")
        check_dict['timestamp'] = datetime.timestamp(now)
        check_dict['result'] = all(checks)
        check_dict['position'] = OpenPosCalc.get_open_percentage_required(
            solar_noon)
        if secrets['LOGGING']:
            append_json('log.json', check_dict)
            write_json(onecall, 'file_dumps/onecall_' +
                    str(int(check_dict['timestamp']))+'.json')

        if(all(checks)):
            percent_open = OpenPosCalc.get_open_percentage_required(
                solar_noon, adjustment=3)
            print("All checks OK!")
            move_sunscreen(percent_open)
        else:
            print("Not checks OK!")
            move_sunscreen(0)

    except Exception as e:
        move_sunscreen(0)

        print('Exception!: '+e)
        pass


if __name__ == '__main__':
    main()
