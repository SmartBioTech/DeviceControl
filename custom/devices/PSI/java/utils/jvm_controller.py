from threading import Lock
from time import sleep
from typing import Callable

import jpype
# Enable Java imports
import jpype.imports

from core.flow.workflow import Scheduler, Job
from core.utils.singleton import singleton


@singleton
class Controller:

    def __init__(self):
        self.lock = Lock()
        self.commander_connector = None
        self.plugins_loaded = False
        self.scheduler = Scheduler()
        self.scheduler.start()
        self.execute_command(self.start_jvm, [])

    def start_jvm(self):
        self.lock.acquire()
        if not self.is_jvm_started():
            jpype.addClassPath('custom/devices/PSI/java/lib/jar/bioreactor-commander-0.8.7.jar')
            jpype.startJVM(jvmpath=jpype.getDefaultJVMPath(), convertStrings=False,
                           classpath="custom/devices/PSI/java/lib/jar/bioreactor-commander-0.8.7.jar")

        self.lock.release()

    def load_plugins(self):
        if not self.plugins_loaded:
            server_plugin_manager = jpype.JClass("psi.bioreactor.server.plugin.ServerPluginManager")
            sleep(10)
            server_plugin_manager.getInstance().loadPlugins()
        self.plugins_loaded = True

    @staticmethod
    def shutdown_jvm():
        jpype.shutdownJVM()

    @staticmethod
    def is_jvm_started():
        return jpype.isJVMStarted()

    def execute_command(self, cmd: Callable, args: list):
        job = Job(task=cmd, args=args)
        self.scheduler.schedule_job(job)
        job.is_done.wait()
        if job.success:
            return job.data
        else:
            return job.cause
