from abc import ABC, abstractmethod
from typing import Any, Dict

class BaseEventHandler(ABC):
    """
    Abstract base class for event handlers.
    
    Provides a consistent interface for event-handling classes that connect to 
    various streaming or messaging services (e.g., Pub/Sub, Kafka). Subclasses 
    must implement methods for connecting, publishing messages, and closing the connection.

    Attributes:
        connection_creds: Credentials required for connecting to the external service, 
                          typically provided in the configuration.
    """

    def __init__(self) -> None:
        """
        Initializes the base event handler with connection credentials.

        Args:
            config (dict): Configuration dictionary containing credentials and other settings 
                           needed for connecting to the target service.
        """
        pass

    @abstractmethod
    def connect(self):
        """
        Establishes a connection to the external event handler.
        
        To be implemented by subclasses for connecting to their respective services.
        """
        pass

    @abstractmethod
    def publish(self, message):
        """
        Publishes a message to the event handler's destination (e.g., a topic or queue).
        
        Args:
            message (dict or str): The data/message to be published, format determined by subclasses.
        """
        pass


