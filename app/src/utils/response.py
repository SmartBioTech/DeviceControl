from flask import jsonify


class Response:
    """
    Represents a response class containing information about the success/failure and returned data of the conducted
    action.
    """
    def __init__(self, success, data, cause):
        self.cause = cause
        self.data = data
        self.success = success

    def __eq__(self, other):
        return self.__dict__ == other.__dict__

    def __str__(self):
        return str(self.__dict__)

    def to_json(self):
        return jsonify(
            {
                "success": self.success,
                "cause": str(self.cause),
                "data": self.data,
            }
        )
