from threading import Thread
from time import sleep

import smtplib, ssl

from core.data.command import Command
from core.device.manager import DeviceManager
from core.task.abstract import BaseTask

MESSAGE = """\
Subject: {}

This is automatic message sent from DeviceControl.

The device {} measured low amount of medium remaining.

Current value is {}, which is {} of max capacity.
"""


class MeasureWeightMedium(BaseTask):
    def __init__(self, config):
        self.__dict__.update(config)

        required = ['sleep_period', 'device_id', 'task_id', 'max_weight', 'warning_threshold']
        self.validate_attributes(required, type(self).__name__)

        self.max_weight = float(self.max_weight)
        self.sleep_period = int(self.sleep_period)
        self.warning_threshold = float(self.warning_threshold)

        self.device = DeviceManager().get_device(self.device_id)
        super(MeasureWeightMedium, self).__init__()

    def start(self):
        t = Thread(target=self._run)
        t.start()

    def _run(self):
        while self.is_active:
            command = Command(self.device_id, "1", [], self.task_id, is_awaited=True)
            self.device.post_command(command)
            command.await_cmd()

            # TODO: outliers?

            if command.is_valid:
                weight = command.response['weight']
                remaining = weight/self.max_weight
                if round(weight, 3) == 0:
                    self.send_mail(remaining, weight, critical=True)
                elif remaining < self.warning_threshold:
                    self.send_mail(remaining, weight, critical=False)

            # command.save_data_to_db()  # store?
            sleep(self.sleep_period)

    def end(self):
        self.is_active = False

    def send_mail(self, remaining, weight, critical=False):
        port = 465  # For SSL
        smtp_server = "smtp.gmail.com"
        sender_email = "my@gmail.com"  # Enter your address

        receiver_email = "your@gmail.com"  # Enter receiver address, should be loaded from a config
        password = "password"  # should be loaded from a config

        subject = "Medium critically low" if critical else "Medium is running low"
        message = MESSAGE.format(subject, self.device_id, weight, remaining)

        context = ssl.create_default_context()
        with smtplib.SMTP_SSL(smtp_server, port, context=context) as server:
            server.login(sender_email, password)
            server.sendmail(sender_email, receiver_email, message)
