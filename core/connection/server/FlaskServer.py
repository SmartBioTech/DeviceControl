from flask import Flask, request, Response

from core.manager import AppManager

app = Flask(__name__)
manager = AppManager()

SUCCESS = Response(status=200)
BAD_REQUEST = Response(status=400)
UNAUTHORIZED = Response(status=401)
ERROR = Response(status=500)


@app.route('/device', methods=["POST"])
def initiate():
    device_config = request.get_json()
    if manager.register_device(device_config):
        return SUCCESS
    return BAD_REQUEST


@app.route('/end', methods=["POST"])
def end():
    data = request.get_json()
    _type = data.get("type")
    target_id = data.get("target_id")
    if _type == "device":
        if manager.end_device(target_id):
            return SUCCESS
        else:
            return BAD_REQUEST
    elif _type == "task":
        if manager.end_task(target_id):
            return SUCCESS
        else:
            return BAD_REQUEST
    elif _type == "all":
        manager.end()
        return SUCCESS


@app.route('/ping')
def ping():
    return manager.ping()


@app.route('/command', methods=["POST"])
def command():
    data: dict = request.get_json()
    device_id = data.get("device_id")
    cmd_id = data.get("command_id")
    args = data.get("arguments", "[]")
    source = data.get("source", "external")
    if manager.command(device_id, cmd_id, args, source):
        return SUCCESS
    else:
        return BAD_REQUEST


@app.route('/task', methods=["POST"])
def task():
    data: dict = request.get_json()
    if manager.register_task(data):
        return SUCCESS
    else:
        return BAD_REQUEST


if __name__ == '__main__':
    app.run()
