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


class TestDevice(Device):

    def __init__(self):
        super(TestDevice, self).__init__()
        self.id = 9
        self.address = "home"
        self.interpreter = {1: self.hello,
                            2: self.hi}

    def hello(self):
        print("Device {} says hello".format(self.id))

    def hi(self):
        pass

    def test_connection(self) -> bool:
        return True

    def disconnect(self) -> None:
        return
