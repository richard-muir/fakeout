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

    def __init__(self, config: Dict[str, Any]) -> None:
        """
        Initializes the PubSubEventHandler with Pub/Sub specific settings.
        
        Args:
            config (dict): Configuration dictionary including Pub/Sub-specific
                           credentials and topic information.
        """
        super().__init__(config)

        # Extract Pub/Sub-specific settings from credentials
        self.project_id = self.connection_creds['project_id']
        self.topic_id = self.connection_creds['topic_id']
        self.credentials_path = self.connection_creds['credentials_path']
              
        


    def connect(self) -> None:
        """Initializes the Pub/Sub Publisher client and prepares the topic path."""

        creds_path = os.path.join("_creds", self.credentials_path)
        self.creds = service_account.Credentials.from_service_account_file(creds_path)
        self.publisher = pubsub_v1.PublisherClient(credentials=self.creds)

        self.topic_path = self.publisher.topic_path(self.project_id, self.topic_id)


    def publish(self, data) -> None:
        """
        Publishes a message to the Pub/Sub topic.
        
        Args:
            data (dict): The data/message to publish, which is converted to JSON.
        """
        data = json.dumps(data).encode("utf-8")
    
        # Publish the message
        future = self.publisher.publish(self.topic_path, data)
        print(f"Published message ID: {future.result()}")








