import json
import os
from typing import Any, Dict

from google.cloud import pubsub_v1
from google.oauth2 import service_account
from google.auth.exceptions import DefaultCredentialsError

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

    def __init__(self, connection: Dict[str, Any]) -> None:
        """
        Initializes the PubSubEventHandler with settings from the connection dictionary.
        
        Args:
            connection (Dict[str, Any]): Pub/Sub connection details.
        """
        super().__init__(connection)
        self.project_id = connection['project_id']
        self.topic_id = connection['topic_id']
        self.credentials_path = connection['credentials_path']
        self.publisher = None
        self.topic_path = None
              
        
    def connect(self) -> None:
        """Sets up the Pub/Sub client and prepares the topic path."""
        creds_path = os.path.join("_creds", self.credentials_path)
        self.creds = service_account.Credentials.from_service_account_file(creds_path)
        self.publisher = pubsub_v1.PublisherClient(credentials=self.creds)
        self.topic_path = self.publisher.topic_path(self.project_id, self.topic_id)


    def publish(self, data) -> None:
        """
        Publishes a message to the Pub/Sub topic.

        Args:
            data (dict): The data to be published, converted to JSON.
        """
        data = json.dumps(data).encode("utf-8")
        future = self.publisher.publish(self.topic_path, data)
        print(f"Published message ID: {future.result()}")








