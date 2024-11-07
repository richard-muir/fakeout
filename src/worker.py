import time
from threading import Thread
from typing import Any, List

from streaming_service import StreamingService
from batch_service import BatchService

class Worker:
    """
    Coordinates data generation, streaming, and batching processes using multiple threads.
    
    Attributes:
        data_generator: Object responsible for generating data records.
        streaming_service: Service used to stream generated data.
        batch_service: Service used to batch and save data periodically.
        keep_running (bool): Controls whether the worker should continue running.
        data_queue (queue.Queue): Queue to manage data between streaming and batching threads.
    """
    def __init__(
            self, 
            config
            ) -> None:
        """
        Initializes the Worker with data generation, streaming, and batch services.
        
        Args:
            data_generator: Data generator instance for producing data records.
            streaming_service: Streaming service instance for sending data to a stream.
            batch_service: Batch service instance for saving data in batches.
        """
        self.streaming_services = []
        self.batch_services = []
        self.keep_running = True

        for streaming_service in config.streaming_configs:
            self.streaming_services.append(StreamingService(streaming_service))

        for batch_service in config.batch_configs:
            self.batch_services.append(BatchService(batch_service))
        
# TODO: Need to fix the threading for multiple streaming and batch services
    def start(self) -> None:
        """
        Starts the worker by launching the streaming and batching threads.
        
        This method creates separate threads for each streaming and batching operation.
        """

        # Create and start a thread for each streaming service
        self.streaming_threads = [
            Thread(target=self._run_streaming_service, args=(service,))
            for service in self.streaming_services
        ]

        # Start threads for each batch service
        self.batch_threads = [
            Thread(target=self._run_batch_service, args=(service,))
            for service in self.batch_services
        ]

        self.all_threads = self.streaming_threads + self.batch_threads


        # Launch all threads
        for thread in self.all_threads:
            thread.start()
        
        # Wait for all threads to complete
        for thread in self.all_threads:
            thread.join()

    def stop(self) -> None:
        """
        Signals the worker to stop running by setting keep_running to False.
        """
        self.keep_running = False
        for batch_service in self.batch_services:
            batch_service.clean_old_exports()
        # PubSub doesn't have a close connection capability, but others might. 
        #  Leaving this breadcrumb here.
        # for streaming_service in self.streaming_services:
        #     streaming_service.close()


    def _run_streaming_service(self, service: StreamingService) -> None:
        """
        Manages the lifecycle of a single streaming service, handling data generation and streaming.
        
        Args:
            service (StreamingService): The streaming service to run.
        """
        while self.keep_running:
            data = service.data_generator.generate(num_records=service.block_size)
            service.push(data)
            time.sleep(service.interval)


    def _run_batch_service(self, service: BatchService) -> None:
        """
        Manages the lifecycle of a single batch service, handling data generation and batching.
        
        Args:
            service (BatchService): The batch service to run.
        """
        service.clean_old_exports()
        while self.keep_running:
            time.sleep(service.interval)
            # Generate batch data, export it, and clean up
            batch_data = service.data_generator.generate(num_records=service.block_size)
            service.export_batch(batch_data)
            print(f"Batch data exported for service: {service.service_name}")
            service.clean_old_exports()


