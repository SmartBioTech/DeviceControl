from abc import abstractmethod

from ..utils.AbstractClass import Interface, abstractattribute


class BaseTask(metaclass=Interface):

    def __init__(self):
        self.is_active = True

    def validate_attributes(self, required, class_name):
        for att in required:
            if att not in self.__dict__.keys():
                raise AttributeError("Task {} must contain attribute {}".format(class_name, att))

    @abstractattribute
    def task_id(self):
        pass

    @abstractmethod
    def end(self):
        pass

    @abstractmethod
    def start(self):
        pass
