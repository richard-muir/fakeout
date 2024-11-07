import os
import json
from datetime import datetime, timedelta
import pytz
from typing import List, Dict, Optional

from batch_event_handlers import *
from data_generator import DataGenerator

class BatchService:
    """
    Manages batch data exports and cleans up old exports based on a specified interval.
    
    Attributes:
        interval (int): Interval in seconds for exporting batch data.
        filename_stem (str): Stem of the filename used for exports.
        batch_path (str): Path to the folder where batch files are saved.
        path (str): Complete path for the batch file, including the filename stem.
        data (list): List of data entries to be exported in each batch.
    """
    EVENT_HANDLER_LOOKUP = {
        'local' : LocalStorageConnection,
        'google_cloud_storage' : GoogleCloudStorageConnection
        # Add other handlers here as needed
    }

    def __init__(self, config: Dict, batch_path: str = 'public') -> None:
        """
        Initializes the BatchService with configuration and setup paths for export.
        
        Args:
            config (dict): Configuration dictionary for batch settings.
            batch_path (str): Directory path for saving batch files. Defaults to '../public'.
        """
        self.n_records_pushed = 0

        self.service_name = config.name
        self.interval = config.interval
        self.block_size = config.size
        self.randomise = config.randomise
        self.filetype = config.filetype
        self.cleanup_after = config.cleanup_after
        self.connection_details = config.connection
        self.data_description = config.data_description

        self.data_generator = DataGenerator(
            self.data_description, 
            config.datetime_format_string
            )
        self.datetime_format_string = config.datetime_format_string

        # Overwrite this from the config to place all the files in the public directory
        self.batch_data_destination = os.path.join(batch_path, config.connection['folder_path'])
        config.connection['folder_path'] = self.batch_data_destination

        self.connect_to = self.connection_details['service']

        # Validate service type, create event handler and connect
        if self.connect_to not in self.EVENT_HANDLER_LOOKUP:
            raise ValueError(f"Service '{self.connect_to}' is not supported.")
        
        self.event_handler = self.EVENT_HANDLER_LOOKUP[self.connect_to](self.service_name, self.connection_details)
        self.event_handler.connect()    


    def generate(self) -> List:
        """
        Generates a chunk of data
        """
        return self.data_generator.generate(num_records=self.block_size)
        

    def export_batch(self, data: List) -> None:
        """
        Exports the current batch of data to a JSON file, appending a timestamp to the filename.
        
        The batch is saved in the directory specified by `self.batch_path`, and the filename
        is derived from `self.filename_stem` with the current UTC timestamp appended.
        """
        now = datetime.now(pytz.utc).strftime(self.datetime_format_string)
        filename = self.service_name + f'_{now}.{self.filetype}'

        self.event_handler.export(data, filename)
        

    def clean_old_exports(self) -> None:
        """
        Removes batch files older than the specified `clean_after` interval.
        
        This method iterates over files in the batch directory, checks each file’s timestamp,
        and deletes files that are older than the cutoff time passed in config.
        """
        now = datetime.now(pytz.utc)
        cutoff_time = now - timedelta(seconds=self.cleanup_after)

        self.event_handler.clean_old_exports(cutoff_time, self.service_name)