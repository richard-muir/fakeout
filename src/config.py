import json
import os
import code


class Config:
    """
    A class to handle the configuration settings for fakeout.

    Attributes:
        streaming_interval (int): The interval for streaming data in seconds.
        batch_file_name (str): The name of the batch file stem for export.
        batch_interval (int): The interval for batch export in seconds in seconds.
        data_records (list): A list of data record configurations.
    """

    def __init__(self, config_file='config.json'):
        """
        Initializes the Config instance and loads the configuration from a JSON file.
        Searches for the config file one level up from the src folder

        Args:
            config_file (str): The path to the JSON configuration file (default is 'config.json').
        """
        self.config_file = os.path.join(os.path.dirname(__file__), '..', config_file)
        self.streaming_interval = None
        self.batch_file_name = None
        self.batch_interval = None
        self.data_description = []
        self.load_config()

    def load_config(self):
        """
        Loads configuration settings from the JSON file.

        Parses the JSON structure to extract streaming intervals, batch file names,
        batch intervals, and data records.

        Raises:
            FileNotFoundError: If the configuration file is not found.
            json.JSONDecodeError: If there is an error decoding the JSON file.
        """
        with open(self.config_file, 'r') as file:
            config = json.load(file)
            self.streaming_interval = config.get('streaming', {}).get('interval')
            self.batch_file_name = config.get('batch', {}).get('file_name')
            self.batch_interval = config.get('batch', {}).get('interval')
            self.data_description = config.get('data_description', [])