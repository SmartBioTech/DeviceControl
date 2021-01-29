from datetime import datetime


def now():
    return datetime.utcnow()


def process_time(time):
    """
    Processes the input string to a format the database can work with.
    :param time: requested time
    :return: processed time
    """
    if time is not None:
        try:
            return datetime.strptime(time, "%Y%m%d%H%M%S%f")
        except Exception:
            raise SyntaxError("Invalid time format has been provided: {}".format(time))
