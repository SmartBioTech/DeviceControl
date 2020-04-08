from core.utils.singleton import singleton


@singleton
class MockDatabase:

    @staticmethod
    def update_log(cmd):
        print(cmd)
