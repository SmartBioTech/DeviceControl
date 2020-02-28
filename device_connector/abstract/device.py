from abc import abstractmethod

from utils.AbstractClass import abstractattribute, Interface


class Device(metaclass=Interface):

    @abstractattribute
    def id(self):
        pass

    @abstractattribute
    def address(self):
        pass

    @abstractattribute
    def interpreter(self) -> dict:
        pass

    def __str__(self):
        return "{} @ {}".format(self.id, self.address)

    def __repr__(self):
        return "Device({}, {})".format(self.id, self.address)

    @abstractmethod
    def disconnect(self) -> None:
        pass

    @abstractmethod
    def test_connection(self) -> bool:
        pass

    def get_command_reference(self, cmd_id):
        command_reference = self.interpreter.get(cmd_id)
        if command_reference is None:
            raise AttributeError("Requested command ID is not defined in the device_module's Interpreter")
        return command_reference

    def get_capabilities(self):
        result = {}
        for key, func in self.interpreter.items():
            arguments = list(func.__code__.co_varnames)
            arguments.remove("self")
            result[key] = func.__name__, arguments
        return result
