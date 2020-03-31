from threading import Lock

import jpype
# Enable Java imports
import jpype.imports

from core.utils.singleton import singleton


@singleton
class Controller:

    def __init__(self):
        self.lock = Lock()

    def start_jvm(self):
        self.lock.acquire()
        if not self.is_jvm_started():
            jpype.addClassPath('custom/devices/PSI/java/lib/jar/bioreactor-commander-0.8.7.jar')
            jpype.startJVM(jvmpath=jpype.getDefaultJVMPath(), convertStrings=False,
                           classpath="custom/devices/PSI/java/lib/jar/bioreactor-commander-0.8.7.jar")

        self.lock.release()

    @staticmethod
    def shutdown_jvm():
        jpype.shutdownJVM()

    @staticmethod
    def is_jvm_started():
        return jpype.isJVMStarted()
