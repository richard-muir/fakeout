import unittest
import os
import json
from config import Config

class TestConfig(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        """Create a temporary configuration file for testing."""
        cls.test_config_path = os.path.join(os.path.dirname(__file__), 'test_config.json')
        test_config = { 
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
            json.dump(test_config, f)

    @classmethod
    def tearDownClass(cls):
        """Remove the temporary configuration file after tests."""
        if os.path.isfile(cls.test_config_path):
            os.remove(cls.test_config_path)

    def test_load_config(self):
        """Test if the configuration loads correctly."""
        config = Config.from_json(self.test_config_path)
        self.assertEqual(config.streaming_configs[0].interval, 10)
        self.assertEqual(config.batch_configs[0].name, "batch")
        self.assertEqual(config.batch_configs[0].interval, 30)
        self.assertEqual(len(config.streaming_configs[0].data_description), 3)

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

if __name__ == '__main__':
    unittest.main()
