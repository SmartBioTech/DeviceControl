import logging

from utils.singleton import singleton


@singleton
class Logger:
    def __init__(self):
        logging.basicConfig(level=logging.DEBUG,
                            filename="../device_control.log",
                            format='%(asctime)s %(levelname)s:%(message)s')

    @staticmethod
    def error(exc: Exception):
        logging.error(exc, exc_info=True)

    @staticmethod
    def info(msg: str):
        logging.info("  " + msg)