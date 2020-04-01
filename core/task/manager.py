from typing import Dict

from core.task.abstract import BaseTask
from core.utils.errors import IdError
from core.utils.singleton import singleton


@singleton
class TaskManager:

    def __init__(self):
        self.tasks: Dict[str, BaseTask] = {}

    def create_task(self, config: dict):
        task_id = config.get("task_id")
        task_class = config.get("task_class")
        assert task_id is not None
        assert task_class is not None
        if task_id not in self.tasks:
            task = self.load_class(task_class)(config)
            self.tasks[task_id] = task
            return task
        else:
            raise IdError("Task with requested ID already exists")

    @staticmethod
    def load_class(task_class: str) -> BaseTask.__class__:
        from custom.tasks import classes
        return classes.get(task_class)

    def remove_task(self, task_id):
        if task_id in self.tasks:
            task = self.tasks.pop(task_id)
            task.end()
        else:
            raise IdError("Task with requested ID doesn't exist")

    def get_task(self, task_id):
        task = self.tasks.get(task_id)
        if task is None:
            raise IdError("Task with given ID: %s was not found" % task_id)
        return task

    def end(self):
        for key in list(self.tasks.keys()):
            self.remove_task(key)

    def ping(self) -> Dict[str, bool]:
        result = {}
        for key, task in self.tasks.items():
            result[key] = task.is_active

        return result
