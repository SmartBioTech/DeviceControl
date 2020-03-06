from device_module.command import Command
from device_module.device import Device, DeviceManager
from device_module.node import Node
from task_module.task_manager import TaskManager


class Manager:
    def __init__(self):
        self.nodes = {}
        self.devices = {}
        self.taskManager = TaskManager()
        self.deviceManager = DeviceManager()

    def node_exists(self, node_id: str):
        return self.nodes.get(node_id) is not None

    def create_node(self, node_id) -> bool:
        if not self.node_exists(node_id):
            self.nodes[node_id] = Node()
            return True
        else:
            return False

    def register_device(self, config: dict):
        return self.deviceManager.new_device(config)

    def add_device_to_node(self, node_id: str, device: Device):
        if self.node_exists(node_id):
            return self.nodes.get(node_id).add_device(device)
        else:
            return False

    def end_device(self, node_id: str, device_type: str):
        if self.node_exists(node_id):
            self.nodes.get(node_id).remove_device(device_type)

    def end_node(self, node_id: str):
        if self.node_exists(node_id):
            node = self.nodes.pop(node_id)
            node.remove_node()

    def command(self, node_id, device_type, command_id, args, source):
        cmd = Command(command_id, args, source)
        if self.node_exists(node_id):
            node = self.nodes.get(node_id)
            if node.device_type_exists(device_type):
                node.devices.get(device_type).post_command(cmd)

    def register_task(self, config):
        self.taskManager.create_task(config)

    def remove_task(self, task_id):
        self.taskManager.remove_task(task_id)

    def ping(self) -> dict:
        result = {}
        for node_key, node in self.nodes.items():
            result[node_key] = {}
            for device_key, device in node.devices.items():
                result[node_key][device.device_id] = device.ping()  # TODO make it asynchronous

        return result
