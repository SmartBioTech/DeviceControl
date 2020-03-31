from core.utils.singleton import singleton


@singleton
class MockLogger:

    @staticmethod
    def error(exc: Exception):
        pass

    @staticmethod
    def info(msg: str):
        pass