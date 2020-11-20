from typing import Optional

from flask import jsonify


class Response:
    def __init__(self, success: bool, data: Optional[dict], cause: Optional[Exception] = None):
        self.cause = cause
        self.data = data
        self.success = success

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
