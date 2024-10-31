from abc import ABC, abstractmethod

class BaseEventHandler(ABC):

    def __init__(self, config):
        self.connection_creds = config.streaming_creds

    @abstractmethod
    def connect(self):
        """Connects to the event handler"""
        pass

    @abstractmethod
    def publish(self, message):
        """Publishes events to the destination"""
        pass


    @abstractmethod
    def close(self):
        """Closes the connect event handler"""
        pass

