import json
from enum import IntEnum
from json import JSONDecodeError
from threading import Thread, Lock
from time import sleep
from typing import List

from requests import Session
from requests.exceptions import ConnectionError
from requests.models import Response as RequestResponse

from core.data.manager import DataManager
from core.device.manager import DeviceManager
from core.manager import AppManager
from core.task.manager import TaskManager
from core.utils.networking import Endpoints, RequestTypes
from core.utils.networking import Response as BaseResponse


class Response:
    def __init__(self, id_: str, type_: RequestTypes, response: BaseResponse):
        self.data = response.to_dict()
        self.type = type_
        self.id_ = id_

    def to_dict(self):
        return {"id": self.id_, "type": self.type.value, "data": self.data}


class StatusCodes(IntEnum):
    SUCCESS = 200
    BAD_REQUEST = 400
    UNAUTHORIZED = 401

    @classmethod
    def is_success(cls, response: RequestResponse):
        return cls.SUCCESS.value == response.status_code

    @classmethod
    def is_unauthorized(cls, response: RequestResponse):
        return cls.UNAUTHORIZED.value == response.status_code


class Client:

    def __init__(self):
        self.session = Session()
        self.server_url = None
        self.is_active = False
        self.app_manager = AppManager(TaskManager(), DeviceManager(), DataManager())
        self.request_types = {
            RequestTypes.INITIATE_DEVICE: self.app_manager.register_device,
            RequestTypes.INITIATE_TASK: self.app_manager.register_task,
            RequestTypes.END_DEVICE: self.app_manager.end_device,
            RequestTypes.END_TASK: self.app_manager.end_task,
            RequestTypes.END: self.app_manager.end,
            RequestTypes.COMMAND: self.app_manager.command,
            RequestTypes.DATA: self.app_manager.get_data
        }

        self.unsent_data: List[Response] = []
        self.lock = Lock()
        self.sync_threads = []
        self._is_restarting = False

    def get(self, endpoint: Endpoints):
        try:
            return self.session.get(f"{self.server_url}/{endpoint.value}")
        except ConnectionError:
            resp = RequestResponse()
            resp.status_code = 404
            return resp

    def post(self, endpoint: Endpoints, responses: List[Response]):
        to_send = []
        [to_send.append(response.to_dict()) for response in responses]
        try:
            return self.session.post(f"{self.server_url}/{endpoint.value}", json=to_send)
        except ConnectionError:
            resp = RequestResponse()
            resp.status_code = 404
            return resp

    def start(self, server_url):
        def on_error(exc: Exception):
            print(f"Error occured while connecting: {repr(exc)}")
            sleep(2)
            print("Retrying...")

        self.server_url = server_url
        connected = False
        while not connected:
            try:
                connected = self.connect()
                if not connected:
                    raise ConnectionError("Could not connect to server")
            except ConnectionError as e:
                on_error(e)

        self.is_active = True
        self.sync()

    def stop(self):
        self.is_active = False

    def restart(self, server_url=None):
        self.stop()
        [thread.join() for thread in self.sync_threads]
        self.sync_threads.clear()
        if server_url is None:
            self.start(self.server_url)
        else:
            self.start(server_url)
        self._is_restarting = False

    def handle_incoming(self, incoming_list):
        def execute_incoming(type_: RequestTypes, config: dict, request_id=None):
            if type_ is not None:
                target = self.request_types.get(type_)
                if target is not None:
                    success, cause, data = target(config)

                else:
                    success, cause, data = False, TypeError("Unknown request type inferred"), None
            else:
                success, cause, data = False, TypeError("Unknown request type inferred"), None

            response = [
                Response(
                    request_id,
                    type_,
                    BaseResponse(success, cause, data)
                )
            ]

            r = self.post(Endpoints.DATA, response)

            if StatusCodes.is_success(r):
                return
            else:
                self.lock.acquire()
                self.unsent_data.extend(response)
                self.lock.release()

        for incoming in incoming_list:
            _request_id = incoming.get("id")
            _type = incoming.get("type")
            _config = incoming.get("data")
            Thread(
                target=execute_incoming,
                args=[RequestTypes.from_string(_type), _config, _request_id]
            )

    def sync(self):

        def on_error(status_code: int, text: str):
            print(ConnectionError(
                f"Communication with server failed with status code {status_code}."
                f" Error message: {text}")
            )
            if status_code == StatusCodes.UNAUTHORIZED and not self._is_restarting:
                self._is_restarting = True
                Thread(target=self.restart).start()

        def sync_get():
            while self.is_active:
                get = self.get(Endpoints.DATA)
                if StatusCodes.is_success(get):
                    self.handle_incoming(get.json())
                else:
                    on_error(get.status_code, get.text)
                sleep(5)

        def sync_post():
            while self.is_active:
                self.lock.acquire()
                post = self.post(Endpoints.DATA, self.unsent_data)
                if StatusCodes.is_success(post):
                    self.unsent_data.clear()
                else:
                    on_error(post.status_code, post.text)
                self.lock.release()
                sleep(5)

        self.sync_threads.append(Thread(target=sync_get))
        self.sync_threads.append(Thread(target=sync_post))

        [thread.start() for thread in self.sync_threads]

    def connect(self):

        with open("core/connection/client/flask_client_config.json", "r") as _config:
            try:
                config = json.load(_config)
                token = config.get("token")
                if token is not None:
                    self.session.headers["token"] = token
                    r = self.get(Endpoints.HANDSHAKE)
                    if StatusCodes.is_success(r):
                        return
                else:
                    _config.close()
            except JSONDecodeError:
                _config.close()

        r = self.get(Endpoints.REGISTER)
        if StatusCodes.is_success(r):
            token = r.json().get("token")

            with open("core/connection/client/flask_client_config.json", "w") as _config:
                json.dump({"token": token}, _config)
                _config.close()

            self.session.headers["token"] = token
            return True
        else:
            return False
