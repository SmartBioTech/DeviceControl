import logging
import os


class Logger:
    def __init__(self):
        if not os.path.exists('log'):
            os.makedirs('log')
        logging.basicConfig(level=logging.DEBUG,
                            filename="log/device_control.log",
                            format='%(asctime)s %(levelname)s:%(message)s')

    @staticmethod
    def error(exc: Exception):
        logging.error(exc, exc_info=True)

    @staticmethod
    def info(msg: str):
        logging.info("  " + msg)
