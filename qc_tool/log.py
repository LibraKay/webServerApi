import logging
from enum import IntEnum, unique

DEFAULT_LOG_LEVEL = logging.INFO


class loggingLevel(IntEnum):
    debug = logging.DEBUG
    info = logging.INFO
    warning = logging.WARNING
    error = logging.ERROR


class log:
    def __init__(self):
        logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(DEFAULT_LOG_LEVEL)

    def setLogLevel(self,level):
        self.logger.setLevel(level)
        self.logger.info("日志等级定义为 - {}".format(level))

    def debug(self, msg, *args, **kwargs):
        self.logger.debug(msg, *args, **kwargs)

    def info(self, msg, *args, **kwargs):
        self.logger.info(msg, *args, **kwargs)

    def warning(self, msg, *args, **kwargs):
        self.logger.warning(msg, *args, **kwargs)

    def error(self, msg, *args, **kwargs):
        self.logger.error(msg, *args, **kwargs)

