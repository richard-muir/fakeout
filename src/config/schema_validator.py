import json
from typing import List, Optional, Literal, Any, Union
from typing_extensions import Annotated

from pydantic import BaseModel, Field, model_validator


# TODO: Need to implement conditional model checking if I want to have separate models for
#  batch_creds and streaming_creds, and for every DataType:
#  https://docs.pydantic.dev/latest/concepts/unions/#discriminated-unions
# TODO: # Add these later
        # 'integer', 'float', 'bool', 'email', 'name',
        # 'phone', 'datetime', 'nested', 'image', 'video'
# TODO: Default values for some fields

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



class Config(BaseModel):
    version: str
    streaming: List[StreamingConfig]
    batch: List[BatchConfig]

# Example usage

config_loc = r"C:\Users\richa\OneDrive\Documents\Python Scripts\fake-out\config.json"
with open(config_loc, 'r') as file:
    config_data = json.load(file)

config = Config(**config_data)


# {
#           "name": "value",
#           "data_type": "numeric",
#           "allowable_values": [0.0, 100.0] 
#         }

# {
#       "name" : "streaming_2",
#       "interval" : 10,
#       "size" : 3,
#       "randomise" : true,
#       "connection" : {
#           "service" : "pubsub",
#           "project_id": "fakeout-440306",
#           "topic_id": "fakeout-receive-2",
#           "credentials_path": "GOOGLE_APPLICATION_CREDENTIALS.json"
#       },
#       "data_description": [
#         {
#           "name": "machine_id",
#           "data_type": "category",
#           "allowable_values": ["Machine_1", "Machine_2", "Machine_3"]
#         },
#         {
#           "name": "value_1",
#           "data_type": "numeric",
#           "allowable_values": [0.0, 1.0] 
#         },
#         {
#           "name": "value_2",
#           "data_type": "numeric",
#           "allowable_values": [100, 1000] 
#         }
#       ] 
#     }

################################
# Garage - preferred configuration architecture

# class MainConfig(BaseModel):
#     pass

# class StreamingConfig(BaseModel):
#     pass

# class StreamingConnectionCreds(BaseModel):
#     pass

# class BatchConfig(BaseModel):
#     pass

# class BatchConnectionCreds(BaseModel):
#     pass

# class DataField(BaseModel):
#     pass

# class CategoryField(DataField):
#     pass

# class NumericField(DataField):
#     pass

# class DataDescription(BaseModel):
#     pass

################################
# Garage - attempt at preferred configuration architecture


# class DataTypeEnum(str, Enum):
#     category = 'category'
#     numeric = 'numeric'


# class DataField(BaseModel):
#     name: str #= Field(..., description="The name of the field.")
#     data_type: DataTypeEnum

# class CategoryField(DataField):
#     allowable_values: list[str] = Field(..., description="Allowed values for the category field.",
#                                         min_items=1, max_items=100)

# class NumericField(DataField):
#     allowable_values: list[float] = Field(..., description="Allowed numeric values.",
#                                           min_items=2, max_items=2
#                                           )

#     def validate(self):
#         print("numeric validation")
#         if len(set(self.allowable_values)) != 2:
#             raise ValueError("allowable_values must contain exactly two distinct numbers.")
        



# class DataDescription(BaseModel):
#     data_description: List[Union[CategoryField, NumericField]] = Field(..., description="A list of data fields.")

#     @model_validator(mode='after')
#     def validate_data_fields(cls, values):
#         # This will store validated fields
#         validated_fields = []
        
#         for field in values['data_description']:
#             if field['data_type'] == 'numeric':
#                 validated_fields.append(NumericField(**field))
#             elif field['data_type'] == 'category':
#                 validated_fields.append(CategoryField(**field))
#             else:
#                 raise ValueError("Invalid data type. Must be 'numeric' or 'category'.")

#         # Update the validated fields in the values
#         values['data_description'] = validated_fields
#         return values

#     @classmethod
#     def model_validate(cls, values):
#         print("Model validation")
#         # Call the default validation first
#         values = super().model_validate(values)
        
#         # Now call the custom validation method
#         cls.validate_fields(values['data_description'])

#         # Iterate through the data description and validate each field
#         for field in values.data_description:
#             print(type(field))
#             if isinstance(field, NumericField):
#                 field.validate()  # Call validate method for NumericField
#             # You can add more field type checks and validations here if necessary

#         return values
        

#     @classmethod
#     def validate_fields(cls, v):
#         print("validate_fields")
#         # Ensure all fields are instances of CategoryField or NumericField
#         if not all(isinstance(field, (CategoryField, NumericField)) for field in v):
#             raise ValueError("All fields must be instances of CategoryField or NumericField.")
#         return v
    

# numeric_field = {
#             "name": "value_1",
#             "data_type": "numeric",
#             "allowable_values": [1, 10]
#         }


# categorical_field = {
#             "name": "machine_id",
#             "data_type": "category",
#             "allowable_values": ["Machine_1", "Machine_2", "Machine_3"]
#         }

# # try:
# #     # Validate the data
# #     n_test = CategoryField(**categorical_field)
# #     # n_test.model_validate()
# #     print(n_test)
# # except ValidationError as e:
# #     print("Validation error:", e)



# # Example data for testing
# test_data = {
#     "data_description": [
#         {
#             "name": "machine_id",
#             "data_type": "category",
#             "allowable_values": ["Machine_1", "Machine_2", "Machine_3"]
#         },
#         {
#             "name": "value_1",
#             "data_type": "numeric",
#             "allowable_values": [0.0, 1.0, 99]
#         },
#         {
#             "name": "value_2",
#             "data_type": "numerical",
#             "allowable_values": [100, 1000]
#         }
#     ]
# }

# try:
#     # Validate the data
#     data_description = DataDescription(**test_data)
#     print(data_description)
# except ValidationError as e:
#     print("\nValidation error:", e)