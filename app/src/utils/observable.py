from abc import abstractmethod


class Observable:

    def __init__(self):
        self._observers: [Observer] = []
        self._value = None

    @property
    def value(self):
        return self._value

    @value.setter
    def value(self, new):
        self._value = new
        self._notify()

    def _notify(self):
        for observer in self._observers:
            observer.update(self)

    def observe(self, observer):
        self._observers.append(observer)

    def remove_observer(self, observer):
        self._observers.remove(observer)


class Observer:

    @abstractmethod
    def update(self, my_observable: Observable):
        pass
