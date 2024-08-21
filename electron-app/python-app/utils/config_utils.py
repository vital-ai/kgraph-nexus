import os

import yaml
from os.path import exists

# TODO
# This used for development, to be removed


class ConfigUtils:

    @staticmethod
    def load_config():
        current_working_directory = os.getcwd()
        print(f"Current working directory: {current_working_directory}")

        current_file_path = os.path.abspath(__file__)
        print(f"current file path: {current_file_path}")

        parent_directory = os.path.dirname(os.path.dirname(current_file_path))

        config_file_path = os.path.join(parent_directory, 'app_config.yaml')

        print(f"pyinstaller config file path: {config_file_path}")

        if exists(config_file_path):
            path = config_file_path
        elif exists("../app_config.yaml"):
            path = "../app_config.yaml"
        else:
            path = "app_config.yaml"
        with open(path, "r") as config_stream:
            try:
                return yaml.safe_load(config_stream)
            except yaml.YAMLError as exc:
                pass

