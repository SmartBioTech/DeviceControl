from flask import Flask, request

from core.data.manager import DataManager
from core.data.model import Response
from core.device.manager import DeviceManager
from core.manager import AppManager
from core.task.manager import TaskManager
from core.utils.singleton import singleton


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
            response = self.app_manager.register_device(device_config)
            return response.to_json()

        @self.server.route('/end', methods=["POST"])
        def end():
            data = request.get_json()
            _type = data.get("type", None)
            target_id = data.get("target_id", None)
            if _type == "device":
                response = self.app_manager.end_device(target_id)
            elif _type == "task":
                response = self.app_manager.end_task(target_id)
            elif _type == "all":
                response = self.app_manager.end()
            else:
                e = TypeError("Invalid type to end: {}".format(_type if _type is not None else "not given"))
                response = Response(False, None, e)
            return response.to_json()

        @self.server.route('/ping')
        def ping():
            response = self.app_manager.ping()
            return response.to_json()

        @self.server.route('/command', methods=["POST"])
        def command():
            data: dict = request.get_json()
            response = self.app_manager.command(data)
            return response.to_json()

        @self.server.route('/task', methods=["POST"])
        def task():
            data: dict = request.get_json()
            response = self.app_manager.register_task(data)
            return response.to_json()

        @self.server.route('/data', methods=["GET"])
        def get_data():
            args = dict(request.args)
            response = self.app_manager.get_data(args)
            return response.to_json()

        @self.server.route('/data/latest', methods=['GET'])
        def get_latest_data():
            args = dict(request.args)
            response = self.app_manager.get_latest_data(args)
            return response.to_json()
