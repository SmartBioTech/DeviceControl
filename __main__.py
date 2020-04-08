import sys

from core.data.manager import DataManager
from core.device.manager import DeviceManager
from core.flow.workflow import Scheduler
from core.log import Logger
from core.manager import AppManager
from core.task.manager import TaskManager
from core.connection import classes

logger = Logger()

deviceManager = DeviceManager()
taskManager = TaskManager()
dataManager = DataManager()
scheduler = Scheduler
appManager = AppManager(taskManager, deviceManager, dataManager)

default = "flask_server"

conModule = None

if len(sys.argv) > 1:
    conModule = classes.get(sys.argv[1])

if conModule is None:
    conModule = classes.get(default)

scheduler.start()
conModule(appManager).start()


