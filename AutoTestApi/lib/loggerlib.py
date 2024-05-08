import os
import logging

root_path = os.path.dirname(os.path.abspath(__file__))
info_path = os.path.join(root_path, r'..\info')
log_file = os.path.join(info_path, 'main_log.txt')


class Logger:
    def __init__(self, path=None, clevel=logging.DEBUG, Flevel=logging.DEBUG):
        self.logger = logging.getLogger(path)
        self.logger.setLevel(logging.DEBUG)
        self.fmt = logging.Formatter(f'[%(asctime)s][%(levelname)s] %(message)s', '%Y-%m-%d %H:%M:%S')
        # 设置CMD日志
        self.Flevel = Flevel
        sh = logging.StreamHandler()
        sh.setFormatter(self.fmt)
        sh.setLevel(clevel)
        self.logger.addHandler(sh)

        if path:
            # 设置文件日志
            self.fh = logging.FileHandler(path)
            self.fh.setFormatter(self.fmt)
            self.fh.setLevel(Flevel)
            self.logger.addHandler(self.fh)

    def update_filehandler(self, new_path):
        self.logger.removeHandler(self.fh)
        self.fh = logging.FileHandler(new_path)
        self.fh.setFormatter(self.fmt)
        self.fh.setLevel(self.Flevel)
        self.logger.addHandler(self.fh)

    def debug(self, message):
        self.logger.debug(message)

    def info(self, message):
        self.logger.info(message)

    def warn(self, message):
        self.logger.warning(message)

    def error(self, message):
        self.logger.error(message)

    def critical(self, message):
        self.logger.critical(message)


logger = Logger(log_file, logging.INFO, logging.INFO)

