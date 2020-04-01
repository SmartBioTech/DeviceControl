from threading import Thread, Event
from typing import List, Callable

from flask import Flask, request, Response

from core.utils.singleton import singleton


@singleton
class Server:

    def __init__(self, app_manager):

        self.app_manager = app_manager
        self.server = Flask(__name__)

        self.scheduler = Scheduler()

        self.SUCCESS = Response(status=200)
        self.BAD_REQUEST = Response(status=400)
        self.UNAUTHORIZED = Response(status=401)
        self.ERROR = Response(status=500)
        self.register_endpoints()
        self.scheduler.start()
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
                if self.app_manager.end_device(target_id):
                    return self.SUCCESS
                else:
                    return self.BAD_REQUEST
            elif _type == "task":
                if self.app_manager.end_task(target_id):
                    return self.SUCCESS
                else:
                    return self.BAD_REQUEST
            elif _type == "all":
                self.app_manager.end()
                return self.SUCCESS

            @self.server.route('/ping')
            def ping():
                return self.app_manager.ping()

            @self.server.route('/command', methods=["POST"])
            def command():
                data: dict = request.get_json()
                device_id = data.get("device_id")
                cmd_id = data.get("command_id")
                args = data.get("arguments", "[]")
                source = data.get("source", "external")
                if self.app_manager.command(device_id, cmd_id, args, source):
                    return self.SUCCESS
                else:
                    return self.BAD_REQUEST

            @self.server.route('/task', methods=["POST"])
            def task():
                data: dict = request.get_json()
                if self.manager.register_task(data):
                    return self.SUCCESS
                else:
                    return self.BAD_REQUEST

            @self.server.route('/data', methods=["GET"])
            def get_data():
                sql_arguments = dict(request.args)
                print(sql_arguments)
                print(type(sql_arguments))
                return self.SUCCESS


class Job:
    def __init__(self, task: Callable, args: []):
        self.task: Callable = task
        self.result = False
        self.is_done = Event()
        self.args: [] = args


class Scheduler(Thread):
    def __init__(self):
        super(Scheduler, self).__init__()
        self.jobs: List[(Job, [])] = []
        self.is_active = True
        self.has_jobs = Event()

    def schedule_job(self, job: Job):
        self.jobs.append(job)

    @staticmethod
    def execute(job: Job):
        job.result = job.task(*job.args)
        job.is_done.set()

    def run(self):
        while self.is_active:
            self.has_jobs.wait()
            while self.jobs:
                self.execute(*self.jobs.pop(0))
            self.has_jobs.clear()
