from threading import Event

from utils.TimeStamper import now


class Command:

    def __init__(self, command_id: int, args: list, source: str):
        self.command_id = command_id
        self.args = args
        self.source = source

        self.time_issued = now()

        self.resolved = Event()
        self.is_valid = None
        self.time_executed = None
        self.response = None

    def __str__(self):
        return "SOURCE:{} ID: {},  IS VALID: {}  RESPONSE: {}".format(
            self.source,
            self.command_id,
            self.is_valid,
            self.response
        )



