from core.db import DatabaseManager
from core.utils.singleton import singleton


@singleton
class MockDatabase:

    def update_log(self, cmd):
        pass
