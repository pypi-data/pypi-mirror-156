from configparser import ConfigParser
import os


# load config file
def get_config(section):
    config = ConfigParser()
    config.read(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))) + "\\config.ini")
    if section=='storage':
        config[section]['upload_path'] = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),"upload")
        config[section]['local_path '] = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    return config[section]
