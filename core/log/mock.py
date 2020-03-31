from core.utils.singleton import singleton


@singleton
class MockLogger:

    @staticmethod
    def error(exc: Exception):
        print(exc)

    @staticmethod
    def info(msg: str):
        print(msg)