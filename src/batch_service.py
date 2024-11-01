import os
import json
from datetime import datetime, timedelta
import pytz
from typing import List, Dict, Optional

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

    def __init__(self, config: Dict[str, str], batch_path: str = 'public') -> None:
        """
        Initializes the BatchService with configuration and setup paths for export.
        
        Args:
            config (dict): Configuration dictionary for batch settings.
            batch_path (str): Directory path for saving batch files. Defaults to '../public'.
        """
        self.datetime_format_string = config.datetime_format_string
        self.interval = config.batch_interval
        self.filename_stem = config.batch_file_name
        self.batch_path = batch_path
        self.cleanup_after = config.batch_cleanup_after
        self.path = os.path.join(batch_path, self.filename_stem)
        self.data = []
        

    def export_batch(self) -> None:
        """
        Exports the current batch of data to a JSON file, appending a timestamp to the filename.
        
        The batch is saved in the directory specified by `self.batch_path`, and the filename
        is derived from `self.filename_stem` with the current UTC timestamp appended.
        """
        now = datetime.now(pytz.utc).strftime(self.datetime_format_string)
        output_path = self.path + f'_{now}.json'
        with open(output_path, 'w') as f:
            json.dump(self.data, f, indent=4)
        

    def clean_old_exports(self) -> None:
        """
        Removes batch files older than the specified `clean_after` interval.
        
        This method iterates over files in the batch directory, checks each file’s timestamp,
        and deletes files that are older than the cutoff time passed in config.
        """
        now = datetime.now(pytz.utc)
        cutoff_time = now - timedelta(seconds=self.cleanup_after)

        deleted_files = []
        # Iterate through files in the folder
        for filename in os.listdir(self.batch_path):
            if filename.startswith(self.filename_stem):  # Check if it's an export file
                file_time = self.__parse_timestamp_from_filename(filename)
                
                # Check if the file is older than the cutoff time
                if file_time and file_time < cutoff_time:
                    self.__delete_file(filename)
                    deleted_files.append(filename)
        print(f"{len(deleted_files)} exported batch files deleted")


    def _clear_batch_data(self) -> None:
        """Resets the batch data to an empty list"""
        self.data = []


    def __parse_timestamp_from_filename(self, filename: str) -> Optional[datetime]:
        """Extracts and returns the datetime object from the filename."""
        try:
            timestamp_str = filename.split('_')[-1].replace('.json', '')
            return datetime.strptime(timestamp_str, self.datetime_format_string).astimezone(pytz.utc)
        except ValueError:
            print(f"Could not parse timestamp from filename: {filename}")
            return None
        

    def __delete_file(self, filename: str) -> None:
        """Deletes the specified file and logs the deletion."""
        file_path = os.path.join(self.batch_path, filename)
        os.remove(file_path)
        print(f"Deleted old export file: {file_path}")