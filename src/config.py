import os
import json
from typing import List, Optional, Dict, Union


class Config:
    """
    A class to handle configuration settings for Fakeout.

    Attributes:
        streaming_interval (Optional[int]): The interval for streaming data in seconds.
        batch_file_name (Optional[str]): The base name of the batch file for export.
        batch_interval (Optional[int]): The interval for batch export in seconds.
        data_description (List[Dict[str, Union[str, int, float]]]): A list of data record configurations.
        datetime_format_string (str): Format string for date and time in batch files.
        streaming_service (Optional[str]): Name of the streaming service (e.g., 'pubsub').
        streaming_creds (Optional[Dict[str, str]]): Connection credentials for streaming services.
    """

    def __init__(self, config_file: str = 'config.json') -> None:
        """
        Initializes the Config instance and loads the configuration from a JSON file.
        Searches for the config file one level up from the src folder.

        Args:
            config_file (str): The path to the JSON configuration file (default is 'config.json').
        """
        self.config_file = os.path.join(os.path.dirname(__file__), '..', config_file)
        self.streaming_interval = None
        self.batch_file_name = None
        self.batch_interval = None
        self.data_description = []
        self.load_config()
        self.datetime_format_string = '%Y%m%d %H%M%S %f %z'

    def load_config(self) -> None:
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

            config_errors = self._validate_config()
            if config_errors:
                raise Exception(config_errors)
            else:
                self.streaming_interval = config.get('streaming', {}).get('interval')
                self.batch_file_name = config.get('batch', {}).get('file_name')
                self.batch_interval = config.get('batch', {}).get('interval')
                self.batch_cleanup_after = config.get('batch', {}).get('cleanup_after')
                self.data_description = config.get('data_description', [])
                self.streaming_service = config.get('streaming', {}).get('service')
                self.streaming_creds = config.get('streaming', {}).get('connection_creds')

    def _validate_config(self) -> List[str]:
        """Validate the configuration, or at least, it will do."""
        return []