from random import choice, uniform, randint
from datetime import datetime, timedelta
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
            'category': self._generate_categorical_data,
            'float': self._generate_float_data,
            'integer': self._generate_integer_data,
            'bool': self._generate_boolean_data,
            'date': self._generate_date_data,
            'datetime': self._generate_datetime_data
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
        generated_at = datetime.now(pytz.utc).strftime(self.datetime_format_string)

        while self.keep_on_swimming and (num_records is None or count < num_records):
            new_row = self._generate_fake_data(generated_at)
            print(new_row)
            records.append(new_row)
            count += 1

        print(records)
        return records

    def stop(self) -> None:
        """
        Stops the data generation process.
        """
        self.keep_on_swimming = False  # Method to set the flag to stop

    def _generate_fake_data(self, timestamp) -> Dict[str, Any]:
        """
        Generates a single data record with a timestamp and other fields defined 
        in the configuration.

        Returns:
            Dict[str, Any]: A dictionary containing generated data fields and a timestamp.
        """
        base_data = {"generated_at" : timestamp}
        for datapoint in self.data_description:
            try:
                data_type = datapoint['data_type']
                generating_fn = self.datatype_lookup[data_type]
                output = generating_fn(datapoint)
                base_data.update(output)
            except Exception as e:
                print(f"Error generating data for {datapoint['name']}: {e}")
                continue  # Skip this data poin

        return base_data
    
    
    def _generate_categorical_data(self, field_config: Dict) -> Dict:
        """
        Generates a categorical data field with the option to return None based on proportion_nulls.

        Args:
            field_config (Dict): Configuration dictionary for the field.

        Returns:
            Dict[str, Union[str, None]]: A dictionary containing the generated categorical data or None.
        """
        if random.random() < field_config.get("proportion_nulls", 0):
            return {field_config["name"]: None}
        return {field_config["name"]: random.choice(field_config["allowable_values"])}
    

    def _generate_float_data(self, field_config: Dict) -> Dict:
        """
        Generates a numeric data field within the specified range, with optional nulls.

        Args:
            field_config (Dict): Configuration dictionary for the field.

        Returns:
            Dict: A dictionary containing the generated numeric data or None.
        """
        if random.random() < field_config.get("proportion_nulls", 0):
            return {field_config["name"]: None}
        data_range = field_config["allowable_values"]
        return {field_config["name"]: random.uniform(data_range[0], data_range[1])}
    
    
    def _generate_integer_data(self, field_config: Dict) -> Dict:
        """
        Generates an integer data field within the specified range, with optional nulls.

        Args:
            field_config (Dict): Configuration dictionary for the field.

        Returns:
            Dict[str, Union[int, None]]: A dictionary containing the generated integer data or None.
        """
        if random.random() < field_config.get("proportion_nulls", 0):
            return {field_config["name"]: None}
        data_range = field_config["allowable_values"]
        return {field_config["name"]: random.randint(data_range[0], data_range[1])}
    

    def _generate_boolean_data(self, field_config: Dict) -> Dict:
        """
        Generates a boolean data field with optional nulls.

        Args:
            field_config (Dict): Configuration dictionary for the field.

        Returns:
            Dict[str, Union[bool, None]]: A dictionary containing the generated boolean data or None.
        """
        if random.random() < field_config.get("proportion_nulls", 0):
            return {field_config["name"]: None}
        return {field_config["name"]: random.choice([True, False])}
    
    
    def _generate_date_data(self, field_config: Dict) -> Dict:
        """
        Generates a date string within the specified range, with optional nulls.

        Args:
            field_config (Dict): Configuration dictionary for the field.

        Returns:
            Dict[str, Union[str, None]]: A dictionary containing the generated date data or None.
        """
        if random.random() < field_config.get("proportion_nulls", 0):
            return {field_config["name"]: None}
        
        #TODO add in more date type checking to support different formats
        start_date = datetime.strptime(field_config["allowable_values"][0], "%Y-%m-%d")
        end_date = datetime.strptime(field_config["allowable_values"][1], "%Y-%m-%d")
        random_date = start_date + timedelta(days=random.randint(0, (end_date - start_date).days))
        return {field_config["name"]: random_date.strftime("%Y-%m-%d")}
    
    
    def _generate_datetime_data(self, field_config: Dict) -> Dict:
        """
        Generates a datetime string within the specified range, with optional nulls.

        Args:
            field_config (Dict): Configuration dictionary for the field.

        Returns:
            Dict[str, Union[str, None]]: A dictionary containing the generated datetime data or None.
        """
        if random.random() < field_config.get("proportion_nulls", 0):
            return {field_config["name"]: None}
        #TODO add in more date type checking to support different formats. 
        #  Consider pulling into a different function to support _generate_date_data
        start_datetime = datetime.strptime(field_config["allowable_values"][0], "%Y-%m-%d %H:%M:%S")
        end_datetime = datetime.strptime(field_config["allowable_values"][1], "%Y-%m-%d %H:%M:%S")
        random_datetime = start_datetime + timedelta(seconds=random.randint(0, int((end_datetime - start_datetime).total_seconds())))
        return {field_config["name"]: random_datetime.strftime("%Y-%m-%d %H:%M:%S")}
    