import json
import os
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

    def __init__(self, connection: Dict[str, Any]) -> None:
        """
        Initializes the GoogleCloudStorageConnection with provided connection details.

        Args:
            connection (Dict[str, Any]): Dictionary containing connection settings 
                                         including project ID, bucket name, folder path, 
                                         and credentials path.
        """
        super().__init__()
        self.port = connection['port']
        self.folder = connection['folder_path']

        
    def connect(self) -> None:
        """
        Establishes a connection to the local filesystem.

        """
        return True


    def export(self, data: Any, filename: str):
        """
        Exports the current batch of data to a JSON file, appending a timestamp to the filename.
        
        The batch is saved in the directory specified by `self.batch_path`, and the filename
        is derived from `self.filename_stem` with the current UTC timestamp appended.
        """
        with open(filename, 'w') as f:
            json.dump(data, f, indent=4)


    def clean_old_exports(self, cutoff_time: datetime, filename_prefix: str) -> None:
        """
        Removes batch files older than the specified `clean_after` interval.
        
        This method iterates over files in the batch directory, checks each file’s timestamp,
        and deletes files that are older than the cutoff time passed in config.
        """
        deleted_files = []
        # Iterate through files in the folder
        for filename in os.listdir(self.folder):
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
            timestamp_str = filename.split('_')[-1].replace('.json', '')
            return datetime.strptime(timestamp_str, self.datetime_format_string).astimezone(pytz.utc)
        except ValueError:
            print(f"Could not parse timestamp from filename: {filename}")
            return None
        

    def __delete_file(self, filename: str) -> None:
        """Deletes the specified file and logs the deletion."""
        file_path = os.path.join(self.folder, filename)
        os.remove(file_path)
        print(f"Deleted old export file: {file_path}")