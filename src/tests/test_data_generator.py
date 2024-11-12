import unittest
from datetime import datetime
from unittest.mock import MagicMock
from data_generator import DataGenerator
from config import DataDescription


class TestDataGenerator(unittest.TestCase):

    def setUp(self):
        # Mock configuration for testing
        self.data_description = [
            {"name": "date_field", "data_type": "date", "allowable_values": ["2023-01-01", "2023-12-31"], "proportion_nulls": 0},
            {"name": "datetime_field", "data_type": "datetime", "allowable_values": ["2023-01-01 00:00:00", "2023-12-31 23:59:59"], "proportion_nulls": 0},
            {"name": "category_field", "data_type": "category", "allowable_values": ["A", "B", "C"], "proportion_nulls": 0},
            {"name": "integer_field", "data_type": "integer", "allowable_values": [0, 10], "proportion_nulls": 0},
            {"name": "float_field", "data_type": "float", "allowable_values": [0.0, 1.0], "proportion_nulls": 0},
            {"name": "bool_field", "data_type": "bool", "proportion_nulls": 0}
        ]
        self.data_description = DataDescription(self.data_description)
        print(self.data_description[0])
        self.datetime_format = "%Y-%m-%d %H:%M:%S"
        self.generator = DataGenerator(self.data_description, self.datetime_format)


        # Add new data types here
        self.allowable_values_mapping = {
            'category' : ['A', 'B', 'C'],
            'integer' : [1, 100],
            'float' : [0, 1],
            'bool' : [],
            'date' : ["2023-01-01", "2023-12-31"],
            'datetime' : ["2023-01-01 00:00:00", "2023-12-31 23:59:59"]
        }

        # and here
        self.datatype_fn_mapping = [
            ("category", self.generator._generate_categorical_data),
            ("integer", self.generator._generate_integer_data),
            ("float", self.generator._generate_float_data),
            ("bool", self.generator._generate_boolean_data),
            ("date", self.generator._generate_date_data),
            ("datetime", self.generator._generate_datetime_data),
        ]
            

    def test_initialization(self):
        self.assertEqual(self.generator.data_description, self.data_description)
        self.assertEqual(self.generator.datetime_format_string, self.datetime_format)
        self.assertTrue(self.generator.keep_on_swimming)

    def test_generate_method(self):
        # Generate a fixed number of records
        records = list(self.generator.generate(num_records=5))
        self.assertEqual(len(records), 5)
        self.assertIn("generated_at", records[0])

    def test_stop_method(self):
        # Confirm that `stop` sets keep_on_swimming to False
        self.generator.stop()
        self.assertFalse(self.generator.keep_on_swimming)

    def test_generate_date_data(self):
        field_config = next(field for field in self.generator.data_description if field.data_type == "date")
        start_date = datetime.strptime(field_config.allowable_values[0], "%Y-%m-%d")
        end_date = datetime.strptime(field_config.allowable_values[1], "%Y-%m-%d")

        for _ in range(10):
            data = self.generator._generate_date_data(field_config)
            value = data[field_config.name]
            if value is not None:
                generated_date = datetime.strptime(value, "%Y-%m-%d")
                self.assertGreaterEqual(generated_date, start_date)
                self.assertLessEqual(generated_date, end_date)
            else:
                self.assertIsNone(value)

    def test_generate_datetime_data(self):
        field_config = next(field for field in self.generator.data_description if field.data_type == "datetime")
        start_datetime = datetime.strptime(field_config.allowable_values[0], "%Y-%m-%d %H:%M:%S")
        end_datetime = datetime.strptime(field_config.allowable_values[1], "%Y-%m-%d %H:%M:%S")

        for _ in range(10):
            data = self.generator._generate_datetime_data(field_config)
            value = data[field_config.name]
            if value is not None:
                generated_datetime = datetime.strptime(value, "%Y-%m-%d %H:%M:%S")
                self.assertGreaterEqual(generated_datetime, start_datetime)
                self.assertLessEqual(generated_datetime, end_datetime)
            else:
                self.assertIsNone(value)

    def test_generate_categorical_data(self):
        field_config = next(field for field in self.generator.data_description if field.data_type == "category")
        allowable_values = field_config.allowable_values

        for _ in range(10):
            data = self.generator._generate_categorical_data(field_config)
            value = data[field_config.name]
            if value is not None:
                self.assertIn(value, allowable_values)
            else:
                self.assertIsNone(value)

    def test_generate_integer_data(self):
        field_config = next(field for field in self.generator.data_description if field.data_type == "integer")
        min_value, max_value = field_config.allowable_values

        for _ in range(10):
            data = self.generator._generate_integer_data(field_config)
            value = data[field_config.name]
            if value is not None:
                self.assertGreaterEqual(value, min_value)
                self.assertLessEqual(value, max_value)
                self.assertIsInstance(value, int)
            else:
                self.assertIsNone(value)

    def test_generate_float_data(self):
        field_config = next(field for field in self.generator.data_description if field.data_type == "float")
        min_value, max_value = field_config.allowable_values

        for _ in range(10):
            data = self.generator._generate_float_data(field_config)
            value = data[field_config.name]
            if value is not None:
                self.assertGreaterEqual(value, min_value)
                self.assertLessEqual(value, max_value)
                self.assertIsInstance(value, float)
            else:
                self.assertIsNone(value)

    def test_generate_boolean_data(self):
        field_config = next(field for field in self.generator.data_description if field.data_type == "bool")

        for _ in range(10):
            data = self.generator._generate_boolean_data(field_config)
            value = data[field_config.name]
            if value is not None:
                self.assertIn(value, [True, False])
                self.assertIsInstance(value, bool)
            else:
                self.assertIsNone(value)

    def test_no_null_values(self):
        # Test with proportion_nulls set to 0
        for data_type, generate_fn in self.datatype_fn_mapping:
            field_config = DataDescription([{
                "name": f"test_{data_type}",
                "data_type": data_type,
                "proportion_nulls": 0,
                "allowable_values": self.allowable_values_mapping[data_type]
            }])
            # Run 100 records to verify that all values are non-null
            for _ in range(100):
                data = generate_fn(field_config[0])
                value = data[field_config[0].name]
                self.assertIsNotNone(value)

    def test_all_null_values(self):
        # Test with proportion_nulls set to 1
        for data_type, generate_fn in self.datatype_fn_mapping:
            field_config = DataDescription([{
                "name": f"test_{data_type}",
                "data_type": data_type,
                "proportion_nulls": 1,
                "allowable_values": self.allowable_values_mapping[data_type]
            }])
            # Run 100 records to verify that all values are null
            for _ in range(100):
                data = generate_fn(field_config[0])
                value = data[field_config[0].name]
                self.assertIsNone(value)

    def test_half_null_values(self):
        # Test with proportion_nulls set to 0.5
        null_counts = {data_type: 0 for data_type in ["category", "integer", "float", "bool", "date", "datetime"]}
        total_records = 1000

        for data_type, generate_fn in self.datatype_fn_mapping:
            field_config = DataDescription([{
                "name": f"test_{data_type}",
                "data_type": data_type,
                "proportion_nulls": 0.5,
                "allowable_values": self.allowable_values_mapping[data_type]
            }])
            for _ in range(total_records):
                data = generate_fn(field_config[0])
                value = data[field_config[0].name]
                if value is None:
                    null_counts[data_type] += 1

            # Check if approximately 50% of the generated values are null
            null_proportion = null_counts[data_type] / total_records
            self.assertAlmostEqual(null_proportion, 0.5, delta=0.05)

if __name__ == "__main__":
    unittest.main()


