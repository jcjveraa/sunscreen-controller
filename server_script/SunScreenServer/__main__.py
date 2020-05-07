import math
import traceback
from SunScreenServer.GetSecrets import append_json, write_json, get_secrets
from datetime import datetime
import requests

from . import OpenWeatherManager, SunManager, TimeManager, OpenPosCalc

def move_sunscreen(percent_open: int):
    """Sends a command to the control unit - now via a Get request"""
    secrets = get_secrets()
    operate_url = "http://{}/Operate?targetPercentageOpen={}&key={}&timestamp={}"

    print("moving to " + str(percent_open))

    operate_url = operate_url.format(
        secrets["ESP_IP"], percent_open, secrets["ESP_KEY"], datetime.timestamp(datetime.now()))
    print(operate_url)
    r = requests.get(operate_url)
    try:
        print(r.status_code)
        print(r.json())
    except:
        print('Some exception occured...')
        pass
    print(r.status_code)


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
        check_dict['position'] = OpenPosCalc.get_open_percentage_required(
            solar_noon)
        append_json('log.json', check_dict)
        write_json(onecall, 'file_dumps/onecall_' +
                   str(int(check_dict['timestamp']))+'.json')

        if(all(checks)):
            percent_open = OpenPosCalc.get_open_percentage_required(
                solar_noon, adjustment=10)
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
