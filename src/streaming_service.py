

class StreamingService:
    
    
    def __init__(self, config, batch_path='../public'):
        """
        Initializes the StreamingService with configuration and setup paths for export.
        
        Args:
            config (dict): Configuration dictionary for batch settings.
            batch_path (str): Directory path for saving batch files. Defaults to '../public'.
        """
        self.interval = config.streaming_interval
        self.n_records_pushed = 0

    def push(self, data):
        print(data)
        self.n_records_pushed += 1