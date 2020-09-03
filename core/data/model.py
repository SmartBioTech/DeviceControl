from typing import Optional

from flask import jsonify


class Response:
    def __init__(self, success: bool, data: Optional[dict], cause: Optional[Exception] = None):
        self.cause = cause
        self.data = data
        self.success = success

    def to_json(self):
        return jsonify(
            {
                "success": self.success,
                "cause": self.cause,
                "data": self.data,
            }
        )
