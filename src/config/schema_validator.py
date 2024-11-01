from pydantic import BaseModel, Field
from typing import List, Optional, Literal, Any

# TODO: Need to implement conditional model checking if I want to have separate models for
#  batch_creds and streaming_creds, and for every DataType:
#  https://stackoverflow.com/a/78414574 <-- pretty sure this is what i'll needs
# https://medium.com/@marcnealer/a-practical-guide-to-using-pydantic-8aafa7feebf6
# https://stackoverflow.com/questions/61392633/how-to-validate-more-than-one-field-of-a-pydantic-model
# Also consider Cerberus as an alternative
# TODO: Default values for some fields

class DataDescription(BaseModel):
    name: str
    data_type: Literal[
        'category',
        'numeric', 
        # Add these later
        # 'integer', 'float', 'bool', 'email', 'name',
        # 'phone', 'datetime', 'nested', 'image', 'video'
        ]
    allowable_values: List[Any]  # Change to List[Any] if mixed types are allowed

class ConnectionCreds(BaseModel):
    project_id: Optional[str] = None
    topic_id: Optional[str] = None
    bucket_name: Optional[str] = None
    folder_path: Optional[str] = None
    port: Optional[str] = None
    credentials_path: Optional[str] = None

class StreamingConfig(BaseModel):
    name: str
    interval: int
    size: int
    service: Literal['pubsub']
    randomise: bool
    connection_creds: ConnectionCreds
    data_description: List[DataDescription]

class BatchConfig(BaseModel):
    name: str
    interval: int
    size: Optional[int] = None
    randomise: bool
    filetype: Literal['csv', 'json', 'parquet']
    service: Literal['google_cloud_storage', 'local']
    cleanup_after: int
    connection_creds: ConnectionCreds
    data_description: List[DataDescription]

class Config(BaseModel):
    version: str
    streaming: List[StreamingConfig]
    batch: List[BatchConfig]

# Example usage
config_data = { 
  "version": "2.0",
  "streaming" : [
    {
      "name" : "streaming_1",
      "interval" : 1,
      "size" : 3,
      "service" : "pubsub",
      "randomise" : False,
      "connection_creds" : {
          "project_id": "fakeout-440306",
          "topic_id": "fakeout-receive",
          "credentials_path": "GOOGLE_APPLICATION_CREDENTIALS.json"
      },
      "data_description": [
        {
          "name": "sensor_id",
          "data_type": "category",
          "allowable_values": ["sensor_1", "sensor_2", "sensor_3"]
        },
        {
          "name": "value",
          "data_type": "numeric",
          "allowable_values": [0.0, 100.0] 
        }
      ] 
    },
    {
      "name" : "streaming_2",
      "interval" : 10,
      "size" : 3,
      "service" : "pubsub",
      "randomise" : True,
      "connection_creds" : {
          "project_id": "fakeout-440306",
          "topic_id": "fakeout-receive-2",
          "credentials_path": "GOOGLE_APPLICATION_CREDENTIALS.json"
      },
      "data_description": [
        {
          "name": "machine_id",
          "data_type": "category",
          "allowable_values": ["Machine_1", "Machine_2", "Machine_3"]
        },
        {
          "name": "value_1",
          "data_type": "numeric",
          "allowable_values": [0.0, 1.0] 
        },
        {
          "name": "value_2",
          "data_type": "numeric",
          "allowable_values": [100, 1000] 
        }
      ] 
    }
  ],
  "batch" : [
    {
      "name" : "batch_1",
      "interval" : 3600,
      "size" : 1000,
      "randomise" : True,
      "filetype" : "csv",
      "service" : "google_cloud_storage",
      "cleanup_after" : 60,
      "connection_creds" : {
        "project_id": "fakeout-440306",
        "bucket_name": "your-bucket-name",
        "folder_path": "your-folder-path",
        "credentials_path": "GOOGLE_APPLICATION_CREDENTIALS.json"
      },
      "data_description" : [
        {
          "name": "machine_id",
          "data_type" : "category",
          "allowable_values": ["Machine_1", "Machine_2", "Machine_3"]
        },
        {
          "name": "value_1",
          "data_type": "numeric",
          "allowable_values": [0.0, 1.0] 
        },
        {
          "name": "value_2",
          "data_type": "numeric",
          "allowable_values": [100, 1000] 
        }
      ]
    },
    {
      "name" : "batch_2",
      "interval" : 30,
      "filetype" : "json",
      "service" : "local",
      "randomise" : False,
      "cleanup_after" : 60,
      "connection_creds" : {
        "port" : "8080"
      },
      "data_description" : [
        {
          "name": "sensor_id",
          "data_type": "category",
          "allowable_values": ["sensor_1", "sensor_2", "sensor_3"]
        },
        {
          "name": "value",
          "data_type": "numeric",
          "allowable_values": [0.0, 100.0] 
        }
      ]
    }
  ]      
}

config = Config(**config_data)

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