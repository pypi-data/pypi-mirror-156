import json
import os
import sys


class __Config:
    def __init__(self):
        self.api_url = "https://api.instabuy.com.br"
        self.items_batch_count = 1000
        self.program_path: str = os.path.dirname(os.path.abspath(sys.argv[0]))
        self.ib_integration_temp_files = os.path.join(self.program_path, "tmp")
        self.version_file_name: str = "version.txt"
        self.DEBUG = False

    def get_local_version(self):
        local_vpath = os.path.join(self.program_path, self.version_file_name)

        if not os.path.exists(local_vpath):
            return None

        local_version = ""
        try:
            with open(local_vpath, "r", encoding="utf-8") as local_vfile:
                local_version = local_vfile.read()
        except Exception as exception:
            print(exception)

        return local_version

    def load_local_config(self, local_file_name="config.json"):
        with open(os.path.join(self.program_path, local_file_name), "r") as local_file:
            local_config = json.load(local_file)

            for key in local_config:
                self.__setattr__(key, local_config[key])

    def __nested_dict_keys(self, dict_to_nest: dict) -> list:
        nested_dict_keys = []
        for key, value in dict_to_nest.items():
            if isinstance(value, dict):
                nested_dict_keys.append(key)
                nested_dict_keys.extend(self.__nested_dict_keys(value))
            else:
                nested_dict_keys.append(key)
        return nested_dict_keys

    def verify_local_config(
        self,
        local_file_name="config.json",
        config_template_file_name="config_template.json",
    ):
        local_config_path = os.path.join(self.program_path, local_file_name)
        config_template_path = os.path.join(
            self.program_path, config_template_file_name
        )

        with open(config_template_path, "r") as config_template_file:
            config_template = json.load(config_template_file)

        with open(local_config_path, "r") as local_config_file:
            local_config = json.load(local_config_file)

        config_keys = self.__nested_dict_keys(config_template)
        local_config_keys = self.__nested_dict_keys(local_config)
        if set(config_keys) != set(local_config_keys):
            print("Config file is invalid")
            return False

        return True


config = __Config()
