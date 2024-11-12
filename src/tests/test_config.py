import unittest
import os
import json
from pydantic import ValidationError

from config import Config
from config.config import (
    StreamingConfig, 
    BatchConfig, 
    StreamingConnectionCredsPubSub, 
    BatchConnectionCredsGCP, 
    BatchLocalCreds,
    FloatField, 
    IntegerField,
    CategoryField,
    BoolField,
    DateField,
    DateTimeField
    )

from data_fields import *

TEST_LOCAL_BATCH_CREDS = {
        "service" : "local",
        "port" : "8080",
        "folder_path": "your-folder-path"
    }

TEST_GCP_STORAGE_BATCH_CREDS = {
        "service" : "google_cloud_storage",
        "project_id": "fakeout-440306",
        "bucket_name": "fakeout-test-bucket-1",
        "folder_path": "folder-1",
        "credentials_path": "GOOGLE_APPLICATION_CREDENTIALS.json"
    }

TEST_PUBSUB_STREAMING_CREDS = {
        "service" : "pubsub",
        "project_id": "fakeout-440306",
        "topic_id": "feakeout-receive-2",
        "credentials_path": "GOOGLE_APPLICATION_CREDENTIALS.json"
    }

TEST_DATA_DESCRIPTION = [
        {
          "name": "sensor_id",
          "data_type": "category",
          "allowable_values": ["sensor_1", "sensor_2", "sensor_3"],
          "proportion_nulls" : 0
        },
        {
          "name": "float_1",
          "data_type": "float",
          "allowable_values": [0.0, 100.0],
          "proportion_nulls" : 0
        },
        {
          "name": "integer_1",
          "data_type": "integer",
          "allowable_values": [0, 10],
          "proportion_nulls" : 0
        },
        {
          "name": "bool_1",
          "data_type": "bool",
          "proportion_nulls" : 0
        },
        {
          "name": "date_1",
          "data_type": "date",
          "allowable_values": ["2024-01-01", "2024-12-31"],
          "proportion_nulls" : 0
        },
        {
          "name": "datetime_1",
          "data_type": "datetime",
          "allowable_values": ["2024-01-01 00:00:00", "2024-12-31 00:00:00"],
          "proportion_nulls" : 0
        }
    ]

TEST_CONFIG_DICT = { 
    "version": "2.0",
    "streaming" : [
        {
            "name" : "streaming",
            "interval" : 10,
            "size" : 3,
            "randomise" : False,
            "connection" : TEST_PUBSUB_STREAMING_CREDS,
            "data_description": TEST_DATA_DESCRIPTION
        }
    ],
    "batch" : [
        {
            "name" : "batch_local",
            "interval" : 30,
            "filetype" : "json",
            "size" : 1000,
            "randomise" : False,
            "cleanup_after" : 60,
            "connection" : TEST_LOCAL_BATCH_CREDS,
            "data_description" : TEST_DATA_DESCRIPTION
        },
        {
            "name" : "batch_gcp",
            "interval" : 30,
            "filetype" : "json",
            "size" : 1000,
            "randomise" : False,
            "cleanup_after" : 60,
            "connection" : TEST_GCP_STORAGE_BATCH_CREDS,
            "data_description" : TEST_DATA_DESCRIPTION
        }
    ]      
}

# class TestConfig(unittest.TestCase):

#     @classmethod
#     def setUpClass(cls):
#         """Create a temporary configuration file for testing."""
#         cls.test_config_path = os.path.join(os.path.dirname(__file__), 'test_config.json')
#         with open(cls.test_config_path, 'w') as f:
#             json.dump(TEST_CONFIG_DICT, f)

#     @classmethod
#     def tearDownClass(cls):
#         """Remove the temporary configuration file after tests."""
#         if os.path.isfile(cls.test_config_path):
#             os.remove(cls.test_config_path)

#     def test_load_config_from_dict(self):
#         config = Config.from_dict(TEST_CONFIG_DICT)
#         self.assertIsInstance(config, Config)

#     def test_load_config_from_json(self):
#         """Test if the configuration loads correctly."""
#         config = Config.from_json(self.test_config_path)
        
#         # Test general properties of the config
#         self.assertEqual(config.version, "2.0")
#         self.assertEqual(len(config.streaming_configs), 1)  # Only 1 streaming config in the test data
#         self.assertEqual(len(config.batch_configs), 1)  # Only 1 batch config in the test data
        
#         # Test specific streaming configuration values
#         streaming_config = config.streaming_configs[0]
#         self.assertEqual(streaming_config.name, "streaming")
#         self.assertEqual(streaming_config.interval, 10)
#         self.assertEqual(streaming_config.size, 3)
#         self.assertFalse(streaming_config.randomise)
        
