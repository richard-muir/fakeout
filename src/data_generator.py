from datetime import datetime
import random
import pytz
from typing import List, Dict, Any, Iterator

from config import Config



class DataGenerator:
    """
    Generates data based on the passed Config object
    """
    
    def __init__(self, config: Config) -> None:
        self.datetime_format_string = config.datetime_format_string
        self.data_description = config.data_description
        self.keep_on_swimming = True
        self.datatype_lookup = {
            'category' : self._generate_categorical_data,
            'numeric' : self._generate_numeric_data
        }

    def generate(self) -> Iterator[Dict[str, Any]]:
        """Generate fake data continuously until stopped."""
        while self.keep_on_swimming:
            yield self._generate_fake_data()

    def stop(self) -> None:
        """Stop the data generation process."""
        self.keep_on_swimming = False  # Method to set the flag to stop

    def _generate_fake_data(self) -> Dict[str, Any]:
        """Generate a complete set of fake data including a timestamp and other
        fields defined in the config."""
        all_data = self._generate_datetime_data()
        
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

    def _generate_datetime_data(self) -> str:
        """Generate the current UTC datetime."""
        now = datetime.now(pytz.utc)
        return {'datetime': now.strftime(self.datetime_format_string)}
    
    def _generate_categorical_data(
            self, 
            name: str, 
            choices: List[str]
            ) -> Dict[str, str]:
        """Generate categorical data based on the provided choices."""
        return {name : random.choice(choices)}
    
    def _generate_numeric_data(self, name: str, data_range: List[float]) -> Dict[str, float]:
        """Generate numeric data based on the provided range."""
        return {name : random.uniform(data_range[0], data_range[1])}


cf = Config()
dg = DataGenerator(cf)