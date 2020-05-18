from typing import Optional

from flask import Flask, request, jsonify

from core.data.manager import DataManager
from core.device.manager import DeviceManager
from core.manager import AppManager
from core.task.manager import TaskManager
from core.utils.singleton import singleton
from core.utils.time import process_time


class Response:
    def __init__(self, success: bool, cause: Optional[Exception], data: Optional[dict]):
        self.success = success
        self.cause = cause
        self.data = data

    def to_json(self):
        return jsonify(
            {
                "success": self.success,
                "cause": self.cause,
                "data": self.data,
            }
        )


@singleton
class Server:

    def __init__(self):

        self.app_manager = AppManager(TaskManager(), DeviceManager(), DataManager())
        self.server = Flask(__name__)
        self.register_endpoints()

    def start(self):
        self.server.run(host='0.0.0.0')

    def register_endpoints(self):

        @self.server.route('/device', methods=["POST"])
        def initiate():
            device_config = request.get_json()

            success, cause, data = self.app_manager.register_device(device_config)

            return Response(success, cause, data).to_json()

        @self.server.route('/end', methods=["POST"])
        def end():
            data = request.get_json()
            _type = data.get("type")
            target_id = data.get("target_id")
            if _type == "device":
                success, cause, data = self.app_manager.end_device(target_id)

            elif _type == "task":
                success, cause, data = self.app_manager.end_task(target_id)

            elif _type == "all":
                success, cause, data = self.app_manager.end()
            else:
                e = TypeError("Invalid type to end")
                return Response(False, e, None).to_json()

            return Response(success, cause, data).to_json()

        @self.server.route('/ping')
        def ping():
            success, cause, data = self.app_manager.ping()
            return Response(success, cause, data).to_json()

        @self.server.route('/command', methods=["POST"])
        def command():
            data: dict = request.get_json()
            device_id = data.get("device_id")
            cmd_id = data.get("command_id")
            args = data.get("arguments", "[]")
            source = data.get("source", "external")

            success, cause, data = self.app_manager.command(device_id, cmd_id, args, source)

            return Response(success, cause, data).to_json()

        @self.server.route('/task', methods=["POST"])
        def task():
            data: dict = request.get_json()
            success, cause, data = self.app_manager.register_task(data)
            return Response(success, cause, data).to_json()

        @self.server.route('/data', methods=["GET"])
        def get_data():
            args = dict(request.args)
            device_id = args.get("device_id", None)
            log_id = args.get("log_id", None)
            time = args.get("time", None)
            if time is not None:
                try:
                    time = process_time(time)
                except SyntaxError as e:
                    return Response(False, e, None).to_json()
            success, cause, data = self.app_manager.get_data(device_id, log_id=log_id, time=time)
            return Response(success, cause, data).to_json()

        @self.server.route('/data/latest', methods=['GET'])
        def get_latest_data():
            args = dict(request.args)
            device_id = args.get("device_id", None)
            success, cause, data = self.app_manager.get_latest_data(device_id)
            return Response(success, cause, data).to_json()
