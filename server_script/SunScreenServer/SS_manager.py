import OpenWeatherManager as owm

def move_sunscreen(direction_open: bool):
    pass

try:
    onecall = owm.get_Open_Weather_JSON()
    next_fcst = owm.get_next_forecast(onecall)
    rain_check = owm.forecast_has_rain(next_fcst)
    wind_check = owm.forecast_has_high_winds(next_fcst, 3.6)
    print(next_fcst)

except Exception as e:
    move_sunscreen(False)
    pass
