from threading import Thread, Event
from typing import List, Callable

from flask import Flask, request, Response, jsonify

from core.flow.workflow import Job, Scheduler
from core.manager import AppManager
from core.utils.singleton import singleton


@singleton
class Server:

    def __init__(self, app_manager):

        self.app_manager: AppManager = app_manager
        self.server = Flask(__name__)

        self.scheduler = Scheduler

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

            job = Job(task=self.app_manager.register_device, args=[device_config])

            self.scheduler.schedule_job(job)
            job.is_done.wait()

            if job.result:
                return self.SUCCESS

            return self.BAD_REQUEST

        @self.server.route('/end', methods=["POST"])
        def end():
            data = request.get_json()
            _type = data.get("type")
            target_id = data.get("target_id")
            if _type == "device":
                job = Job(task=self.app_manager.end_device, args=[target_id])

            elif _type == "task":
                job = Job(task=self.app_manager.end_task, args=[target_id])

            elif _type == "all":
                job = Job(task=self.app_manager.end)

            else:
                return self.BAD_REQUEST

            self.scheduler.schedule_job(job)
            job.is_done.wait()

            if job.result:
                return self.SUCCESS
            else:
                return self.BAD_REQUEST

        @self.server.route('/ping')
        def ping():
            job = Job(task=self.app_manager.ping)
            self.scheduler.schedule_job(job)
            job.is_done.wait()
            return job.result

        @self.server.route('/command', methods=["POST"])
        def command():
            data: dict = request.get_json()
            device_id = data.get("device_id")
            cmd_id = data.get("command_id")
            args = data.get("arguments", "[]")
            source = data.get("source", "external")

            job = Job(task=self.app_manager.command, args=[device_id, cmd_id, args, source])

            self.scheduler.schedule_job(job)
            job.is_done.wait()

            if job.result:
                return self.SUCCESS

            return self.BAD_REQUEST

        @self.server.route('/task', methods=["POST"])
        def task():
            data: dict = request.get_json()

            job = Job(task=self.app_manager.register_task, args=[data])

            self.scheduler.schedule_job(job)
            job.is_done.wait()

            if job.result:
                return self.SUCCESS

            return self.BAD_REQUEST

        @self.server.route('/data', methods=["GET"])
        def get_data():
            args = dict(request.args)
            device_id = args.get("device_id", None)
            log_id = args.get("log_id", None)
            return jsonify(self.app_manager.get_data(device_id, log_id))


