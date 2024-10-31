from typing import Any, Dict

from stream_event_handlers import *



class StreamingService:
    """
    Manages streaming events by delegating to the appropriate event handler (e.g., PubSub).
    
    This service supports different streaming providers, with a lookup table for event handlers,
    and handles connections, data pushing, and closing the handler.
    
    Attributes:
        interval (int): Interval in seconds between data streaming operations.
        n_records_pushed (int): Counter for the number of records pushed to the streaming service.
        service_name (str): Name of the streaming service being used.
        event_handler (BaseEventHandler): The active event handler responsible for streaming data.
    """

    EVENT_HANDLER_LOOKUP = {
        'pubsub' : PubSubEventHandler
        # Add other handlers here as needed
    }
    
    
    def __init__(self, config: Any) -> None:
        """
        Initializes the StreamingService with configuration and sets up the event handler.
        
        Args:
            config (Any): Configuration object containing streaming settings, including
                          interval, service type, and credentials.
        
        Raises:
            ValueError: If the specified service name is not supported.
        """
        self.interval = config.streaming_interval
        self.n_records_pushed = 0
        self.service_name = config.streaming_service

        # Validate service type, create event handler and connect
        if self.service_name not in self.EVENT_HANDLER_LOOKUP:
            raise ValueError(f"Service '{self.service_name}' is not supported.")
        
        self.event_handler = self.EVENT_HANDLER_LOOKUP[self.service_name](config)
        self.event_handler.connect()
        
    def push(self, data: Dict[str, Any]) -> None:
        """
        Publishes a data record to the event handler and increments the push counter.
        
        Args:
            data (Dict[str, Any]): Data record to be published.
        """
        self.event_handler.publish(data)
        self.n_records_pushed += 1

    def close(self) -> None:
        """
        Closes the connection to the event handler, releasing resources.
        """
        self.event_handler.close()