from datetime import datetime
import random
import pytz
from typing import List, Dict, Any, Iterator, Optional

from config import Config



class DataGenerator:
    """
    Generates synthetic data based on configuration settings from a Config object.
    
    Attributes:
        datetime_format_string (str): Format string for the datetime field in generated data.
        data_description (List[Dict[str, Any]]): Describes the data fields to be generated.
        keep_on_swimming (bool): Flag to indicate whether data generation should continue.
        datatype_lookup (Dict[str, Callable]): Mapping of data types to generation methods.
    """
    
    def __init__(self, data_description: Dict, datetime_format_string: str) -> None:
        """
        Initializes the DataGenerator with configuration settings.

        Args:
            config (Config): Configuration object containing settings for data generation.
        """
        self.data_description = data_description
        self.datetime_format_string = datetime_format_string
        self.keep_on_swimming = True
        self.datatype_lookup = {
            'category' : self._generate_categorical_data,
            'numeric' : self._generate_numeric_data
        }

    def generate(self, num_records: Optional[int] = 1) -> Iterator[Dict[str, Any]]:
        """
        Continuously generates synthetic data until stopped.

        Yields:
            Dict[str, Any]: A dictionary containing a data record with a timestamp 
            and fields based on the data description in the configuration.
        """
        records = []
        count = 0
        while self.keep_on_swimming and (num_records is None or count < num_records):
            records.append(self._generate_fake_data())
            count += 1
        return records

    def stop(self) -> None:
        """
        Stops the data generation process.
        """
        self.keep_on_swimming = False  # Method to set the flag to stop

    def _generate_fake_data(self) -> Dict[str, Any]:
        """
        Generates a single data record with a timestamp and other fields defined 
        in the configuration.

        Returns:
            Dict[str, Any]: A dictionary containing generated data fields and a timestamp.
        """
        all_data = self._generate_timestamp_data()
        
        for datapoint in self.data_description:
            try:
                data_type = datapoint['data_type']
                name = datapoint['name']
                allowable_values = datapoint['allowable_values']
                generating_fn = self.datatype_lookup[data_type]
                all_data.update(generating_fn(name, allowable_values))
            except Exception as e:
                print(f"Error generating data for {name}: {e}")
                continue  # Skip this data poin
                              
        return all_data

    def _generate_timestamp_data(self) -> str:
        """
        Generates the current UTC datetime string in the configured format.

        Returns:
            Dict[str, str]: A dictionary with the current datetime as a formatted string.
        """
        now = datetime.now(pytz.utc)
        return {'datetime': now.strftime(self.datetime_format_string)}
    
    def _generate_categorical_data(
            self, 
            name: str, 
            choices: List[str]
            ) -> Dict[str, str]:
        """
        Generates a categorical data field by randomly selecting from provided choices.

        Args:
            name (str): Name of the data field.
            choices (List[str]): List of possible categorical values.

        Returns:
            Dict[str, str]: A dictionary containing the generated categorical data.
        """
        return {name : random.choice(choices)}
    
    def _generate_numeric_data(self, name: str, data_range: List[float]) -> Dict[str, float]:
        """
        Generates a numeric data field within the specified range.

        Args:
            name (str): Name of the data field.
            data_range (List[float]): A list with two values, specifying the minimum 
            and maximum values for the numeric range.

        Returns:
            Dict[str, float]: A dictionary containing the generated numeric data.
        """
        return {name : random.uniform(data_range[0], data_range[1])}