from threading import Event, Thread
from typing import Callable

import socketio

from core.data.manager import DataManager
from core.device.manager import DeviceManager
from core.flow.workflow import WorkflowProvider, Job
from core.manager import AppManager
from core.task.manager import TaskManager
from core.utils.singleton import singleton


@singleton
class Client:
    def __init__(self):
        self.ws = socketio.Client()
        self.connected = False
        self.app_manager = AppManager(TaskManager(), DeviceManager(), DataManager(self))
        self.scheduler = WorkflowProvider().scheduler
        self.is_sending_data = False
        self.unsent_data = []
        self._url = None

    def start(self, url):
        self._url = url
        self.register_events()
        self.connect()
        self._sync_unsent_data()
        self.ws.wait()

    def _job(self, task: Callable, args=None):
        if args is None:
            args = []
        job = Job(task=task, args=args)
        self.scheduler.schedule_job(job)
        job.is_done.wait(30)
        return job.success, job.cause, job.data

    def _handle_connection_fail(self, e: Exception):
        print(f"Connection Failed: {repr(e)}")
        print("Reconnecting...")
        self.ws.sleep(2)

    def connect(self):
        while not self.connected:
            try:
                self.ws.connect(self._url)
            except socketio.client.exceptions.ConnectionError as e:
                self._handle_connection_fail(e)

    def register_events(self):
        @self.ws.event
        def connect():
            self.connected = True
            print(f"Connected: {self.connected}")

        @self.ws.event
        def connect_error(message):
            self.connected = False
            self._handle_connection_fail(ConnectionAbortedError(message))

        @self.ws.event
        def disconnect():
            self.connected = False
            self._handle_connection_fail(ConnectionAbortedError("Disconnected"))

        @self.ws.on('initiate_device')
        def initiate_device(message):
            return self._job(self.app_manager.register_device, [message])

        @self.ws.on('initiate_task')
        def initiate_task(message):
            return self._job(self.app_manager.register_task, [message])

        @self.ws.on('end')
        def end(message):
            _type = message.get("type")
            target_id = message.get("target_id")

            if _type == "device":
                return self._job(self.app_manager.end_device, [target_id])

            elif _type == "task":
                return self._job(self.app_manager.end_task, [target_id])

            elif _type == "all":
                return self._job(self.app_manager.end)

            else:
                return False, repr(AttributeError("Invalid type was provided")), None

        @self.ws.on('command')
        def command(message):
            return self._job(self.app_manager.command, [message])

        @self.ws.on('ping')
        def ping():
            job = Job(self.app_manager.ping)
            self.scheduler.schedule_job(job)
            job.is_done.wait(30)
            return job.success, job.cause, job.data

    def _on_send_data_fail(self, command):
        print("Server failed to accept data. Resending...")
        self.ws.sleep(1)
        self.unsent_data.append(command)

    def send_data(self, command):
        if self.connected:
            response = Response()
            self.ws.emit("data", command, callback=response.respond)
            response.resolved.wait(30)
            if response.success:
                return

        print("send data fail")
        self._on_send_data_fail(command)

    def _sync_unsent_data(self):
        def sync():
            while True:
                while self.unsent_data:
                    command = self.unsent_data.pop()
                    self.send_data(command)
                self.ws.sleep(10)

        Thread(target=sync).start()


class Response:
    def __init__(self):
        self.resolved = Event()
        self.success = False
        self.cause = repr(TimeoutError("Server failed to react"))
        self.data = None

    def respond(self, success, cause, data):
        self.success = success
        self.cause = cause
        self.data = data
        self.resolved.set()
