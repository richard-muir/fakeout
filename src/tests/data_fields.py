from config.config import (
    FloatField, 
    IntegerField, 
    CategoryField, 
    BoolField, 
    DateField, 
    DateTimeField
    )

# One master source of truth to set up any lists of all the data types for testing
# Add new data types here
DATA_FIELD_TYPES = (
    FloatField, 
    IntegerField, 
    CategoryField, 
    BoolField, 
    DateField, 
    DateTimeField
    )

ALLOWABLE_VALUES_MAPPING = {
    'category' : ['A', 'B', 'C'],
    'integer' : [1, 100],
    'float' : [0, 1],
    'bool' : [],
    'date' : ["2023-01-01", "2023-12-31"],
    'datetime' : ["2023-01-01 00:00:00", "2023-12-31 23:59:59"]
}

DATA_TYPES = list(ALLOWABLE_VALUES_MAPPING.keys())

