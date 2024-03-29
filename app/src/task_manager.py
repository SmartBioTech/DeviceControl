from typing import Dict

from app.src.utils.abstract_task import BaseTask
from app.src.utils.errors import IdError, ClassError
from ..workspace.tasks import classes


class TaskManager:
    """
    Manages tasks in the application.
    """
    def __init__(self):
        self.tasks: Dict[str, BaseTask] = {}

    def create_task(self, config: dict):
        """
        Creates a new task in the application.

        Extra parameters:

        - 'task_id': string - unique ID of the task,
        - 'task_class': string - Class of the task,
        - 'task_type': string - Type of the task,

        :param config: Configuration of the task with the specified extra parameters
        :return: the created task
        """
        task_id = config.get('task_id')
        task_class = config.get('task_class')
        task_type = config.get('task_type')
        if task_id not in self.tasks:
            try:
                task = self._load_class(task_class, task_type)(config)
            except KeyError:
                raise ClassError("Unknown task class/type: {}/{}".format(task_class, task_type))
            self.tasks[task_id] = task
            return task
        else:
            raise IdError("Task with requested ID {} already exists".format(task_id))

    def remove_task(self, task_id):
        """
        Terminates an existing task.

        :param task_id: ID of the task
        """
        task = self.tasks.pop(task_id)
        dev_id = task.device_id
        task.end()
        return dev_id

    def get_task(self, task_id):
        """
        Get an existing task reference.

        :param task_id: ID of the task
        :return: the requested task
        """
        task = self.tasks.get(task_id)
        if task is None:
            raise IdError("Task with given ID: {} was not found".format(task_id))
        return task

    def end(self):
        """
        Terminates all existing tasks.
        """
        for key in list(self.tasks.keys()):
            self.remove_task(key)

    def ping(self) -> Dict[str, bool]:
        """
        Tests connectivity with each existing task.

        :return: A dictionary {"task_id": true/false}
        """
        result = {}
        for key, task in self.tasks.items():
            result[key] = task.is_active

        return result

    @staticmethod
    def _load_class(task_class: str, task_type: str) -> BaseTask.__class__:
        return classes[task_class][task_type]
