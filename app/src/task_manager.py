from typing import Dict

from app.src.utils.abstract_task import BaseTask
from app.src.utils.errors import IdError
from ..workspace.tasks import classes


class TaskManager:
    def __init__(self):
        self.tasks: Dict[str, BaseTask] = {}

    def create_task(self, config: dict):
        task_id = config.get('task_id')
        task_class = config.get('task_class')
        task_type = config.get('task_type')
        if task_id not in self.tasks:
            task = self.load_class(task_class, task_type)(config)
            self.tasks[task_id] = task
            return task
        else:
            raise IdError("Task with requested ID {} already exists".format(task_id))

    def remove_task(self, task_id):
        task = self.tasks.pop(task_id)
        task.end()

    def get_task(self, task_id):
        task = self.tasks.get(task_id)
        if task is None:
            raise IdError("Task with given ID: {} was not found".format(task_id))
        return task

    def end(self):
        for key in list(self.tasks.keys()):
            self.remove_task(key)

    def ping(self) -> Dict[str, bool]:
        result = {}
        for key, task in self.tasks.items():
            result[key] = task.is_active

        return result

    @staticmethod
    def load_class(task_class: str, task_type: str) -> BaseTask.__class__:
        return classes[task_class][task_type]
