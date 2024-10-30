import json
import os
import code


class Config:
    def __init__(self, config_file='config.json'):
        self.config_file = os.path.join(os.path.dirname(__file__), '..', config_file)
        self.streaming_interval = None
        self.batch_file_name = None
        self.batch_interval = None
        self.data_records = []
        self.load_config()

    def load_config(self):
        try:
            with open(self.config_file, 'r') as file:
                config = json.load(file)
                self.streaming_interval = config.get('streaming', {}).get('interval')
                self.batch_file_name = config.get('batch', {}).get('file_name')
                self.batch_interval = config.get('batch', {}).get('interval')
                self.data_records = config.get('data_records', [])

        except FileNotFoundError:
            print(f"Configuration file '{self.config_file}' not found.")
            # Handle error or set defaults
        except json.JSONDecodeError:
            print(f"Error decoding JSON from '{self.config_file}'.")
            # Handle error or set defaults
