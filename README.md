# Fake Out

## Overview

FakeOut is a Python application that generates realistic and customisable fake streaming and batch data. 

It's useful for Data Engineers who want to test their streaming and batch processing pipelines with toy data that mimics their real-world data structures.


## Features

- **Concurrent Data Models**: Define and run multiple models simultaneously for both streaming and batch services, allowing for diverse data simulation across different configurations and services.
- **Streaming Data Generation**: Continuously generates fake data records according to user-defined configurations, supporting multiple streaming services at once.
- **Batch Export**: Exports configurable chunks of data to cloud storage services, or to the local filesystem.
- **Timestamped Data Generation**: Data is timestamped for easy debugging and time-based processing
- **Configurable**: A flexible JSON configuration file allows detailed customization of data generation parameters, enabling targeted testing and simulation.

## Getting Started

### Prerequisites

- Docker

### Installation

1. Clone the repository:

```bash
   git clone https://github.com/yourusername/fake_data_service.git
```

### Supported Services

#### Streaming
- Google Pub/Sub


#### Batch
- Google Cloud Storage
- Local file system

### Configuration

For connection to the different batch and streaming services, you will need to generate a credentials file. You'll probably want to limit the scope of these creds to only the specific Pub/Sub topics and Storage buckets, just in case. 