#         # Test streaming connection details
#         connection = streaming_config.connection
#         self.assertEqual(connection.service, "pubsub")
#         self.assertEqual(connection.project_id, "fakeout-440306")
#         self.assertEqual(connection.topic_id, "feakeout-receive-2")
#         self.assertEqual(connection.credentials_path, "GOOGLE_APPLICATION_CREDENTIALS.json")
        
#         # Test data description for streaming
#         data_description = streaming_config.data_description
#         self.assertEqual(len(data_description), 3)
        
#         # Validate individual data fields in the streaming config
#         machine_id_field = data_description[0]
#         self.assertEqual(machine_id_field.name, "machine_id")
#         self.assertEqual(machine_id_field.data_type, "category")
#         self.assertEqual(len(machine_id_field.allowable_values), 3)
        
#         value_1_field = data_description[1]
#         self.assertEqual(value_1_field.name, "value_1")
#         self.assertEqual(value_1_field.data_type, "float")
#         self.assertEqual(len(value_1_field.allowable_values), 2)
        
#         value_2_field = data_description[2]
#         self.assertEqual(value_2_field.name, "value_2")
#         self.assertEqual(value_2_field.data_type, "integer")
#         self.assertEqual(len(value_2_field.allowable_values), 2)
        
#         # Test specific batch configuration values
#         batch_config = config.batch_configs[0]
#         self.assertEqual(batch_config.name, "batch")
#         self.assertEqual(batch_config.interval, 30)
#         self.assertEqual(batch_config.size, 1000)
#         self.assertEqual(batch_config.filetype, "json")
#         self.assertFalse(batch_config.randomise)
        
#         # Test batch connection details
#         batch_connection = batch_config.connection
#         self.assertEqual(batch_connection.service, "local")
#         self.assertEqual(batch_connection.port, "8080")
#         self.assertEqual(batch_connection.folder_path, "your-folder-path")
        
#         # Test data description for batch
#         batch_data_description = batch_config.data_description
#         self.assertEqual(len(batch_data_description), 2)
        
#         # Validate individual data fields in the batch config
#         sensor_id_field = batch_data_description[0]
#         self.assertEqual(sensor_id_field.name, "sensor_id")
#         self.assertEqual(sensor_id_field.data_type, "category")
#         self.assertEqual(len(sensor_id_field.allowable_values), 3)
        
#         value_field = batch_data_description[1]
#         self.assertEqual(value_field.name, "value")
#         self.assertEqual(value_field.data_type, "float")
#         self.assertEqual(len(value_field.allowable_values), 2)

#         # Test the overall length of the config's root fields
#         self.assertEqual(len(config.streaming_configs[0].data_description), 3)
#         self.assertEqual(len(config.batch_configs[0].data_description), 2)

#         # Test the data_description field of each config for type consistency (e.g., DataField)
#         for field in config.streaming_configs[0].data_description:
#             self.assertTrue(isinstance(field, DATA_FIELD_TYPES))  # Ensure fields are instances of DataField classes (e.g., CategoryField, IntegerField, etc.)
        
#         for field in config.batch_configs[0].data_description:
#             self.assertTrue(isinstance(field, DATA_FIELD_TYPES))  # Same check for batch config data fields


#     def test_missing_file(self):
#         """Test if FileNotFoundError is raised for a missing config file."""
#         with self.assertRaises(FileNotFoundError):
#             Config.from_json('non_existent_config.json')

#     def test_invalid_json(self):
#         """Test if json.JSONDecodeError is raised for an invalid JSON file."""
#         invalid_config_path = os.path.join(os.path.dirname(__file__), 'invalid_config.json')
#         with open(invalid_config_path, 'w') as f:
#             f.write("{ invalid_json }")  # Invalid JSON
        
#         with self.assertRaises(json.JSONDecodeError):
#             Config.from_json(invalid_config_path)
        
#         # Cleanup
#         os.remove(invalid_config_path)

#     def test_config_with_all_required_keys(self):
#         # This test should pass without any exceptions
#         config = Config.from_dict(TEST_CONFIG_DICT)
#         assert config.version == "2.0"

#     def test_missing_version(self):
#         config_data = TEST_CONFIG_DICT.copy()
#         del config_data["version"]  # Remove the 'version' key
#         with self.assertRaises(ValidationError) as context:
#             Config.from_dict(config_data)
#         self.assertIn("version", str(context.exception))



