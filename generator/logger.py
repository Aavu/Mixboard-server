import time
import logging
from celery.utils.log import get_task_logger
import inspect
import os
from .config.config import LOG_DIR_PATH

class Logger:
    __instance = {}

    def __init__(self, name, loglevel=logging.DEBUG):
        self.name = name
        self.loglevel = loglevel
        if name in Logger.__instance:
            raise Exception(f"Logger with name '{name}' already created")
        else:
            self.logger = None
            Logger.__instance[name] = self
            self.time = None
            self.create_log(name=name, loglevel=loglevel)

    @staticmethod
    def get_logger(name="mixboard"):
        if not name in Logger.__instance:
            Logger(name=name)
        return Logger.__instance[name]

    # def get_logger(self):
    #     return self.logger

    @staticmethod
    def get_self(name="mixboard"):
        if not name in Logger.__instance:
            Logger(name=name)
        return Logger.__instance[name]

    def get_time(self):
        return self.time

    @staticmethod
    def __get_call_info():
        stack = inspect.stack()

        # stack[1] gives previous function ('info' in our case)
        # stack[2] gives before previous function and so on

        fn = stack[3][1]
        ln = stack[3][2]
        func = stack[3][3]

        _file = os.path.split(fn)[1]
        return _file, ln

    def create_log(self, name="mixboard", loglevel=logging.DEBUG):
        self.time = time.strftime("%Y-%m-%d-%H-%M-%S")
        self.logger = get_task_logger(name)
        if not os.path.exists(LOG_DIR_PATH):
            os.mkdir(LOG_DIR_PATH)
        file_handler = logging.FileHandler(os.path.join(LOG_DIR_PATH, f"{self.time}.log"))
        # formatter = logging.Formatter("%(asctime)s | %(levelname)s | %(filename)s | %(funcName)s | %(message)s")
        formatter = logging.Formatter("%(asctime)s | %(levelname)s | %(message)s")
        file_handler.setFormatter(formatter)
        self.logger.handlers.clear()
        self.logger.addHandler(file_handler)
        self.logger.setLevel(loglevel)

    @staticmethod
    def __get_msg(msg):
        stack = Logger.__get_call_info()
        return f"{stack[0]} | Line: {stack[1]} | {msg}"

    def info(self, msg, *args, **kwargs):
        self.logger.info(Logger.__get_msg(msg), *args, **kwargs)

    def debug(self, msg, *args, **kwargs):
        self.logger.debug(Logger.__get_msg(msg), *args, **kwargs)

    def error(self, msg, *args, **kwargs):
        self.logger.error(Logger.__get_msg(msg), *args, **kwargs)

    def warning(self, msg, *args, **kwargs):
        self.logger.warning(Logger.__get_msg(msg), *args, **kwargs)

    def exception(self, msg, *args, **kwargs):
        self.logger.exception(Logger.__get_msg(msg), *args, **kwargs)


logger = Logger.get_logger()

# if __name__ == '__main__':
#     logger = Logger.get_logger()
#     logger1 = Logger.get_logger()
#     logger.debug("Debug message")
#     logger.info("info message")
#     logger1.error("error message")
#     logger1.warning("warning message")
