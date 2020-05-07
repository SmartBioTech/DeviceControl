from datetime import datetime


def now():
    return str(datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S"))


def process_time(time):
    """
    Processes the input string to a format the database can work with.
    :param time: requested time
    :return: processed time
    """
    if time == None:
        return
    try:
        processed = "'" + time[:4] + '-' \
                    + time[4:6] + '-' + time[6:8] \
                    + ' ' + time[8:10] + ':' \
                    + time[10:12] + ':' \
                    + time[12:14] + "'"
        return processed
    except IndexError:
        raise SyntaxError("Invalid time format has been provided")
