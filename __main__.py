import sys

from core.device.manager import DeviceManager
from core.log import Logger
from core.manager import AppManager
from core.task.manager import TaskManager
from core.connection import classes

logger = Logger()

deviceManager = DeviceManager()
taskManager = TaskManager()
appManager = AppManager(taskManager, deviceManager)

default = "flask_server"

conModule = None

if len(sys.argv) > 1:
    conModule = classes.get(sys.argv[1])

if conModule is None:
    conModule = classes.get(default)

conModule(appManager).start()


