class IdError(Exception):
    def __init__(self, message):
        self.message = message

    def __eq__(self, other):
        return self.message == other.message


class ClassError(IdError):
    pass
