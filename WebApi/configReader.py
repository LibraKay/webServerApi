import os
import sys

root_path = os.path.dirname(os.path.abspath(__file__))
os.environ['WORKSPACE'] = root_path
sys.path.append(root_path)
tool_root_path = os.path.join(root_path, "..")
tool_path = os.path.join(tool_root_path, "qc_tool")
sys.path.append(tool_path)

import os
from qc_tool.conftool import ConfTool



ROOT_PATH = os.path.dirname(os.path.abspath(__file__))
CONFIG_FOLDER = os.path.join(ROOT_PATH, "Config")
CONFIG_FILE = os.path.join(CONFIG_FOLDER, "conf.json")


# load configure data
conf_tool = ConfTool(CONFIG_FILE)
conf_data = conf_tool.get_conf()

# mongo data
mongo_data = conf_data["mongodb"]
mongo_ip = mongo_data["IP"]
mongo_port = mongo_data["port"]
mongo_username = mongo_data["username"]
mongo_password = mongo_data["password"]
# mongo_database = mongo_data["database"]
# mongo_collection = mongo_data["collection"]