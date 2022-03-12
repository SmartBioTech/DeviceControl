from abc import abstractmethod

from .AbstractClass import Interface, abstractattribute


class BaseTask(metaclass=Interface):
    """
    An interface which every implemented Task must implement.
    For additional information, see Wiki_.

    .. _Wiki: https://github.com/SmartBioTech/DeviceControl/wiki/New-task
    """

    def __init__(self, config):
        self.is_active = True
        self.config = config

    def __eq__(self, other):
        return self.config == other.config

    def validate_attributes(self, required, class_name):
        for att in required:
            if att not in self.__dict__.keys():
                raise AttributeError("Task {} must contain attribute {}".format(class_name, att))

    @abstractattribute
    def task_id(self):
        """
        ID of the task.
        """
        pass

    @abstractmethod
    def end(self):
        """
        Terminate the task.
        """
        pass

    @abstractmethod
    def start(self):
        """
        Start the task.
        """
        pass
