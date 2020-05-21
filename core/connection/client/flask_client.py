import json
from enum import IntEnum
from json import JSONDecodeError
from threading import Thread, Lock
from time import sleep
from typing import List, Optional

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
        self.app_manager = AppManager(TaskManager(), DeviceManager(), DataManager())
        self.request_types = {
            RequestTypes.INITIATE_DEVICE: self.app_manager.register_device,
            RequestTypes.INITIATE_TASK: self.app_manager.register_task,
            RequestTypes.END_DEVICE: self.app_manager.end_device,
            RequestTypes.END_TASK: self.app_manager.end_task,
            RequestTypes.END: self.app_manager.end,
            RequestTypes.COMMAND: self.app_manager.command,
            RequestTypes.DATA: self.app_manager.get_data,
            RequestTypes.UNKNOWN: None
        }

        self.unsent_data: List[Response] = []
        self.lock = Lock()
        self.sync_manager = SyncManager(self)

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

    @staticmethod
    def on_error(exc: Exception):
        print(f"Error occured while connecting: {repr(exc)}")
        sleep(2)
        print("Retrying...")

    def start(self, server_url):
        self.server_url = server_url
        connected = False
        while not connected:
            try:
                connected = self.connect()
                if not connected:
                    raise ConnectionError("Could not connect to server")
            except ConnectionError as e:
                self.on_error(e)

        self.sync_manager.start_synchronization(5)

    def stop(self):
        self.sync_manager.is_active = False

    def respond(self,
                success: bool,
                cause: Optional[Exception],
                data: dict,
                request_id: Optional[str],
                type_: RequestTypes):

        response = [
            Response(
                request_id,
                type_,
                BaseResponse(success, cause, data)
            )
        ]

        r = self.post(Endpoints.DATA, response)

        if not StatusCodes.is_success(r):
            self.lock.acquire()
            self.unsent_data.extend(response)
            self.lock.release()

    def execute_incoming(self, type_: RequestTypes, config: dict, request_id=None):
        target = self.request_types.get(type_)
        if target is not None:
            success, cause, data = target(config)

        else:
            success, cause, data = False, TypeError("Unknown request type inferred"), None

        self.respond(success, cause, data, request_id, type_)

    def handle_incoming(self, incoming_list: List[dict]):

        for incoming in incoming_list:
            _request_id = incoming.get("id")
            _type = incoming.get("type")
            _config = incoming.get("data")
            Thread(
                target=self.execute_incoming,
                args=[RequestTypes.from_string(_type), _config, _request_id]
            ).start()

    @staticmethod
    def load_token() -> Optional[str]:
        _config = None
        try:
            _config = open("core/connection/client/flask_client_config.json", "r")
            config = json.load(_config)
            token = config.get("token")
        except (JSONDecodeError, FileNotFoundError):
            token = None
        finally:
            if _config is not None:
                _config.close()
        return token

    @staticmethod
    def save_token(token: str):
        with open("core/connection/client/flask_client_config.json", "w") as _config:
            json.dump(
                {"token": token},
                _config
            )
        _config.close()

    def connect(self):
        token = self.load_token()
        if token is not None:
            self.session.headers["token"] = token
        else:
            r = self.get(Endpoints.REGISTER)
            if StatusCodes.is_success(r):
                token = r.json().get("token")
                self.session.headers["token"] = token
                self.save_token(token)

        handshake = self.get(Endpoints.HANDSHAKE)
        return StatusCodes.is_success(handshake)


class SyncManager:
    def __init__(self, client: Client):
        self.client = client
        self.sync_thread: Optional[Thread] = None
        self.is_active = False

    @staticmethod
    def on_error(status_code: int, text: str):
        print(ConnectionError(
            f"Communication with server failed with status code {status_code}."
            f" Error message: {text}"))

    def sync_get(self):
        get = self.client.get(Endpoints.DATA)
        if StatusCodes.is_success(get):
            self.client.handle_incoming(get.json())
        else:
            self.on_error(get.status_code, get.text)
            if StatusCodes.is_unauthorized(get):
                raise ConnectionRefusedError()

    def sync_post(self):
        self.client.lock.acquire()
        post = self.client.post(Endpoints.DATA, self.client.unsent_data)
        if StatusCodes.is_success(post):
            self.client.unsent_data.clear()
        else:
            self.on_error(post.status_code, post.text)
            if StatusCodes.is_unauthorized(post):
                self.client.lock.release()
                raise ConnectionRefusedError()
        self.client.lock.release()

    def sync(self, interval: int):
        threads: List[Thread] = []
        while self.is_active:
            try:
                threads.append(Thread(target=self.sync_get))
                threads.append(Thread(target=self.sync_post))
                [thread.start() for thread in threads]
                [thread.join() for thread in threads]
                sleep(interval)
            except ConnectionRefusedError:
                self.client.connect()
            finally:
                threads.clear()

    def start_synchronization(self, interval: int):
        self.stop_synchronization()
        self.is_active = True
        self.sync_thread = Thread(target=self.sync, args=[interval])
        self.sync_thread.start()

    def stop_synchronization(self):
        self.is_active = False
        if self.sync_thread is not None:
            self.sync_thread.join()
            self.sync_thread = None
