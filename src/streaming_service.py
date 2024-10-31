from stream_event_handlers import PubSubEventHandler



class StreamingService:
    EVENT_HANDLER_LOOKUP = {
        'pubsub' : PubSubEventHandler
        # Add other handlers here as needed
    }
    
    
    def __init__(self, config):
        """
        Initializes the StreamingService with configuration and setup paths for export.
        
        Args:
            config (dict): Configuration dictionary for batch settings.
        """
        self.interval = config.streaming_interval
        self.n_records_pushed = 0
        self.service_name = config.streaming_service

        # Validate service type, create event handler and connect
        if self.service_name not in self.EVENT_HANDLER_LOOKUP:
            raise ValueError(f"Service '{self.service_name}' is not supported.")
        
        self.event_handler = self.EVENT_HANDLER_LOOKUP[self.service_name](config)
        self.event_handler.connect()
        
    def push(self, data):
        self.event_handler.publish(data)
        self.n_records_pushed += 1

    def close(self):
        self.event_handler.close()