from typing import Any, Dict, List

from stream_event_handlers import *
from data_generator import DataGenerator



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
        self.n_records_pushed = 0

        self.service_name = config.name
        self.interval = config.interval
        self.block_size = config.size
        self.randomise = config.randomise
        self.connection_details = config.connection
        self.data_description = config.data_description

        self.data_generator = DataGenerator(config)

        self.connect_to = self.connection_details['service']

        # Validate service type, create event handler and connect
        if self.connect_to not in self.EVENT_HANDLER_LOOKUP:
            raise ValueError(f"Service '{self.connect_to}' is not supported.")
        
        self.event_handler = self.EVENT_HANDLER_LOOKUP[self.connect_to](self.connection_details)
        self.event_handler.connect()
        
    def push(self, data: List[Dict[str, Any]]) -> None:
        """
        Publishes a data record to the event handler and increments the push counter.
        
        Args:
            data (Dict[str, Any]): Data record to be published.
        """
        self.event_handler.publish(data)
        self.n_records_pushed += self.block_size

    def generate(self) -> List:
        """
        Generates a chunk of data
        """
        self.data_generator.generate(num_records=self.block_size)