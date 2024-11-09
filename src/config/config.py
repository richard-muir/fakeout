import os
import json
from typing import List, Optional, Literal, Any, Union
from typing_extensions import Annotated

from pydantic import BaseModel, Field, model_validator, field_validator


# TODO: # Add these later
        # 'integer', 'float', 'bool', 'email', 'name',
        # 'phone', 'datetime', 'nested', 'image', 'video'
# TODO: Field decriptions


def validate_values_different(allowable_values):
    if len(set(allowable_values)) != 2:
        raise ValueError("allowable_values must contain exactly two distinct numbers.")
    return allowable_values
    

class BaseDataField(BaseModel):
    proportion_nulls: float = Field(default=0,
                                    description="Likelihood of a single record having null for this value",
                                    ge=0,
                                    le=1
                                    )
    
    @field_validator('proportion_nulls', mode='before')
    @classmethod
    def bound_proportion_nulls(cls, value: float) -> float:
        """Ensure proportion_nulls is between 0 and 1."""
        return max(0, min(value, 1))
    

class CategoryField(BaseDataField):
    name: str
    data_type: Literal['category']
    allowable_values: List[str] = Field(..., 
                                        description="Allowed values for the category field.",
                                        min_items=1, 
                                        max_items=100)
    


class IntegerField(BaseDataField):
    name: str
    data_type: Literal['integer']
    allowable_values: List[int] = Field(..., 
                                        description="Min and max values defining the range of allowable values in the colums",
                                        min_items=2, 
                                        max_items=2)
    
    validate_fields = field_validator("allowable_values")(validate_values_different)
        
        
class FloatField(BaseDataField):
    name: str
    data_type: Literal['float']
    allowable_values: List[float] = Field(..., 
                                        description="Min and max values defining the range of allowable values in the colums",
                                        min_items=2, 
                                        max_items=2)
    
    validate_fields = field_validator("allowable_values")(validate_values_different)
        

# Inherits from this because we don't want to validate allowable values
class BoolField(BaseModel):
    name: str
    data_type: Literal['bool']

        

class DateField(BaseDataField):
    name: str
    data_type: Literal['date']
    allowable_values: List[str] = Field(..., 
                                        description="Min and max values defining the range of allowable values in the colums",
                                        min_items=2, 
                                        max_items=2)
    
    validate_fields = field_validator("allowable_values")(validate_values_different)
        

class DateTimeField(BaseDataField):
    name: str
    data_type: Literal['datetime']
    allowable_values: List[str] = Field(..., 
                                        description="Min and max values defining the range of allowable values in the colums",
                                        min_items=2, 
                                        max_items=2)
    
    validate_fields = field_validator("allowable_values")(validate_values_different)
    
        
    


# DataField needs to be defined like this in order to validate each of the possible types
#  in a list. 
#  Thanks: https://stackoverflow.com/questions/70914419/how-to-get-pydantic-to-discriminate-on-a-field-within-listuniontypea-typeb
DataField = Annotated[
    Union[
        FloatField, 
        IntegerField,
        CategoryField,
        BoolField,
        DateField,
        DateTimeField
    ],
    Field(discriminator="data_type")]


class BatchConnectionCredsGCP(BaseModel):
    service: Literal['google_cloud_storage']
    project_id: str
    bucket_name: str
    folder_path: str
    credentials_path: str


class BatchLocalCreds(BaseModel):
    service: Literal['local']
    port: str
    folder_path: str


class StreamingConnectionCredsPubSub(BaseModel):
    service: Literal['pubsub']
    project_id: str
    topic_id: str
    credentials_path: str


class StreamingConfig(BaseModel):
    name: str
    interval: int = 60 # Every minute
    size: int = 3 # rows
    randomise: bool = False
    datetime_format_string: str = '%Y%m%d %H%M%S %f %z'
    connection: Union[
        StreamingConnectionCredsPubSub
        ] = Field(..., discriminator='service')
    data_description: List[DataField] = Field(..., max_items=99, min_items=1)


class BatchConfig(BaseModel):
    name: str
    filetype: Literal[
        # 'csv', 
        'json',
        # 'parquet'
        ]
    interval: int = 60*60*24 # Daily
    size: int = 1000 # Rows
    cleanup_after: Union[int, None] = 60*60*24*7 # Weekly
    randomise: bool = False
    datetime_format_string: str = '%Y%m%d %H%M%S %f %z'
    connection: Union[
        BatchLocalCreds,
        BatchConnectionCredsGCP
        ] = Field(..., discriminator='service')
    data_description: List[DataField] = Field(..., max_items=99, min_items=1)


class Config(BaseModel):
    version: str
    streaming_configs: List[StreamingConfig] = Field(max_items=5)
    batch_configs: List[BatchConfig] = Field(max_items=5)

    @classmethod
    def from_json(cls, file_path: str = 'config.json') -> "Config":
        """
        Class method to create an instance from a JSON file.
        """
        config_file_path = os.path.join(os.path.dirname(__file__), '..', '..', file_path)
        with open(config_file_path, 'r') as file:
            config_data = json.load(file)
    
        # Validate and transform data
        streaming_configs = [
            StreamingConfig(**stream)
            for stream in config_data.get("streaming", [])
        ]
        batch_configs = [
            BatchConfig(**batch)
            for batch in config_data.get("batch", [])
        ]

        # Initialize ConfigValidator with transformed data
        return cls(
            version=config_data.get("version", "1.0"),
            streaming_configs=streaming_configs,
            batch_configs=batch_configs
        )