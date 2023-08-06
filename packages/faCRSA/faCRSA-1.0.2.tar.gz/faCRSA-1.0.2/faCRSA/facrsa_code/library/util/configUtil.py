import os
from pathlib import Path


# load config file
def get_config(section):
    local_path = Path(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))).as_posix()
    upload_path = Path(os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "static",'upload')).as_posix()
    config = {'upload_path': upload_path + "/", 'local_path': local_path + "/"}
    return config
