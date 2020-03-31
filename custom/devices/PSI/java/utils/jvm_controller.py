from threading import Event

import jpype
# Enable Java imports
import jpype.imports

from core.utils.singleton import singleton


@singleton
class Controller:

    def __init__(self):
        self.started = False
        self.finished = False
        self.finished_flag = Event()

    def start_jvm(self):
        self.started = True

        jpype.startJVM(jvmpath=jpype.getDefaultJVMPath(), convertStrings=False,
                       classpath="custom/devices/PSI/java/lib/jar/bioreactor-commander-0.8.7.jar")

        self.finished = True
        self.finished_flag.set()

    def shutdown_jvm(self):
        self.started = False

        jpype.shutdownJVM()

    def is_jvm_started(self):
        return jpype.isJVMStarted() or self.started
