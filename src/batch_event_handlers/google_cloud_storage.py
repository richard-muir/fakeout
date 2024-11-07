import json
import os
from typing import Any, Dict
from datetime import datetime, timedelta

from google.cloud import storage
from google.oauth2 import service_account
from google.auth.exceptions import DefaultCredentialsError

from .base import BaseBatchConnection
from config import Config



class GoogleCloudStorageConnection(BaseBatchConnection):
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

    def __init__(self, config: Config) -> None:
        """
        Initializes the GoogleCloudStorageConnection with provided connection details.

        Args:
            connection (Dict[str, Any]): Dictionary containing connection settings 
                                         including project ID, bucket name, folder path, 
                                         and credentials path.
        """
        super().__init__()
        self.name = config.name
        self.project_id = config.connection['project_id']
        self.bucket_name = config.connection['bucket_name']
        self.folder_path = config.connection['folder_path']
        self.credentials_path = config.connection['credentials_path']
        self.client = None  # Will hold the GCS client instance

        
    def connect(self) -> None:
        """
        Establishes a connection to Google Cloud Storage.

        Initializes the GCS client using the service account credentials provided in 
        `credentials_path`. This method must be called before attempting to upload data.
        """
        creds_path = os.path.join("_creds", self.credentials_path)
        self.creds = service_account.Credentials.from_service_account_file(creds_path)
        self.client = storage.Client(credentials=self.creds)


    def export(self, data: Any, filename: str):
        """
        Uploads data to a specified path within the GCS bucket.

        Args:
            data (Any): The data to be uploaded, either as a string or bytes. If 
                        provided as a dictionary, it will be converted to JSON format.
            destination (str): The path within the bucket where the data will be stored.
        
        Raises:
            ValueError: If the client is not connected (i.e., `connect` has not been called).
        """
        if not self.client:
            raise ValueError("Client not connected. Call 'connect' first.")

        # Retrieve the bucket object
        bucket = self.client.bucket(self.bucket_name)
        blob = bucket.blob(f"{self.folder_path}/{filename}")

        data = json.dumps(data)

        print(type(data))
        blob.upload_from_string(data)
        print(f"Data successfully uploaded to {self.bucket_name}/{self.folder_path}.")



    def clean_old_exports(self, cutoff_time: datetime, filename_prefix: str) -> None:
        """
        Cleans up old uploads from the Google Cloud Storage bucket based on the specified cutoff time.

        Args:
            cutoff_time (datetime): The time threshold for removing old uploads.
        """
        if not self.client:
            raise ValueError("Client not connected. Call 'connect' first.")

        bucket = self.client.bucket(self.bucket_name)
        blobs = bucket.list_blobs(prefix=f"{self.folder_path}/{filename_prefix}")  # Filter by folder and prefix


        deleted_files = []
        for blob in blobs:
            # Check if the blob's creation time is older than the cutoff time
            if blob.time_created < cutoff_time:
                blob.delete()  # Delete the blob
                deleted_files.append(blob.name)

        print(f"Deleted {len(deleted_files)} old upload(s) from GCS.")