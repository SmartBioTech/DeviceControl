from typing import Dict

from app.core.task.abstract import BaseTask
from app.core.utils.errors import IdError
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

    @staticmethod
    def load_class(task_class: str, task_type: str) -> BaseTask.__class__:
        return classes.get(task_class, {}).get(task_type)

    def remove_task(self, task_id):
        if task_id in self.tasks:
            task = self.tasks.pop(task_id)
            task.end()
        else:
            raise IdError("Task with requested ID {} does not exist".format(task_id))

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
