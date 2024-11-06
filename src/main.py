import os
import signal
import sys
import argparse
from data_generator import DataGenerator
from streaming_service import StreamingService
from batch_service import BatchService
from worker import Worker
from config import Config


def signal_handler(sig, frame):
    print("Shutting down gracefully...")
    worker.stop()  # Signal the worker to stop
    sys.exit(0)


if __name__ == "__main__":
    # Setup argument parser
    parser = argparse.ArgumentParser(description="Run the data generator application.")
    parser.add_argument("--config", type=str, required=True, help="Path to the configuration file.")
    args = parser.parse_args()  # Parse command-line arguments


    # Setup signal handling for graceful shutdown
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

    # Load configuration
    config = Config(args.config)  # Assuming this reads your config.json

    # Create the Worker with all services
    worker = Worker(config)

    # Start the worker threads
    worker.start()  # This should start both the streaming and batch processes