class TestStreamingConfig(unittest.TestCase):
    def test_streaming_config_has_name(self):
        """Test that 'name' is required in streaming config."""
        streaming_config = TEST_CONFIG_DICT['streaming'][0].copy()
        del streaming_config['name']
        with self.assertRaises(ValidationError):
            _ = StreamingConfig(**streaming_config)

    def test_streaming_config_has_data_description(self):
        """Test that 'data_description' is required in streaming config."""
        streaming_config = TEST_CONFIG_DICT['streaming'][0].copy()
        del streaming_config['data_description']
        with self.assertRaises(ValidationError):
            _ = StreamingConfig(**streaming_config)

    def test_streaming_config_has_connection(self):
        """Test that 'connection' is required in streaming config."""
        streaming_config = TEST_CONFIG_DICT['streaming'][0].copy()
        del streaming_config['connection']
        with self.assertRaises(ValidationError):
            _ = StreamingConfig(**streaming_config)


class TestBatchConfig(unittest.TestCase):
    def test_batch_config_has_name(self):
        """Test that 'name' is required in batch config."""
        batch_config = TEST_CONFIG_DICT['batch'][0].copy()
        del batch_config['name']
        with self.assertRaises(ValidationError):
            _ = BatchConfig(**batch_config)

    def test_batch_config_has_data_description(self):
        """Test that 'data_description' is required in batch config."""
        batch_config = TEST_CONFIG_DICT['batch'][0].copy()
        del batch_config['data_description']
        with self.assertRaises(ValidationError):
            _ = BatchConfig(**batch_config)

    def test_batch_config_has_connection(self):
        """Test that 'connection' is required in batch config."""
        batch_config = TEST_CONFIG_DICT['batch'][0].copy()
        del batch_config['connection']
        with self.assertRaises(ValidationError):
            _ = BatchConfig(**batch_config)

    
        
