import json
from typing import List, Optional, Literal, Any, Union
from typing_extensions import Annotated

from pydantic import BaseModel, Field, model_validator


# TODO: # Add these later
        # 'integer', 'float', 'bool', 'email', 'name',
        # 'phone', 'datetime', 'nested', 'image', 'video'
# TODO: Field decriptions

class CategoryField(BaseModel):
    name: str
    data_type: Literal['category']
    allowable_values: List[str] = Field(..., 
                                        description="Allowed values for the category field.",
                                        min_items=1, 
                                        max_items=100)


class NumericField(BaseModel):
    name: str
    data_type: Literal['numeric']
    allowable_values: List[float] = Field(..., 
                                        description="Min and max values defining the range of allowable values in the colums",
                                        min_items=2, 
                                        max_items=2)
    
    @model_validator(mode='after')
    def validate_values_different(self):
        if len(set(self.allowable_values)) != 2:
            raise ValueError("allowable_values must contain exactly two distinct numbers.")


# DataField needs to be defined like this in order to validate each of the possible types
#  in a list. 
#  Thanks: https://stackoverflow.com/questions/70914419/how-to-get-pydantic-to-discriminate-on-a-field-within-listuniontypea-typeb
DataField = Annotated[
    Union[
        NumericField, 
        CategoryField
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
    # REF: Need to implement conditional model checking if I want to have separate models for
    #  batch_creds and streaming_creds, and for every DataType:
    #  https://docs.pydantic.dev/latest/concepts/unions/#discriminated-unions
    connection: Union[
        StreamingConnectionCredsPubSub
        ] = Field(..., discriminator='service')
    data_description: List[DataField]


class BatchConfig(BaseModel):
    name: str
    filetype: Literal['csv', 'json', 'parquet']
    interval: int = 60*60*24 # Daily
    size: int = 1000 # Rows
    cleanup_after: int = 60*60*24*7 # Weekly
    randomise: bool = False
    connection: Union[
        BatchLocalCreds,
        BatchConnectionCredsGCP
        ] = Field(..., discriminator='service')
    data_description: List[DataField]


class ConfigValidator(BaseModel):
    version: str
    streaming: List[StreamingConfig]
    batch: List[BatchConfig]

