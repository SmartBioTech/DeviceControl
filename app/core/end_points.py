from flask import request
from ..src.utils.response import Response
from . import main


@main.route('/device', methods=["POST"])
def initiate():
    device_config = request.get_json()
    from .. import app_manager
    response = app_manager.register_device(device_config)
    return response.to_json()


@main.route('/end', methods=["POST"])
def end():
    data = request.get_json()
    _type = data.get("type", None)
    target_id = data.get("target_id", None)
    from .. import app_manager
    if _type == "device":
        response = app_manager.end_device(target_id)
    elif _type == "task":
        response = app_manager.end_task(target_id)
    elif _type == "all":
        response = app_manager.end()
    else:
        e = TypeError("Invalid type to end: {}".format(_type if _type is not None else "not given"))
        response = Response(False, None, e)
    return response.to_json()


@main.route('/ping')
def ping():
    from .. import app_manager
    response = app_manager.ping()
    return response.to_json()


@main.route('/command', methods=["POST"])
def command():
    from .. import app_manager
    data: dict = request.get_json()
    response = app_manager.command(data)
    return response.to_json()


@main.route('/task', methods=["POST"])
def task():
    from .. import app_manager
    data: dict = request.get_json()
    response = app_manager.register_task(data)
    return response.to_json()


@main.route('/data', methods=["GET"])
def get_data():
    from .. import app_manager
    args = dict(request.args)
    response = app_manager.get_data(args)
    return response.to_json()


@main.route('/data/latest', methods=['GET'])
def get_latest_data():
    from .. import app_manager
    args = dict(request.args)
    response = app_manager.get_latest_data(args)
    return response.to_json()
