from typing import Dict

from task_module.abstract import BaseTask
from task_module.tasks import PBRMeasureAll, PBRGeneralPump
from utils.errors import IdError
from utils.singleton import singleton


@singleton
class TaskManager:

    def __init__(self):
        self._tasks = {}

        self.task_types = {
            "PBR_MEASURE_ALL": PBRMeasureAll,
            "PBR_GENERAL_PUMP": PBRGeneralPump
        }

    def create_task(self, config: dict):
        task_id = config.get("task_id")
        task_type = config.get("task_type")
        assert task_id is not None
        assert task_type is not None
        if task_id not in self._tasks:
            task = self.task_types.get(task_type)(config)
            self._tasks[task_id] = task
            return task
        else:
            raise IdError("Task with requested ID already exists")

    def remove_task(self, task_id):
        if task_id in self._tasks:
            task = self._tasks.pop(task_id)
            task.end()
        else:
            raise IdError("Task with requested ID doesn't exist")

    def get_task(self, task_id):
        return self._tasks.get(task_id)
