import time
import queue
from threading import Thread
from typing import Any, List

from data_generator import DataGenerator
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
            streaming_services: List[StreamingService], 
            batch_services: List[BatchService]
            ) -> None:
        """
        Initializes the Worker with data generation, streaming, and batch services.
        
        Args:
            data_generator: Data generator instance for producing data records.
            streaming_service: Streaming service instance for sending data to a stream.
            batch_service: Batch service instance for saving data in batches.
        """
        self.streaming_services = streaming_services
        self.batch_services = batch_services
        self.keep_running = True
        self.data_queue = queue.Queue()  # Create a shared queue
        
# TODO: Need to fix the threading for multiple streaming and batch services
    def start(self) -> None:
        """
        Starts the worker by launching streaming and batching threads.
        
        This method creates separate threads for streaming and batching operations,
        allowing both to run concurrently.
        """
        streaming_thread = Thread(target=self._streaming_loop)
        batch_thread = Thread(target=self._batch_loop)
        
        streaming_thread.start()
        batch_thread.start()
        
        streaming_thread.join()
        batch_thread.join()

    def stop(self) -> None:
        """
        Stops the worker by cleaning up old batch exports and closing streaming resources.
        
        Calls the batch service's cleanup function and closes the streaming service.
        """
        self.batch_service.clean_old_exports()
        self.streaming_service.close()

    def _streaming_loop(self) -> None:
        """
        Handles the streaming loop, generating data and pushing it to the streaming service.
        
        This loop continuously generates data from the data generator, adds it to the data queue,
        and sends it to the streaming service, with a delay based on the streaming interval.
        """
        while self.keep_running:
            data = next(self.data_generator.generate())
            self.data_queue.put(data)  # Push data to the queue
            self.streaming_service.push(data)  # Stream data
            time.sleep(self.streaming_service.interval)

    def _batch_loop(self) -> None:
        """
        Handles the batching loop, saving data in batches at regular intervals.
        
        This loop periodically collects data from the data queue, adds it to the batch service's data list,
        and triggers the batch export function. Old exports are cleaned up after each batch save.
        """
        self.batch_service.clean_old_exports()
        while self.keep_running:
            time.sleep(self.batch_service.interval)
            # After sleeping, populate the batch service data list from the shared Queue
            while not self.data_queue.empty():
                self.batch_service.data.append(self.data_queue.get())
            # export, log & clean up    
            self.batch_service.export_batch()
            print(f"N streaming records: {self.streaming_service.n_records_pushed}\n" + 
                  f"N records uploaded in batch: {len(self.batch_service.data)}")
            self.batch_service._clear_batch_data()
            self.batch_service.clean_old_exports()

