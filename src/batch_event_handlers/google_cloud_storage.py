import json
import inspect
import sys
import os
from typing import Any, Dict
from datetime import datetime, timedelta

from google.cloud import storage
from google.oauth2 import service_account
from google.auth.exceptions import DefaultCredentialsError, GoogleAuthError
from google.api_core.exceptions import (
    NotFound, 
    Forbidden, 
    GoogleAPIError, 
    ServiceUnavailable, 
    PermissionDenied
    )


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
    ALL_POSSIBLE_ERRORS = (
        FileNotFoundError, 
        ValueError,
        DefaultCredentialsError, 
        OSError, 
        GoogleAPIError,
        json.JSONDecodeError,
        TypeError,
        NotFound, 
        Forbidden,
        ConnectionError, 
        ServiceUnavailable,
        PermissionDenied,
        GoogleAuthError,
        Exception,
        )

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
        try:
            creds_path = os.path.join("_creds", self.credentials_path)
            self.creds = service_account.Credentials.from_service_account_file(creds_path)
            self.client = storage.Client(credentials=self.creds)
        except self.ALL_POSSIBLE_ERRORS as e:
            self._handle_errors(e)
            sys.exit(1)


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
        try:
            if not self.client:
                raise ValueError("Client not connected. Call 'connect' first.")

            # Retrieve the bucket object
            bucket = self.client.bucket(self.bucket_name)
            blob = bucket.blob(f"{self.folder_path}/{filename}")

            data = json.dumps(data)
            blob.upload_from_string(data)
            print(f"Data successfully uploaded to {self.bucket_name}/{self.folder_path}.")

        except self.ALL_POSSIBLE_ERRORS as e:
            self._handle_errors(e)
            sys.exit(1)



    def clean_old_exports(self, cutoff_time: datetime, filename_prefix: str) -> None:
        """
        Cleans up old uploads from the Google Cloud Storage bucket based on the specified cutoff time.

        Args:
            cutoff_time (datetime): The time threshold for removing old uploads.
        """
        try:
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

        except self.ALL_POSSIBLE_ERRORS as e:
            self._handle_errors(e, additional_context=f"Trying to delete: {blob.name}")
            sys.exit(1)

    def _handle_errors(self, exception: Exception, additional_context: str=''):
        """Handles connection and publishing related errors with descriptive messages."""

        # Get the name of the calling function to determine the context
        calling_function = inspect.stack()[1].function
        context = "connecting" if calling_function == "connect" else "publishing"

        # Want to highlight additional context if it's passed
        if additional_context:
            additional_context = f"\nAdditional context: {additional_context}"

        # Error handling for each specific error type
        if isinstance(exception, FileNotFoundError):
            error_message = (
                f"Error during {context} for batch service '{self.name}': "
                f"The specified file or directory could not be found. "
                f"Please ensure the path is correct and accessible."
                f"{additional_context}"
            )

        elif isinstance(exception, ValueError):
            error_message = (
                f"Error during {context} for batch service '{self.name}': "
                f"Invalid value encountered.\n"
                f"Please check input values and data types.{additional_context}"
            )

        elif isinstance(exception, DefaultCredentialsError):
            error_message = (
                f"Error during {context} for batch service '{self.name}': "
                f"Unable to locate default credentials.\n"
                f"Please set up authentication credentials for Google Cloud."
                f"{additional_context}"
            )

        elif isinstance(exception, OSError):
            error_message = (
                f"Error during {context} for batch service '{self.name}': "
                f"An OS-level error occurred.\n"
                f"Details: {exception}.{additional_context}"
            )

        elif isinstance(exception, GoogleAPIError):
            error_message = (
                f"Error during {context} for batch service '{self.name}': "
                f"A Google API error occurred.\n"
                f"Please check API usage and permissions.{additional_context}"
            )

        elif isinstance(exception, json.JSONDecodeError):
            error_message = (
                f"Error during {context} for batch service '{self.name}': "
                f"Failed to decode JSON data.\n"
                f"Ensure data is in valid JSON format.{additional_context}"
            )

        elif isinstance(exception, TypeError):
            error_message = (
                f"Error during {context} for batch service '{self.name}': "
                f"Data not valid for JSON serialization."
                f"Ensure data is in valid JSON format.{additional_context}"
            )

        elif isinstance(exception, NotFound):
            error_message = (
                f"Error during {context} for batch service '{self.name}': "
                f"The specified bucket {self.bucket_name} in project "
                f"{self.project_id} was not found.\n"
                f"Please verify the resource's existence and location."
                f"{additional_context}"
            )

        elif isinstance(exception, Forbidden):
            error_message = (
                f"Error during {context} for batch service '{self.name}': "
                f"Access to the bucket {self.bucket_name} in project "
                f"{self.project_id} is forbidden.\n"
                f"Please verify GCP permissions and access settings for the "
                f"service account in your credentials file.{additional_context}"
            )

        elif isinstance(exception, ConnectionError):
            error_message = (
                f"Error during {context} for batch service '{self.name}': "
                f"A connection error occurred.\n"
                f"Please check network connectivity and try again."
                f"{additional_context}"
            )

        elif isinstance(exception, ServiceUnavailable):
            error_message = (
                f"Error during {context} for batch service '{self.name}': "
                f"Google Cloud Storage service is unavailable.\n"
                f"This may be a temporary issue. Please try again later."
                f"{additional_context}"
            )

        elif isinstance(exception, PermissionDenied):
            error_message = (
                f"Error during {context} for batch service '{self.name}': "
                f"Permission denied. for bucket {self.bucket_name} in project "
                f"{self.project_id}\n Please verify that you have given the "
                f"required GCP permissions to the service account in your "
                f"credentials.{additional_context}"
            )

        elif isinstance(exception, GoogleAuthError):
            error_message = (
                f"Error during {context} for batch service '{self.name}': "
                f"Authentication with Google Cloud failed for bucket "
                f"{self.bucket_name} in project {self.project_id}"
                f"Please verify the credentials and account permissions.{additional_context}"
            )

        else:  # Catch-all for any other exceptions
            error_message = (
                f"Unexpected error during {context} for batch service '{self.name}': {exception}. "
                f"Please check the error details and retry.{additional_context}"
            )

        print(error_message)


