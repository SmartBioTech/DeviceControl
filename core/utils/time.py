
from datetime import datetime


def now():
    return str(datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S.%f"))


def process_time(time):
    """
    Processes the input string to a format the database can work with.
    :param time: requested time
    :return: processed time
    """
    if time == None:
        return
    try:
        processed = datetime.strptime(time, "%Y%m%d%H%M%S%f")
        return "'" + processed.strftime("%Y-%m-%d %H:%M:%S.%f") + "'"
    except Exception:
        raise SyntaxError("Invalid time format has been provided")