Currently only GCP is supported, so get your [Google Cloud Credentials JSON file](https://www.youtube.com/watch?v=rWcLDax-VmM) and save it to the /_creds directory.


Easiest if you save it as "GOOGLE_APPLICATION_CREDENTIALS.json", otherwise you need to make the following changes:
- docker-compose.yml: Under "environment", change "GOOGLE_APPLICATION_CREDENTIALS=/app/_creds/GOOGLE_APPLICATION_CREDENTIALS.json" to "GOOGLE_APPLICATION_CREDENTIALS=/app/_creds/<YOUR_GOOGLE_CREDS_FILENAME>.json
- config.json: For each streaming and batch service, change connection.credentials_path to "<YOUR_GOOGLE_CREDS_FILENAME>.json"

#### High level definition of batch and streaming services
Edit the `config.json` file to customize the batch and streaming services. You can pass lists of up to five of each.
```json
{
  "version": "2.0",
  "streaming": [
    {
      "name": "example_streaming_service",
      "interval": 5,                       // Frequency of data generation in seconds
      "size": 10,                          // Number of records generated in each batch
      "randomise": false,                  // Defaults to false. Randomisation not yet supported
      "connection": {},                    // Connection details different for each type of service
      "data_description": []               // Generate bespoke data structure
    }
  ],
  "batch": [
    {
      "name": "example_batch_service",
      "interval": 60,                      // Frequency of data export in seconds
      "size": 500,                         // Number of records per batch file
      "randomise": false,                  // Set to false for consistent data order in files
      "filetype": "json",                  // File format for export - currently only json is supported
      "cleanup_after": 3600,               // Time in seconds before deleting old batch files
      "connection": {},                    // Connection details different for each type of service
      "data_description": []               // Generate bespoke data structure
    }
  ]
}
```

#### Service Connections

There are several different services you can connect to. The `connection` field will be specific for each service.

##### Streaming
Google Pub/Sub
```json
"connection": {
  "service": "pubsub",                                      // Specifies Google Pub/Sub as the streaming service
  "project_id": "my_project_id",                           // Google Cloud project ID where Pub/Sub is enabled
  "topic_id": "my_topic_id",                          // The ID of the Pub/Sub topic that receives data
  "credentials_path": "GOOGLE_APPLICATION_CREDENTIALS.json" // Name of Google service account credentials file in the '_creds' directory
}
```

##### Batch
Google Cloud Storage
```json
"connection": {
  "service": "google_cloud_storage",                        // Specifies Google Cloud Storage as the batch storage service
  "project_id": "my_project_id",                            // Google Cloud project ID where the storage bucket is located
  "bucket_name": "my_bucket_id",                            // The name of the Cloud Storage bucket to store batch files
  "folder_path": "my_folder_path",                          // The folder path within the bucket to store batch files. Can be ''.
  "credentials_path": "GOOGLE_APPLICATION_CREDENTIALS.json" // Path to the Google service account credentials file in the '_creds' directory
}
```

Local Storage
```json
"connection": {
  "service": "local",                 // Specifies the local storage option for batch export
  "port": "8080",                     // Port number where the local server will serve files
  "folder_path": "my_folder_path"    // Path on the local system where batch files will be saved, under the 'public' directory
}
```

#### Data Definitions
Each dictionary in this list corresponds to a generated data field (or a column in aa csv).

```json
"data_description": [
  {
    "name": "sensor_id",                                     // Name of the field in the generated data
    "data_type": "category",                                 // Specifies a categorical data type
    "allowable_values": ["sensor_1", "sensor_2", "sensor_3"] // List of allowed values for categorical data
  },
  {
    "name": "value",                          // Name of the field in the generated data
    "data_type": "numeric",                   // Specifies a numeric data type
    "allowable_values": [0.0, 100.0]          // Specifies a range as [min, max] for numeric data
  }
]
```


Output data looks like below. The datetime key is automatically generated, and the rest are determined from the config:
```json
[
    {
        "datetime": "20241031 152500 098457 +0000",
        "sensor_id": "sensor_1",
        "value": 47.28257845861492
    },
    {
        "datetime": "20241031 152501 189349 +0000",
        "sensor_id": "sensor_1",
        "value": 79.39957680017326
    },
    {
        "datetime": "20241031 152502 279582 +0000",
        "sensor_id": "sensor_3",
        "value": 82.46778096117309
    },
    {
        "datetime": "20241031 152503 367012 +0000",
        "sensor_id": "sensor_2",
        "value": 69.38714157423425
    },
]
```

### Running the Service

To start fakeout, you can run the following docker-compose command to build the service image and start serving the streaming and batch services.
Batch data will be served on localhost:8080 and streaming data will be sent to the service described in the config.

```bash
docker-compose up --build
```

To close down the service, run the following:
```bash
docker-compose down
```

### Running Tests

To run the unit tests, use the following command:

```bash
pytest
```


## Project Structure

```
fake-out/
│
├── src/                            
│   ├── batch_event_handlers/       # Holds the batch event handler classes
│   │   ├── __init__.py             
│   │   ├── base.py                 # Base class for batch event handlers
│   │   ├── google_cloud_storage.py # Google Cloud Storage batch event handler
│   │   └── local.py                # Local storage batch event handler
│   ├── config/                     
│   │   ├── __init__.py             
│   │   ├── config.py               # Load and manage the JSON config
│   │   └── schema_validator.py     # Validates config schema
│   ├── data_generator/             
│   │   ├── __init__.py             
│   │   └── data_generator.py       # Logic for generating fake data
│   ├── stream_event_handlers/      
│   │   ├── __init__.py             
│   │   ├── base.py                 # Base class for stream event handlers
│   │   └── pubsub_handler.py       # Google Pub/Sub event handler class
│   ├── tests/                      
│   │   ├── __init__.py             
│   │   ├── test_config.py          # Tests for the config process   
│   │   ├── test_data_generator.py  # Tests for the data generator
│   ├── batch_service.py            # Controller for the various batch services
│   ├── streaming_service.py        # Controller for the various streaming services
│   ├── worker.py                   # Coordinates the data generator, streaming service, and batch service
│   └── main.py                     # Entry point of the application
│
├── .dockerignore                   # Docker ignore file
├── .gitignore                      # Git ignore file
├── config.json                     # Example JSON config file
├── docker-compose.yml              # Compose file for Docker
├── Dockerfile                      # Dockerfile for building the container
├── LICENSE                         # Project license
└── README.md                       # Project documentation
```



### License

This project is licensed under Unlicense Agreement.

### Acknowledgments

- [Python](https://www.python.org/)
- [Docker](https://www.docker.com/)
