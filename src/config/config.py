import os
import json
from typing import List, Optional, Literal, Any, Union
from typing_extensions import Annotated

from pydantic import BaseModel, Field, model_validator, field_validator


# TODO: # Add these later
        # 'name',
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
        

class BoolField(BaseDataField):
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
    """
    Represents the configuration settings for a single streaming service in FakeOut.

    Attributes:
        name (str): The unique name of the streaming service configuration.
        interval (int): The interval in seconds between each data streaming event.
        size (int): The number of records to generate per streaming interval.
        randomise (bool): Indicates whether the data generated should be randomized.
        connection (Dict[str, Union[str, int]]): The connection details for the streaming service.
            Expected keys may include:
                - 'service' (str): The name of the streaming service (e.g., 'pubsub').
                - 'project_id' (str): The Google Cloud project ID if using Google Pub/Sub.
                - 'topic_id' (str): The Pub/Sub topic ID to which data is streamed.
                - 'credentials_path' (str): Path to the service account JSON file for authentication.
        data_description (List[Dict[str, Union[str, List]]]): A list of dictionaries defining
            the structure of each data record. Each dictionary includes:
                - 'name' (str): The name of the data field.
                - 'data_type' (str): The type of data (e.g., 'category', 'numeric').
                - 'allowable_values' (List): A list of possible values or range for the field.
    """
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
    """
    Represents the configuration settings for a single batch processing service in FakeOut.

    Attributes:
        name (str): The unique name of the batch service configuration.
        interval (int): The interval in seconds between each batch file export.
        size (int): The number of records to include in each batch export.
        randomise (bool): Indicates whether the data in each batch should be randomized.
        filetype (str): The file format for batch export (e.g., 'csv', 'json').
        cleanup_after (int): The time in minutes after which the batch file is deleted.
        connection (Dict[str, Union[str, int]]): The connection details for the batch export service.
            Expected keys may include:
                - 'service' (str): The type of storage service (e.g., 'google_cloud_storage', 'local').
                - 'project_id' (str): The Google Cloud project ID if using Google Cloud Storage.
                - 'bucket_name' (str): The bucket name for storing files if using Google Cloud Storage.
                - 'folder_path' (str): The folder path within the bucket for file storage.
                - 'port' (str): The port number for a local storage service, if applicable.
                - 'credentials_path' (str): Path to the service account JSON file for authentication.
        data_description (List[Dict[str, Union[str, List]]]): A list of dictionaries defining
            the structure of each data record. Each dictionary includes:
                - 'name' (str): The name of the data field.
                - 'data_type' (str): The type of data (e.g., 'category', 'numeric').
                - 'allowable_values' (List): A list of possible values or range for the field.
    """
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
    """
    Main configuration class for FakeOut, handling multiple streaming and batch configurations.
    """
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