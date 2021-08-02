import argparse
from datetime import datetime
import os

from SunScreenServer import SolarEdgeManager, Windmanager
from SunScreenServer.adafruitPoster import post_to_adafruit
from SunScreenServer.SolarEdgeManager import theoretical_solar_output

from . import OpenPosCalc, OpenWeatherManager, SunManager, TimeManager
from .GetSecrets import append_json, get_secrets, write_json
from .ScreenMover import move_sunscreen, set_checks_status


def main():
    print('Running all checks')
    try:
        secrets = get_secrets()
        onecall = OpenWeatherManager.get_Open_Weather_JSON()
        owm_OK = OpenWeatherManager.should_sunscreen_open(onecall)
        solar_noon = OpenWeatherManager.get_solar_noon(onecall['current'])
        outside_temp_celcius = onecall['current']['temp'] - 273.15

        post_to_adafruit("solar-theoretical", theoretical_solar_output(outside_temp_celcius))

        sm_OK = SunManager.should_sunscreen_open(solar_noon)
        tm_OK = TimeManager.should_sunscreen_open()
        wind_OK = not Windmanager.screen_should_close()
        solarEdge_OK = not SolarEdgeManager.screen_should_close(outside_temp_celcius)
        checks = [owm_OK, sm_OK, tm_OK, wind_OK, solarEdge_OK]
        set_checks_status(checks)

        print(checks)
        check_dict = OpenWeatherManager.check_list(onecall)
        check_dict['sunmgr'] = not sm_OK
        check_dict['timemgr'] = not tm_OK
        check_dict['windmgr'] = not wind_OK
        check_dict['solarEdgeMgr'] = not solarEdge_OK
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
                solar_noon, adjustment=secrets['PERCENTAGE_CORRECTION'])
            print("All checks OK!")
            move_sunscreen(percent_open)
        else:
            print("Not checks OK!")
            move_sunscreen(0)

    except Exception as e:
        move_sunscreen(0)

        print('Exception!: '+e)
        pass

def wind():
    print('Checking wind speeds and uploading to Adafruit')
    Windmanager.post_to_adafruit()
    if(Windmanager.screen_should_close()):
        move_sunscreen(0)

if __name__ == '__main__':
    # Lower priority
    value = 5
    niceValue = os.nice(value)
    print("\nCurrent nice value of the process:", niceValue)

    parser = argparse.ArgumentParser(description='Manage the sun screen')
    parser.add_argument("--wind", help="Do only a wind check")
    args = parser.parse_args()
    if args.wind:
        wind()
    else:
        main()
