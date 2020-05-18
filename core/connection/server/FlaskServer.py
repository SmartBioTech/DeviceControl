from flask import Flask, request

from core.data.manager import DataManager
from core.device.manager import DeviceManager
from core.manager import AppManager
from core.task.manager import TaskManager
from core.utils.singleton import singleton
from core.utils.networking import Response


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
            if _type == "device":
                success, cause, data = self.app_manager.end_device(data)

            elif _type == "task":
                success, cause, data = self.app_manager.end_task(data)

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
            config: dict = request.get_json()
            success, cause, data = self.app_manager.command(config)
            return Response(success, cause, data).to_json()

        @self.server.route('/task', methods=["POST"])
        def task():
            data: dict = request.get_json()
            success, cause, data = self.app_manager.register_task(data)
            return Response(success, cause, data).to_json()

        @self.server.route('/data', methods=["GET"])
        def get_data():
            config = dict(request.args)
            success, cause, data = self.app_manager.get_data(config)
            return Response(success, cause, data).to_json()
