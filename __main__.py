import sys


from core.flow.workflow import Scheduler, WorkflowProvider
from core.log import Logger

from core.connection import classes
from custom.devices.PSI.java.utils.jvm_controller import Controller

logger = Logger()


workflowProvider = WorkflowProvider()
controller = Controller()

default = "flask_client"

conModule = None
conModuleStartArgs = None

if len(sys.argv) > 1:
    conModule, conModuleStartArgs = classes.get(sys.argv[1])

if conModule is None:
    conModule, conModuleStartArgs = classes.get(default)

conModule().start(*conModuleStartArgs)


