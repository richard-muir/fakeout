from datetime import datetime
import random
import pytz

from config import Config



class DataGenerator:
    """
    Generates data based on the passed Config object
    """
    
    def __init__(self, config):
        self.data_description = config.data_description
        self.keep_on_swimming = True
        self.datatype_lookup = {
            'category' : self._generate_categorical_data,
            'numeric' : self._generate_numeric_data
        }

    def generate(self):
        while self.keep_on_swimming:
            yield self._generate_fake_data()

    def stop(self):
        self.keep_on_swimming = False  # Method to set the flag to stop

    def _generate_fake_data(self):
        timestamp_data = [self._generate_datetime_data()]
        other_data = []
        for datapoint in self.data_description:
            data_type = datapoint['data_type']
            name = datapoint['name']
            allowable_values = datapoint['allowable_values']
            generating_fn = self.datatype_lookup[data_type]
            other_data.append(generating_fn(name, allowable_values))
                              
        all_data = timestamp_data + other_data 
        
        return all_data

    def _generate_datetime_data(self):
        now = datetime.now(pytz.utc)
        return {'datetime': now.isoformat()}
    
    def _generate_categorical_data(self, name, choices):
        return {name : random.choice(choices)}
    
    def _generate_numeric_data(self, name, data_range):
        return {name : random.uniform(data_range[0], data_range[1])}


cf = Config()
dg = DataGenerator(cf)