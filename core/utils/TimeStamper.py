from datetime import datetime


def now():
    return str(datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S"))
