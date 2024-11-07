import json
import os
import sys
import inspect
from typing import Any, Dict

from google.cloud import pubsub_v1
from google.oauth2 import service_account
from google.auth.exceptions import DefaultCredentialsError, GoogleAuthError
from google.api_core.exceptions import NotFound, Forbidden, GoogleAPIError, ServiceUnavailable, PermissionDenied

from .base import BaseEventHandler
from config import Config



class PubSubEventHandler(BaseEventHandler):
    """
    Event handler for publishing messages to Google Cloud Pub/Sub.

    This class provides an implementation for the abstract BaseEventHandler class,
    allowing for seamless integration with Google Cloud Pub/Sub. It handles the
    initialization of connection credentials, establishes a connection with the
    Pub/Sub service, publishes messages, and ensures proper closure of resources.

    Attributes:
        project_id (str): Google Cloud project ID where the Pub/Sub topic resides.
        topic_id (str): ID of the Pub/Sub topic to publish messages to.
        credentials_path (str): Path to the JSON file with Google Cloud service account credentials.
        publisher (pubsub_v1.PublisherClient): Client instance for publishing messages to Pub/Sub.
        topic_path (str): Fully qualified path of the Pub/Sub topic.

    Methods:
        connect():
            Establishes a connection to the Pub/Sub service by initializing the Publisher client.
        publish(data):
            Publishes a message to the configured Pub/Sub topic.
    """
    ALL_POSSIBLE_ERRORS = (
            FileNotFoundError, 
            DefaultCredentialsError, 
            ServiceUnavailable,
            GoogleAuthError,
            NotFound, 
            Forbidden, 
            GoogleAPIError, 
            Exception,
            PermissionDenied
            )

    def __init__(self, config: Config) -> None:
        """
        Initializes the PubSubEventHandler with settings from the connection dictionary.
        
        Args:
            connection (Dict[str, Any]): Pub/Sub connection details.
        """
        super().__init__()
        self.name = config.name
        self.project_id = config.connection['project_id']
        self.topic_id = config.connection['topic_id']
        self.credentials_path = config.connection['credentials_path']
        self.publisher = None
        self.topic_path = None
              

    def connect(self) -> None:
        """Attempts to connect to Google Pub/Sub, handling common connection errors."""
        creds_path = os.path.join("_creds", self.credentials_path)

        try:
            # Load credentials from specified path
            if not os.path.exists(creds_path):
                raise FileNotFoundError(f"Credentials file not found at {creds_path}")

            # Initialize Pub/Sub client with credentials
            credentials = service_account.Credentials.from_service_account_file(creds_path)
            self.client = pubsub_v1.PublisherClient(credentials=credentials)

            # Need to create the string topic path before we can check if it exists
            self.topic_path = self.client.topic_path(self.project_id, self.topic_id)

        except self.ALL_POSSIBLE_ERRORS as e:
            self._handle_errors(e)
            sys.exit(1)


    def publish(self, data) -> None:
        """
        Publishes a message to the Pub/Sub topic.

        Args:
            data (dict): The data to be published, converted to JSON.
        """
        try:
            data = json.dumps(data).encode("utf-8")
            future = self.client.publish(self.topic_path, data)
            print(f"Published message ID: {future.result()}")

        except self.ALL_POSSIBLE_ERRORS as e:
            self._handle_errors(e)
            sys.exit(1)


    def _handle_errors(self, exception: Exception):
        """Handles connection and publishing related errors with descriptive messages."""

        # Get the name of the calling function to determine the context
        calling_function = inspect.stack()[1].function
        context = "connecting" if calling_function == "connect" else "publishing"


        if isinstance(exception, NotFound):
            error_message = (
                f"Error during {context} for streaming service: {self.name}: The topic '{self.topic_id}' does not exist "
                f"in project '{self.project_id}'. Please verify that the topic is created "
                "and the project ID is correct."
            )
        elif isinstance(exception, Forbidden):
            error_message = (
                f"Error during {context} for streaming service: {self.name}: Permission denied when accessing the topic. "
                f"Ensure the service account has the required Pub/Sub permissions for  for {self.topic_id} in {self.project_id}."
            )
        elif isinstance(exception, ServiceUnavailable):
            error_message = (
                f"Error during {context} for streaming service: {self.name}: Pub/Sub service is unavailable. Please try again later."
            )
        elif isinstance(exception, DefaultCredentialsError):
            error_message = (
                f"Error during {context} for streaming service: {self.name}: Invalid credentials  for {self.topic_id} in {self.project_id}. Please check your service account credentials."
            )
        elif isinstance(exception, GoogleAPIError):
            error_message = (
                f"Google API error during {context} for streaming service: {self.name}: {exception}. Please check your Google Cloud configurations and network access."
            )
        elif isinstance(exception, FileNotFoundError):
            error_message = (
                f"Error during {context} for streaming service: {self.name}: The credentials file was not found. "
                "Please check that you put your Google credentials in the _creds folder, and that the filename is correct."
            )
        elif isinstance(exception, GoogleAuthError):
            error_message = (
                f"Error during {context} for streaming service: {self.name}: Google authentication error.\n"
                f"Exiting the application. Please check your credentials and permissions  for {self.topic_id} in {self.project_id}."
            )
        elif isinstance(exception, PermissionDenied):
            error_message = (
                f"Error: Permission denied while {context} to streaming service: {self.name}.\n"
                f"This likely indicates insufficient permissions for {self.topic_id} in {self.project_id}."
            )
        else:
            error_message = (
                f"Unexpected error during {context} for streaming service: {self.name}: {exception}. Please review your configuration and credentials."
            )

        print(error_message)


