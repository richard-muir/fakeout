import json
import os
import sys
import inspect
from typing import Any, Dict

from google.cloud import pubsub_v1
from google.oauth2 import service_account
from google.auth.exceptions import DefaultCredentialsError, GoogleAuthError
from google.api_core.exceptions import NotFound, Forbidden, GoogleAPIError, ServiceUnavailable

from .base import BaseEventHandler



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
        close():
            Closes the Pub/Sub client connection to release resources.
    """
    ALL_POSSIBLE_ERRORS = (
            FileNotFoundError, 
            DefaultCredentialsError, 
            ServiceUnavailable,
            GoogleAuthError,
            NotFound, 
            Forbidden, 
            GoogleAPIError, 
            Exception
            )

    def __init__(self, connection: Dict[str, Any]) -> None:
        """
        Initializes the PubSubEventHandler with settings from the connection dictionary.
        
        Args:
            connection (Dict[str, Any]): Pub/Sub connection details.
        """
        super().__init__()
        self.project_id = connection['project_id']
        self.topic_id = connection['topic_id']
        self.credentials_path = connection['credentials_path']
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

             # Verify the topic exists
            try:
                self.client.get_topic(request={"topic": self.topic_path})
                print("Connected to Pub/Sub and verified topic.")
            except NotFound:
                print(f"Error: Topic '{self.topic_id}' not found in project '{self.project_id}'. Please verify the topic ID and project.")

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
            self._handle_error(e)
            sys.exit(1)


    def _handle_errors(self, exception: Exception):
        """Handles connection and publishing related errors with descriptive messages."""
        
         # Get the name of the calling function to determine the context
        calling_function = inspect.stack()[1].function
        context = "connection" if calling_function == "connect" else "publishing"


        if isinstance(exception, NotFound):
            error_message = (
                f"Error during {context}: The topic '{self.config['connection']['topic_id']}' does not exist "
                f"in project '{self.config['connection']['project_id']}'. Please verify that the topic is created "
                 "and the project ID is correct."
            )
        elif isinstance(exception, Forbidden):
            error_message = (
                f"Error during {context}: Permission denied when accessing the topic. "
                "Ensure the service account has the required Pub/Sub permissions."
            )
        elif isinstance(exception, ServiceUnavailable):
            error_message = (
                f"Error during {context}: Pub/Sub service is unavailable. Please try again later."
            )
        elif isinstance(exception, DefaultCredentialsError):
            error_message = (
                f"Error during {context}: Invalid credentials. Please check your service account credentials."
            )
        elif isinstance(exception, GoogleAPIError):
            error_message = (
                f"Google API error during {context}: {exception}. Please check your Google Cloud configurations and network access."
            )
        elif isinstance(exception, FileNotFoundError):
            error_message = (
                f"Error during {context}: The credentials file was not found. "
                "Please check that you put your Google credentials in the _creds folder, and that the filename is correct."
            )
        elif isinstance(exception, GoogleAuthError):
            error_message = (
                f"Error during {context}: Google authentication error.\n"
                "Exiting the application. Please check your credentials and permissions."
            )
        else:
            error_message = (
                f"Unexpected error during {context}: {exception}. Please review your configuration and credentials."
            )

        print(error_message)








