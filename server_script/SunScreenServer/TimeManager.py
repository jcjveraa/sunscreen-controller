from datetime import datetime

def should_sunscreen_open() -> bool:
    """Returns True between 8h and 20h local time"""
    now = datetime.now()
    return now.hour > 8 and now.hour < 20