class TestDataModels(unittest.TestCase):
    def test_categorical_data_def_has_name(self):
        categorical_field = next(field for field in TEST_DATA_DESCRIPTION if field['data_type'] == "category").copy()
        del categorical_field['name']
        with self.assertRaises(ValidationError):
            _ = CategoryField(**categorical_field)

    def test_categorical_data_def_has_allowable_values(self):
        categorical_field = next(field for field in TEST_DATA_DESCRIPTION if field['data_type'] == "category").copy()
        del categorical_field['allowable_values']
        with self.assertRaises(ValidationError):
            _ = CategoryField(**categorical_field)

    def test_categorical_data_def_allowable_values_min_length(self):
        categorical_field = next(field for field in TEST_DATA_DESCRIPTION if field['data_type'] == "category").copy()
        categorical_field['allowable_values'] = []
        with self.assertRaises(ValidationError):
            _ = CategoryField(**categorical_field)

    def test_categorical_data_def_allowable_values_max_length(self):
        categorical_field = next(field for field in TEST_DATA_DESCRIPTION if field['data_type'] == "category").copy()
        categorical_field['allowable_values'] = ['a' for i in range(200)]
        with self.assertRaises(ValidationError):
            _ = CategoryField(**categorical_field)

    def test_integer_data_def_has_name(self):
        integer_field = next(field for field in TEST_DATA_DESCRIPTION if field['data_type'] == "integer").copy()
        del integer_field['name']
        with self.assertRaises(ValidationError):
            _ = IntegerField(**integer_field)

    def test_integer_data_def_has_allowable_values(self):
        integer_field = next(field for field in TEST_DATA_DESCRIPTION if field['data_type'] == "integer").copy()
        del integer_field['allowable_values']
        with self.assertRaises(ValidationError):
            _ = IntegerField(**integer_field)

    def test_integer_data_def_allowable_values_min_length(self):
        integer_field = next(field for field in TEST_DATA_DESCRIPTION if field['data_type'] == "integer").copy()
        integer_field['allowable_values'] = [5]
        with self.assertRaises(ValidationError):
            _ = IntegerField(**integer_field)

    def test_integer_data_def_allowable_values_max_length(self):
        integer_field = next(field for field in TEST_DATA_DESCRIPTION if field['data_type'] == "integer").copy()
        integer_field['allowable_values'] = [5, 6, 7]
        with self.assertRaises(ValidationError):
            _ = IntegerField(**integer_field)

    def test_integer_data_def_allowable_values_different(self):
        integer_field = next(field for field in TEST_DATA_DESCRIPTION if field['data_type'] == "integer").copy()
        integer_field['allowable_values'] = [5, 5]
        with self.assertRaises(ValidationError):
            _ = IntegerField(**integer_field)

    def test_float_data_def_has_name(self):
        float_field = next(field for field in TEST_DATA_DESCRIPTION if field['data_type'] == "float").copy()
        del float_field['name']
        with self.assertRaises(ValidationError):
            _ = FloatField(**float_field)

    def test_float_data_def_has_allowable_values(self):
        float_field = next(field for field in TEST_DATA_DESCRIPTION if field['data_type'] == "float").copy()
        del float_field['allowable_values']
        with self.assertRaises(ValidationError):
            _ = FloatField(**float_field)

    def test_float_data_def_allowable_values_min_length(self):
        float_field = next(field for field in TEST_DATA_DESCRIPTION if field['data_type'] == "float").copy()
        float_field['allowable_values'] = [0.0]
        with self.assertRaises(ValidationError):
            _ = FloatField(**float_field)

    def test_float_data_def_allowable_values_max_length(self):
        float_field = next(field for field in TEST_DATA_DESCRIPTION if field['data_type'] == "float").copy()
        float_field['allowable_values'] = [5, 6, 7]
        with self.assertRaises(ValidationError):
            _ = IntegerField(**float_field)

    def test_float_data_def_allowable_values_different(self):
        float_field = next(field for field in TEST_DATA_DESCRIPTION if field['data_type'] == "float").copy()
        float_field['allowable_values'] = [5, 5]
        with self.assertRaises(ValidationError):
            _ = IntegerField(**float_field)

    def test_bool_data_def_has_name(self):
        bool_field = next(field for field in TEST_DATA_DESCRIPTION if field['data_type'] == "bool").copy()
        del bool_field['name']
        with self.assertRaises(ValidationError):
            _ = BoolField(**bool_field)

    def test_date_data_def_has_name(self):
        date_field = next(field for field in TEST_DATA_DESCRIPTION if field['data_type'] == "date").copy()
        del date_field['name']
        with self.assertRaises(ValidationError):
            _ = DateField(**date_field)

    def test_date_data_def_has_allowable_values(self):
        date_field = next(field for field in TEST_DATA_DESCRIPTION if field['data_type'] == "date").copy()
        del date_field['allowable_values']
        with self.assertRaises(ValidationError):
            _ = DateField(**date_field)

    def test_date_data_def_allowable_values_min_length(self):
        date_field = next(field for field in TEST_DATA_DESCRIPTION if field['data_type'] == "date").copy()
        date_field['allowable_values'] = ["2024-01-01"]
        with self.assertRaises(ValidationError):
            _ = DateField(**date_field)

    def test_date_data_def_allowable_values_max_length(self):
        date_field = next(field for field in TEST_DATA_DESCRIPTION if field['data_type'] == "date").copy()
        date_field['allowable_values'] = ["2024-01-01", "2024-03-01", "2024-01-03"]
        with self.assertRaises(ValidationError):
            _ = DateField(**date_field)

    def test_date_data_def_allowable_values_different(self):
        date_field = next(field for field in TEST_DATA_DESCRIPTION if field['data_type'] == "date").copy()
        date_field['allowable_values'] = ["2024-01-01", "2024-01-01"]
        with self.assertRaises(ValidationError):
            _ = DateField(**date_field)

    def test_datetime_data_def_has_name(self):
        datetime_field = next(field for field in TEST_DATA_DESCRIPTION if field['data_type'] == "datetime").copy()
        del datetime_field['name']
        with self.assertRaises(ValidationError):
            _ = DateTimeField(**datetime_field)

    def test_datetime_data_def_has_allowable_values(self):
        datetime_field = next(field for field in TEST_DATA_DESCRIPTION if field['data_type'] == "datetime").copy()
        del datetime_field['allowable_values']
        with self.assertRaises(ValidationError):
            _ = DateTimeField(**datetime_field)

    def test_datetime_data_def_allowable_values_min_length(self):
        datetime_field = next(field for field in TEST_DATA_DESCRIPTION if field['data_type'] == "datetime").copy()
        datetime_field['allowable_values'] = ["2024-01-01 00:00:00"]
        with self.assertRaises(ValidationError):
            _ = DateTimeField(**datetime_field)

    def test_datetime_data_def_allowable_values_max_length(self):
        datetime_field = next(field for field in TEST_DATA_DESCRIPTION if field['data_type'] == "datetime").copy()
        datetime_field['allowable_values'] = ["2024-01-01 00:00:00", "2024-01-02 00:00:00", "2024-01-03 00:00:00"]
        with self.assertRaises(ValidationError):
            _ = DateTimeField(**datetime_field)

    def test_datetime_data_def_allowable_values_different(self):
        datetime_field = next(field for field in TEST_DATA_DESCRIPTION if field['data_type'] == "datetime").copy()
        datetime_field['allowable_values'] = ["2024-01-01 00:00:00", "2024-01-01 00:00:00"]
        with self.assertRaises(ValidationError):
            _ = DateTimeField(**datetime_field)

    

if __name__ == '__main__':
    unittest.main()
