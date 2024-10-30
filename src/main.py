import os
import signal
import sys
from src.data_generator import DataGenerator
from src.streaming_service import StreamingService
from src.batch_service import BatchService
from src.worker import Worker
from src.config import Config


def signal_handler(sig, frame):
    print("Shutting down gracefully...")
    worker.stop()  # Signal the worker to stop
    sys.exit(0)


if __name__ == "__main__":
    # Setup signal handling for graceful shutdown
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

    # Load configuration
    config = Config()  # Assuming this reads your config.json

    # Initialize services with parameters from config
    data_generator = DataGenerator(config)  
    streaming_service = StreamingService(config)
    batch_service = BatchService(config)

    # Create the Worker with all services
    worker = Worker(data_generator, streaming_service, batch_service)

    # Start the worker threads
    worker.start()  # This should start both the streaming and batch processes

    # Keep the main thread alive to allow worker to run
    worker.join()  # Wait for the worker to finish (optional)