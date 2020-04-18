from SunScreenServer import OpenWeatherManager as owm

def move_sunscreen(direction_open: bool):
    pass

LOW_TEMP = 20.0
HIGH_WIND = 3.6

try:
    move_sunscreen(owm.should_sunscreen_open(LOW_TEMP, HIGH_WIND))
except Exception as e:
    move_sunscreen(False)
    pass
