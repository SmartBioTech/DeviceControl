import logging


class Logger:
    def __init__(self):
        logging.basicConfig(level=logging.DEBUG,
                            format='%(asctime)s %(levelname)s: %(message)s')

    @staticmethod
    def error(exc: Exception):
        logging.error(exc, exc_info=True)


def log_initialise(init_type):
    def wrapper(func):
        def wrapped_f(self, config):
            result = func(self, config)
            from ... import app_manager
            if result.success:
                app_manager.dataManager.store_log(init_type, config)
            return result
        return wrapped_f
    return wrapper


def log_terminate(func):
    def wrapper(self, id):
        result = func(self, id)
        from ... import app_manager
        if result.success:
            app_manager.dataManager.remove_log(id)
        return result
    return wrapper


def log_terminate_all(func):
    def wrapper(self):
        result = func(self)
        from ... import app_manager
        app_manager.dataManager.remove_all_logs()
        return result
    return wrapper
