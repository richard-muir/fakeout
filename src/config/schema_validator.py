from typing import List, Dict, Literal, Union
from enum import Enum, IntEnum

from pydantic import Field, BaseModel, ValidationError, model_validator
# from pydantic.functional_validators import str_enum, constrained_list, constrained_float


class MainConfig(BaseModel):
    version: str = Field(..., description="Version of the configuration schema")
    streaming: List['StreamingConfig'] = Field(..., description="List of streaming services to start")
    batch: List['BatchConfig'] = Field(..., description="List of batch services to start")

class StreamingConfig(BaseModel):
    pass

class StreamingConnectionCreds(BaseModel):
    pass

class BatchConfig(BaseModel):
    pass

class BatchConnectionCreds(BaseModel):
    pass





class DataTypeEnum(str, Enum):
    category = 'category'
    numeric = 'numeric'


class DataField(BaseModel):
    name: str #= Field(..., description="The name of the field.")
    data_type: DataTypeEnum

class CategoryField(DataField):
    allowable_values: list[str] = Field(..., description="Allowed values for the category field.",
                                        min_items=1, max_items=100)

class NumericField(DataField):
    allowable_values: list[float] = Field(..., description="Allowed numeric values.",
                                          min_items=2, max_items=2
                                          )

    def validate(self):
        print("numeric validation")
        if len(set(self.allowable_values)) != 2:
            raise ValueError("allowable_values must contain exactly two distinct numbers.")
        



class DataDescription(BaseModel):
    data_description: List[Union[CategoryField, NumericField]] = Field(..., description="A list of data fields.")

    @model_validator(mode='after')
    def validate_data_fields(cls, values):
        # This will store validated fields
        validated_fields = []
        
        for field in values['data_description']:
            if field['data_type'] == 'numeric':
                validated_fields.append(NumericField(**field))
            elif field['data_type'] == 'category':
                validated_fields.append(CategoryField(**field))
            else:
                raise ValueError("Invalid data type. Must be 'numeric' or 'category'.")

        # Update the validated fields in the values
        values['data_description'] = validated_fields
        return values

    @classmethod
    def model_validate(cls, values):
        print("Model validation")
        # Call the default validation first
        values = super().model_validate(values)
        
        # Now call the custom validation method
        cls.validate_fields(values['data_description'])

        # Iterate through the data description and validate each field
        for field in values.data_description:
            print(type(field))
            if isinstance(field, NumericField):
                field.validate()  # Call validate method for NumericField
            # You can add more field type checks and validations here if necessary

        return values
        

    @classmethod
    def validate_fields(cls, v):
        print("validate_fields")
        # Ensure all fields are instances of CategoryField or NumericField
        if not all(isinstance(field, (CategoryField, NumericField)) for field in v):
            raise ValueError("All fields must be instances of CategoryField or NumericField.")
        return v
    

numeric_field = {
            "name": "value_1",
            "data_type": "numeric",
            "allowable_values": [1, 10]
        }


categorical_field = {
            "name": "machine_id",
            "data_type": "category",
            "allowable_values": ["Machine_1", "Machine_2", "Machine_3"]
        }

# try:
#     # Validate the data
#     n_test = CategoryField(**categorical_field)
#     # n_test.model_validate()
#     print(n_test)
# except ValidationError as e:
#     print("Validation error:", e)



# Example data for testing
test_data = {
    "data_description": [
        {
            "name": "machine_id",
            "data_type": "category",
            "allowable_values": ["Machine_1", "Machine_2", "Machine_3"]
        },
        {
            "name": "value_1",
            "data_type": "numeric",
            "allowable_values": [0.0, 1.0, 99]
        },
        {
            "name": "value_2",
            "data_type": "numerical",
            "allowable_values": [100, 1000]
        }
    ]
}

try:
    # Validate the data
    data_description = DataDescription(**test_data)
    print(data_description)
except ValidationError as e:
    print("\nValidation error:", e)