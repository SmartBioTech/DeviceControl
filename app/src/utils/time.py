from datetime import datetime


def now():
    return datetime.utcnow()


def time_from_string(time):
    """
    Processes the input string to datetime format DB can work with.
    :param time: requested time
    :return: processed time
    """
    if time is not None:
        try:
            return datetime.strptime(time, "%Y%m%d%H%M%S%f")
        except Exception:
            raise SyntaxError("Invalid time format has been provided: {}".format(time))


def time_to_string(time):
    """
    Processes the input datetime to standard string representation.
    :param time: requested time
    :return: processed time
    """
    return datetime.strftime(time, "%Y%m%d%H%M%S%f")
