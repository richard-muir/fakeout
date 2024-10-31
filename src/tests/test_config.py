import unittest
import os
import json
from src.config import Config

class TestConfig(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        """Create a temporary configuration file for testing."""
        cls.test_config_path = os.path.join(os.path.dirname(__file__), 'test_config.json')
        test_config = {
            "streaming": {"interval": 5},
            "batch": {"file_name": "data_batch", "interval": 900},
            "data_description": [
                {"name": "sensor_id", "data_type": "string", "allowable_values": ["sensor_1", "sensor_2", "sensor_3"]},
                {"name": "value", "data_type": "float", "allowable_values": [0.0, 100.0]}
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
        config = Config(self.test_config_path)
        self.assertEqual(config.streaming_interval, 5)
        self.assertEqual(config.batch_file_name, "data_batch")
        self.assertEqual(config.batch_interval, 900)
        self.assertEqual(len(config.data_description), 2)

    def test_missing_file(self):
        """Test if FileNotFoundError is raised for a missing config file."""
        with self.assertRaises(FileNotFoundError):
            Config('non_existent_config.json')

    def test_invalid_json(self):
        """Test if json.JSONDecodeError is raised for an invalid JSON file."""
        invalid_config_path = os.path.join(os.path.dirname(__file__), 'invalid_config.json')
        with open(invalid_config_path, 'w') as f:
            f.write("{ invalid_json }")  # Invalid JSON
        
        with self.assertRaises(json.JSONDecodeError):
            Config(invalid_config_path)
        
        # Cleanup
        os.remove(invalid_config_path)

if __name__ == '__main__':
    unittest.main()
