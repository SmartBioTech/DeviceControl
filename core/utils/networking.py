from enum import Enum
from typing import Optional

from flask import jsonify


class Response:
    def __init__(self, success: bool, cause: Optional[Exception], data: Optional[dict]):
        self.success = success
        self.cause = cause
        self.data = data

    def to_json(self):
        return jsonify(
            self.to_dict()
        )

    def to_dict(self):
        return {
            "success": self.success,
            "cause": self.cause,
            "data": self.data,
        }


class Endpoints(Enum):
    HANDSHAKE = "handshake"
    REGISTER = "register"
    DATA = "data"


class RequestTypes(Enum):
    INITIATE_DEVICE = "initiate_device"
    INITIATE_TASK = "initiate_task"
    END_DEVICE = "end_device"
    END_TASK = "end_task"
    END = "end"
    DATA = "data"
    COMMAND = "command"

    # noinspection PyArgumentList
    @classmethod
    def from_string(cls, string: str):
        string = string.lower()
        try:
            return cls(string)
        except ValueError:
            return None
