from flask import Flask, request, Response, jsonify

from core.data.manager import DataManager
from core.device.manager import DeviceManager
from core.manager import AppManager
from core.task.manager import TaskManager
from core.utils.singleton import singleton
from core.utils.time import process_time


@singleton
class Server:

    def __init__(self):

        self.app_manager = AppManager(TaskManager(), DeviceManager(), DataManager())
        self.server = Flask(__name__)

        self.SUCCESS = Response(status=200)
        self.BAD_REQUEST = Response(status=400)
        self.UNAUTHORIZED = Response(status=401)
        self.ERROR = Response(status=500)
        self.register_endpoints()

    def start(self):
        self.server.run(host='0.0.0.0')

    def register_endpoints(self):

        @self.server.route('/device', methods=["POST"])
        def initiate():
            device_config = request.get_json()

            success, cause, data = self.app_manager.register_device(device_config)

            if success:
                return self.SUCCESS

            return self.BAD_REQUEST

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
                return self.BAD_REQUEST

            if success:
                return self.SUCCESS
            else:
                return self.BAD_REQUEST

        @self.server.route('/ping')
        def ping():
            success, cause, data = self.app_manager.ping()
            if success:
                return data

        @self.server.route('/command', methods=["POST"])
        def command():
            data: dict = request.get_json()
            device_id = data.get("device_id")
            cmd_id = data.get("command_id")
            args = data.get("arguments", "[]")
            source = data.get("source", "external")

            success, cause, data = self.app_manager.command(device_id, cmd_id, args, source)

            if success:
                return self.SUCCESS

            return self.BAD_REQUEST

        @self.server.route('/task', methods=["POST"])
        def task():
            data: dict = request.get_json()

            success, cause, data = self.app_manager.register_task(data)

            if success:
                return self.SUCCESS

            return self.BAD_REQUEST

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
                    return jsonify(False, e, None)
            return jsonify(self.app_manager.get_data(device_id, log_id=log_id, time=time))
