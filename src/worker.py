import time
import queue
from threading import Thread

class Worker:
    def __init__(self, data_generator, streaming_service, batch_service):
        self.data_generator = data_generator
        self.streaming_service = streaming_service
        self.batch_service = batch_service
        self.keep_running = True
        self.data_queue = queue.Queue()  # Create a shared queue

    def start(self):
        streaming_thread = Thread(target=self._streaming_loop)
        batch_thread = Thread(target=self._batch_loop)
        
        streaming_thread.start()
        batch_thread.start()
        
        streaming_thread.join()
        batch_thread.join()

    def _streaming_loop(self):
        while self.keep_running:
            data = next(self.data_generator.generate())
            self.data_queue.put(data)  # Push data to the queue
            self.streaming_service.push(data)  # Stream data
            time.sleep(self.streaming_service.interval)

    def _batch_loop(self):
        while self.keep_running:
            time.sleep(self.batch_service.interval)
            batch_data = []
            while not self.data_queue.empty():
                batch_data.append(self.data_queue.get())
            self.batch_service.export_batch(batch_data)
            self.batch_service.clean_old_exports()

