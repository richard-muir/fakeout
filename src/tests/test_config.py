import unittest
import os
import json
from pydantic import ValidationError

from config import Config

from data_fields import *

class TestConfig(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        """Create a temporary configuration file for testing."""
        cls.test_config_path = os.path.join(os.path.dirname(__file__), 'test_config.json')
        cls.test_config = { 
            "version": "2.0",
            "streaming" : [
                {
                    "name" : "streaming",
                    "interval" : 10,
                    "size" : 3,
                    "randomise" : False,
                    "connection" : {
                        "service" : "pubsub",
                        "project_id": "fakeout-440306",
                        "topic_id": "feakeout-receive-2",
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
                        "data_type": "float",
                        "allowable_values": [0.0, 1.0] 
                        },
                        {
                        "name": "value_2",
                        "data_type": "integer",
                        "allowable_values": [100, 1000] 
                        }
                    ] 
                }
            ],
            "batch" : [
                {
                    "name" : "batch",
                    "interval" : 30,
                    "filetype" : "json",
                    "size" : 1000,
                    "randomise" : False,
                    "cleanup_after" : 60,
                    "connection" : {
                        "service" : "local",
                        "port" : "8080",
                        "folder_path": "your-folder-path"
                    },
                    "data_description" : [
                        {
                        "name": "sensor_id",
                        "data_type": "category",
                        "allowable_values": ["sensor_1", "sensor_2", "sensor_3"]
                        },
                        {
                        "name": "value",
                        "data_type": "float",
                        "allowable_values": [0.0, 100.0] 
                        }
                    ]
                }
            ]      
        }
        with open(cls.test_config_path, 'w') as f:
            json.dump(cls.test_config, f)

    @classmethod
    def tearDownClass(cls):
        """Remove the temporary configuration file after tests."""
        if os.path.isfile(cls.test_config_path):
            os.remove(cls.test_config_path)

    def test_load_config_from_dict(self):
        config = Config.from_dict(self.test_config)
        self.assertIsInstance(config, Config)

    def test_load_config_from_json(self):
        """Test if the configuration loads correctly."""
        config = Config.from_json(self.test_config_path)
        
        # Test general properties of the config
        self.assertEqual(config.version, "2.0")
        self.assertEqual(len(config.streaming_configs), 1)  # Only 1 streaming config in the test data
        self.assertEqual(len(config.batch_configs), 1)  # Only 1 batch config in the test data
        
        # Test specific streaming configuration values
        streaming_config = config.streaming_configs[0]
        self.assertEqual(streaming_config.name, "streaming")
        self.assertEqual(streaming_config.interval, 10)
        self.assertEqual(streaming_config.size, 3)
        self.assertFalse(streaming_config.randomise)
        
        # Test streaming connection details
        connection = streaming_config.connection
        self.assertEqual(connection.service, "pubsub")
        self.assertEqual(connection.project_id, "fakeout-440306")
        self.assertEqual(connection.topic_id, "feakeout-receive-2")
        self.assertEqual(connection.credentials_path, "GOOGLE_APPLICATION_CREDENTIALS.json")
        
        # Test data description for streaming
        data_description = streaming_config.data_description
        self.assertEqual(len(data_description), 3)
        
        # Validate individual data fields in the streaming config
        machine_id_field = data_description[0]
        self.assertEqual(machine_id_field.name, "machine_id")
        self.assertEqual(machine_id_field.data_type, "category")
        self.assertEqual(len(machine_id_field.allowable_values), 3)
        
        value_1_field = data_description[1]
        self.assertEqual(value_1_field.name, "value_1")
        self.assertEqual(value_1_field.data_type, "float")
        self.assertEqual(len(value_1_field.allowable_values), 2)
        
        value_2_field = data_description[2]
        self.assertEqual(value_2_field.name, "value_2")
        self.assertEqual(value_2_field.data_type, "integer")
        self.assertEqual(len(value_2_field.allowable_values), 2)
        
        # Test specific batch configuration values
        batch_config = config.batch_configs[0]
        self.assertEqual(batch_config.name, "batch")
        self.assertEqual(batch_config.interval, 30)
        self.assertEqual(batch_config.size, 1000)
        self.assertEqual(batch_config.filetype, "json")
        self.assertFalse(batch_config.randomise)
        
        # Test batch connection details
        batch_connection = batch_config.connection
        self.assertEqual(batch_connection.service, "local")
        self.assertEqual(batch_connection.port, "8080")
        self.assertEqual(batch_connection.folder_path, "your-folder-path")
        
        # Test data description for batch
        batch_data_description = batch_config.data_description
        self.assertEqual(len(batch_data_description), 2)
        
        # Validate individual data fields in the batch config
        sensor_id_field = batch_data_description[0]
        self.assertEqual(sensor_id_field.name, "sensor_id")
        self.assertEqual(sensor_id_field.data_type, "category")
        self.assertEqual(len(sensor_id_field.allowable_values), 3)
        
        value_field = batch_data_description[1]
        self.assertEqual(value_field.name, "value")
        self.assertEqual(value_field.data_type, "float")
        self.assertEqual(len(value_field.allowable_values), 2)

        # Test the overall length of the config's root fields
        self.assertEqual(len(config.streaming_configs[0].data_description), 3)
        self.assertEqual(len(config.batch_configs[0].data_description), 2)

        # Test the data_description field of each config for type consistency (e.g., DataField)
        for field in config.streaming_configs[0].data_description:
            self.assertTrue(isinstance(field, DATA_FIELD_TYPES))  # Ensure fields are instances of DataField classes (e.g., CategoryField, IntegerField, etc.)
        
        for field in config.batch_configs[0].data_description:
            self.assertTrue(isinstance(field, DATA_FIELD_TYPES))  # Same check for batch config data fields


    def test_missing_file(self):
        """Test if FileNotFoundError is raised for a missing config file."""
        with self.assertRaises(FileNotFoundError):
            Config.from_json('non_existent_config.json')

    def test_invalid_json(self):
        """Test if json.JSONDecodeError is raised for an invalid JSON file."""
        invalid_config_path = os.path.join(os.path.dirname(__file__), 'invalid_config.json')
        with open(invalid_config_path, 'w') as f:
            f.write("{ invalid_json }")  # Invalid JSON
        
        with self.assertRaises(json.JSONDecodeError):
            Config.from_json(invalid_config_path)
        
        # Cleanup
        os.remove(invalid_config_path)

    def test_config_with_all_required_keys(self):
        # This test should pass without any exceptions
        config = Config.from_dict(self.test_config)
        assert config.version == "2.0"

    def test_missing_version(self):
        config_data = self.test_config.copy()
        del config_data["version"]  # Remove the 'version' key
        with self.assertRaises(KeyError) as context:
            Config.from_dict(config_data)
        self.assertIn("version", str(context.exception))

if __name__ == '__main__':
    unittest.main()
