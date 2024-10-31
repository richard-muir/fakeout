from .base import BaseEventHandler
from google.cloud import pubsub_v1
import json
import os

class PubSubEventHandler(BaseEventHandler):
    def __init__(self, config):
        super().__init__(config)

        self.project_id = self.connection_creds['project_id']
        self.topic_id = self.connection_creds['topic_id']
        self.credentials_path = self.connection_creds['credentials_path']

        print("XXXXXXXXXXXXXXXXXX")

        print(os.environ.get("GOOGLE_APPLICATION_CREDENTIALS"))

        del os.environ["GOOGLE_APPLICATION_CREDENTIALS"]

        print(os.environ.get("GOOGLE_APPLICATION_CREDENTIALS"))
              
        if "GOOGLE_APPLICATION_CREDENTIALS" not in os.environ:
            # Construct the path to the credentials file
            creds_path = os.path.join("_creds", self.credentials_path)
            os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = creds_path


    def connect(self):
        # Initialize Publisher client
        self.publisher = pubsub_v1.PublisherClient()
        self.topic_path = self.publisher.topic_path(self.project_id, self.topic_id)


    def publish(self, data):
        data = json.dumps(data).encode("utf-8")
    
        # Publish the message
        future = self.publisher.publish(self.topic_path, data)
        print(f"Published message ID: {future.result()}")


    def close(self):
        """Closes the connect event handler"""
        self.publisher.close()







