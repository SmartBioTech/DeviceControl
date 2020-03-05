from builtins import staticmethod

import jpype

# Enable Java imports
import jpype.imports

# Pull in types
from jpype.types import *

from jpype import *


class JVMController:

    def __init__(self):
        pass

    @staticmethod
    def start_jvm():
        jpype.startJVM(jvmpath=jpype.getDefaultJVMPath(), convertStrings=False,
                       classpath="device_connector/PSI_java/lib/jar/bioreactor-commander-0.8.7.jar")

    @staticmethod
    def shutdown_jvm():
        jpype.shutdownJVM()

    @staticmethod
    def is_jvm_started():
        return jpype.isJVMStarted()
