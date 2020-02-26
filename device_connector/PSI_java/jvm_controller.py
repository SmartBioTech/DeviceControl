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
    def startJVM():
        jpype.startJVM(jvmpath=jpype.getDefaultJVMPath(), convertStrings=False,
                       classpath="device_connector/PSI_java/lib/jar/bioreactor-commander-0.8.7.jar")

    @staticmethod
    def shutdownJVM():
        jpype.shutdownJVM()

    @staticmethod
    def isJVMStarted():
        return jpype.isJVMStarted()
