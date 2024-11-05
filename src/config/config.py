import os
import json
from typing import List, Optional, Dict, Union

from pydantic import ValidationError

from schema_validator import ConfigValidator


class StreamingConfig:
    """
    Represents the configuration settings for a single streaming service in FakeOut.

    Attributes:
        name (str): The unique name of the streaming service configuration.
        interval (int): The interval in seconds between each data streaming event.
        size (int): The number of records to generate per streaming interval.
        randomise (bool): Indicates whether the data generated should be randomized.
        connection (Dict[str, Union[str, int]]): The connection details for the streaming service.
            Expected keys may include:
                - 'service' (str): The name of the streaming service (e.g., 'pubsub').
                - 'project_id' (str): The Google Cloud project ID if using Google Pub/Sub.
                - 'topic_id' (str): The Pub/Sub topic ID to which data is streamed.
                - 'credentials_path' (str): Path to the service account JSON file for authentication.
        data_description (List[Dict[str, Union[str, List]]]): A list of dictionaries defining
            the structure of each data record. Each dictionary includes:
                - 'name' (str): The name of the data field.
                - 'data_type' (str): The type of data (e.g., 'category', 'numeric').
                - 'allowable_values' (List): A list of possible values or range for the field.
    """

    def __init__(
            self, 
            name: str, 
            interval: int, 
            size: int, 
            randomise: bool, 
            connection: Dict,
            data_description: List
            ):
        self.name = name
        self.interval = interval
        self.size = size
        self.randomise = randomise
        self.connection = connection
        self.data_description = data_description
        self.datetime_format_string = '%Y%m%d %H%M%S %f %z'

class BatchConfig:
    """
    Represents the configuration settings for a single batch processing service in FakeOut.

    Attributes:
        name (str): The unique name of the batch service configuration.
        interval (int): The interval in seconds between each batch file export.
        size (int): The number of records to include in each batch export.
        randomise (bool): Indicates whether the data in each batch should be randomized.
        filetype (str): The file format for batch export (e.g., 'csv', 'json').
        cleanup_after (int): The time in minutes after which the batch file is deleted.
        connection (Dict[str, Union[str, int]]): The connection details for the batch export service.
            Expected keys may include:
                - 'service' (str): The type of storage service (e.g., 'google_cloud_storage', 'local').
                - 'project_id' (str): The Google Cloud project ID if using Google Cloud Storage.
                - 'bucket_name' (str): The bucket name for storing files if using Google Cloud Storage.
                - 'folder_path' (str): The folder path within the bucket for file storage.
                - 'port' (str): The port number for a local storage service, if applicable.
                - 'credentials_path' (str): Path to the service account JSON file for authentication.
        data_description (List[Dict[str, Union[str, List]]]): A list of dictionaries defining
            the structure of each data record. Each dictionary includes:
                - 'name' (str): The name of the data field.
                - 'data_type' (str): The type of data (e.g., 'category', 'numeric').
                - 'allowable_values' (List): A list of possible values or range for the field.
    """

    def __init__(
            self, 
            name: str, 
            interval: int, 
            size: int, 
            randomise: bool, 
            filetype: str, 
            cleanup_after: int, 
            connection: Dict,
            data_description: List):
        self.name = name
        self.interval = interval
        self.size = size
        self.randomise = randomise
        self.filetype = filetype
        self.cleanup_after = cleanup_after
        self.connection = connection
        self.data_description = data_description
        self.datetime_format_string = '%Y%m%d %H%M%S %f %z'


class Config:
    """
    Main configuration class for FakeOut, handling multiple streaming and batch configurations.
    """

    def __init__(self, config_file: str = 'config.json') -> None:
        """
        Initializes the Config instance and loads the configuration from a JSON file.
        
        Args:
            config_file (str): The path to the JSON configuration file.
        """
        self.config_file = os.path.join(os.path.dirname(__file__), '..', '..', config_file)
        self.streaming_configs: List[StreamingConfig] = []
        self.batch_configs: List[BatchConfig] = []
        self.load_config()

    def load_config(self) -> None:
        """
        Loads configuration settings from the JSON file and initializes multiple StreamingConfig and BatchConfig objects.

        Raises:
            FileNotFoundError: If the configuration file is not found.
            json.JSONDecodeError: If there is an error decoding the JSON file.
        """
        with open(self.config_file, 'r') as file:
            config = json.load(file)
            try:
            # Validate the data
                _ = ConfigValidator(**config)
            except ValidationError as e:
                print("Validation error:", e)

        # Load each streaming configuration
        for stream in config.get("streaming", []):
            streaming_config = StreamingConfig(
                name=stream["name"],
                interval=stream["interval"],
                size=stream.get("size", 1),  # Default to 1 if size isn't specified
                randomise=stream.get("randomise", False),
                connection=stream["connection"],
                data_description=stream["data_description"]
            )
            self.streaming_configs.append(streaming_config)

        # Load each batch configuration
        for batch in config.get("batch", []):
            batch_config = BatchConfig(
                name=batch["name"],
                interval=batch["interval"],
                size=batch.get("size", 1),  # Default to 1 if size isn't specified
                randomise=batch.get("randomise", False),
                filetype=batch["filetype"],
                cleanup_after=batch.get("cleanup_after", 0),
                connection=batch["connection"],
                data_description=batch["data_description"]
            )
            self.batch_configs.append(batch_config)


