import json
import os
import sys
import inspect
from typing import Any, Dict, Optional
from datetime import datetime, timedelta
import pytz

from google.cloud import storage
from google.oauth2 import service_account
from google.auth.exceptions import DefaultCredentialsError

from .base import BaseBatchConnection



class LocalStorageConnection(BaseBatchConnection):
    """
    A Google Cloud Storage connection for managing batch uploads to a specified GCS bucket.

    This class provides methods to connect to a Google Cloud Storage (GCS) bucket 
    and upload data to a defined path. It extends `BaseBatchConnection`, following 
    its structure for connection and data upload.

    Attributes:
        project_id (str): Google Cloud project ID associated with the GCS bucket.
        bucket_name (str): Name of the GCS bucket where data will be uploaded.
        folder_path (str): Folder path within the GCS bucket where data will be stored.
        credentials_path (str): Path to the service account credentials JSON file.
        client (storage.Client): Instance of the GCS client for connecting and uploading.

    Methods:
        connect():
            Initializes the GCS client for connecting to the specified bucket.
        upload(data: Any, destination: str):
            Uploads data to the designated path within the GCS bucket.
    """
    ALL_POSSIBLE_ERRORS = (
            PermissionError,
            OSError,
            FileNotFoundError, 
            TypeError,
            Exception,
            ValueError, 
            AttributeError
            )

    def __init__(self, name, connection: Dict[str, Any]) -> None:
        """
        Initializes the GoogleCloudStorageConnection with provided connection details.

        Args:
            connection (Dict[str, Any]): Dictionary containing connection settings 
                                         including project ID, bucket name, folder path, 
                                         and credentials path.
        """
        super().__init__()
        self.name = name
        self.port = connection['port']
        self.folder_path = connection['folder_path']

        
    def connect(self) -> None:
        """
        Establishes a connection to the local filesystem.
        Creates the folder if necessary.

        """
        try:
            os.makedirs(self.folder_path, exist_ok=True)
            print(f"Connected successfully. Folder '{self.folder_path}' is ready.")
        except self.ALL_POSSIBLE_ERRORS as e:
            self._handle_errors(e)
            sys.exit(1)


    def export(self, data: Any, filename: str):
        """
        Exports the current batch of data to a JSON file, appending a timestamp to the filename.
        
        The batch is saved in the directory specified by `self.batch_path`, and the filename
        is derived from `self.filename_stem` with the current UTC timestamp appended.
        """
        output_path = os.path.join(self.folder_path, filename)
        try:
            with open(output_path, 'w') as f:
                json.dump(data, f, indent=4)
            print(f"Data successfully exported to {output_path}")
        except self.ALL_POSSIBLE_ERRORS as e:
            self._handle_errors(e)
            sys.exit(1)


    def clean_old_exports(self, cutoff_time: datetime, filename_prefix: str) -> None:
        """
        Removes batch files older than the specified `clean_after` interval.
        
        This method iterates over files in the batch directory, checks each file’s timestamp,
        and deletes files that are older than the cutoff time passed in config.
        """
        deleted_files = []
        # Iterate through files in the folder
        for filename in os.listdir(self.folder_path):
            if filename.startswith(filename_prefix):  # Check if it's an export file
                file_time = self.__parse_timestamp_from_filename(filename)
                
                # Check if the file is older than the cutoff time
                if file_time and file_time < cutoff_time:
                    self.__delete_file(filename)
                    deleted_files.append(filename)
        print(f"{len(deleted_files)} exported batch files deleted")


    def _clear_batch_data(self) -> None:
        """Resets the batch data to an empty list"""
        self.data = []


    def __parse_timestamp_from_filename(self, filename: str) -> Optional[datetime]:
        """Extracts and returns the datetime object from the filename."""
        try:
            if not isinstance(filename, str):
                raise TypeError(f"Filename must be a string. Received: {type(filename)}")

            # Attempt to split and extract the timestamp part
            timestamp_str = filename.split('_')[-1].replace('.json', '')
            
            # Parse the timestamp and convert it to UTC timezone
            return datetime.strptime(timestamp_str, self.datetime_format_string).astimezone(pytz.utc)
        
        except self.ALL_POSSIBLE_ERRORS as e:
            self._handle_errors(e, additional_context=f"Filename: {filename}")
            sys.exit(1)
        

    def __delete_file(self, filename: str) -> None:
        """Deletes the specified file and logs the deletion."""
        try:
            file_path = os.path.join(self.folder, filename)
            os.remove(file_path)
            print(f"Deleted old export file: {file_path}")
        except self.ALL_POSSIBLE_ERRORS as e:
            self._handle_errors(e, additional_context=f"Filename: {filename}")
            sys.exit(1)
            


    def _handle_errors(self, exception: Exception, additional_context: str=''):
        """Handles connection and publishing related errors with descriptive messages."""

        # Get the name of the calling function to determine the context
        calling_function = inspect.stack()[1].function
        contexts = {
            'connect' : 'connecting',
            'export' : 'exporting',
            'clean_old_exports' : 'cleaning old exports',
            '__parse_timestamp_from_filename' : 'parsing timestamps from filename',
            '__delete_file' : 'deleting files'
        }
        context = contexts[calling_function]

        # Want to highlight additional context if it's passed
        if additional_context:
            additional_context = f"\nAdditional context :{additional_context}"

        if isinstance(exception, PermissionError):
            error_message = (
                f"Error during {context} for batch export service '{self.name}': Insufficient permissions to create, write to, or access "
                f"'{self.folder_path}'. Please check folder permissions.{additional_context}"
            )
        elif isinstance(exception, OSError):
            error_message = (
                f"Error during {context} for batch export service '{self.name}': Unable to create or access the folder "
                f"'{self.folder_path}'. Details: {exception}{additional_context}"
            )
        elif isinstance(exception, FileNotFoundError):
            error_message = (
                f"Error during {context} for batch export '{self.name}': The directory '{self.folder_path}' does not exist.\n"
                "Please ensure the folder path is valid.{additional_context}"
            )
        elif isinstance(exception, TypeError):
            error_message = (
                f"Error during {context} for batch export '{self.name}': Failed to serialize data to JSON format.\n"
                f"Details: {exception}\n"
                "Ensure the data is JSON serializable.{additional_context}"
            )
        else:
            error_message = (
                f"Unexpected error during {context} for batch export service {self.name}: An error occurred while accessing "
                f"'{self.folder_path}'. Details: {exception}{additional_context}"
            )

        print(error_message)


