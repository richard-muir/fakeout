from abc import ABC, abstractmethod
from typing import Any, Dict
from datetime import datetime, timedelta

class BaseBatchConnection(ABC):
    """
    Abstract base class for event handlers.
    
    Provides a consistent interface for event-handling classes that connect to 
    various streaming or messaging services (e.g., Pub/Sub, Kafka). Subclasses 
    must implement methods for connecting, publishing messages, and closing the connection.

    Attributes:
        connection_creds: Credentials required for connecting to the external service, 
                          typically provided in the configuration.
    """

    @abstractmethod
    def connect(self) -> None:
        """
        Establishes a connection to the storage service.
        This method should be implemented in each subclass with specifics 
        for connecting to the target storage type (e.g., Google Cloud Storage, local).
        """
        pass

    @abstractmethod
    def export(self, data: Any, filename: str) -> None:
        """
        Exports data to the storage service with the specified filename.

        Args:
            data (Any): The data to be exported, typically as a string or bytes.
            filename (str): The filename or destination path for storing the data.
        """
        pass

    @abstractmethod
    def clean_old_uploads(self, cutoff_time: datetime) -> None:
        """
        Cleans up old uploads based on the specified cutoff time.

        Args:
            cutoff_time (Any): The time threshold for removing old uploads. The specifics of
                               time handling will be defined in each subclass.
        """
        pass