from google.cloud import pubsub_v1
import json
import os

# Set the environment variable for Google Cloud authentication
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "../_creds/fakeout-440306-9fd1a97afe32.json"

# Replace 'your-project-id' and 'your-topic-id' with your values
project_id = "fakeout-440306"
topic_id = "fakeout-receive"

# Initialize Publisher client
publisher = pubsub_v1.PublisherClient()
topic_path = publisher.topic_path(project_id, topic_id)

def publish_message(data):
    """Publishes a message to the Pub/Sub topic."""
    # Data must be a bytestring for Pub/Sub
    data = json.dumps(data).encode("utf-8")
    
    # Publish the message
    future = publisher.publish(topic_path, data)
    print(f"Published message ID: {future.result()}")

# Example usage
message_data = {"sensor_id": "sensor_1", "value": 23.4}
publish_message(message_data)





class StreamingService:
    
    
    def __init__(self, config, batch_path='../public'):
        """
        Initializes the StreamingService with configuration and setup paths for export.
        
        Args:
            config (dict): Configuration dictionary for batch settings.
            batch_path (str): Directory path for saving batch files. Defaults to '../public'.
        """
        self.interval = config.streaming_interval
        self.n_records_pushed = 0

    def push(self, data):
        print(data)
        self.n_records_pushed += 1