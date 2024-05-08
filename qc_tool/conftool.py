# -*- coding: UTF-8 -*-
import os
import json
from log import log, loggingLevel

logger = log()
logger.setLogLevel(loggingLevel.info)

class ConfTool:
    def __init__(self, conf_path):
        self.conf = self.load_conf(conf_path)

    def get_conf(self):
        return self.conf

    @staticmethod
    def load_conf(conf_path):
        confInfo = {}
        # 检查配置文件是否存在
        ConfTool.exists_check(conf_path)
        # 加载配置文件数据
        f = open(conf_path, mode='r')
        confInfo = json.load(f)
        f.close()
        return confInfo

    @staticmethod
    def exists_check(path):
        if os.path.exists(path):
            logger.info("本次测试使用配置文件：{}".format(path))
        else:
            raise RuntimeError(f"测试配置文件不存在{path}")