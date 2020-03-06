import jpype
# Enable Java imports
import jpype.imports


def start_jvm():
    jpype.startJVM(jvmpath=jpype.getDefaultJVMPath(), convertStrings=False,
                   classpath="device_connector/PSI_java/lib/jar/bioreactor-commander-0.8.7.jar")


def shutdown_jvm():
    jpype.shutdownJVM()


def is_jvm_started():
    return jpype.isJVMStarted()
