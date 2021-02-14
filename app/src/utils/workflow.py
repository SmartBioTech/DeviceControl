from threading import Thread, Event
from typing import List, Callable
import jpype


class Job:
    def __init__(self, task: Callable, args=None):
        if args is None:
            args = []

        self.task: Callable = task
        self.success = False
        self.cause = None
        self.data = None
        self.is_done = Event()
        self.args: [] = args


class Scheduler(Thread):
    def __init__(self):
        super(Scheduler, self).__init__()
        self.name = "scheduler thread"
        self.jobs: List[(Job, [])] = []
        self.is_active = True
        self.has_jobs = Event()

    def schedule_job(self, job: Job):
        self.jobs.append(job)
        self.has_jobs.set()

    @staticmethod
    def execute(job: Job):
        if jpype.isJVMStarted() and not jpype.isThreadAttachedToJVM():
            jpype.attachThreadToJVM()
        try:
            job.data = job.task(*job.args)
            job.success = True
        except Exception as exc:
            job.cause = repr(exc)
            job.success = False
        job.is_done.set()

    def run(self):
        while self.is_active:
            self.has_jobs.wait(timeout=5)
            while self.jobs:
                self.execute(self.jobs.pop(0))
            self.has_jobs.clear()


class WorkflowProvider:
    def __init__(self):
        self.scheduler = Scheduler()
        self.scheduler.start()

