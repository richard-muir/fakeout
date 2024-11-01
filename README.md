# Fake Out

## Overview

FakeOut is a Python application that generates fake streaming data and periodically exports it as a batch file. 

It's useful for Data Engineers who want to test their streaming and batch processing pipelines with toy data.


## Features

- **Streaming Data Generation**: Continuously generates fake data records based on user-defined configurations.
- **Timestamped Data Generation**: Data is timestamped for easy debugging
- **Batch Export**: Exports accumulated streaming data to a batch file at specified intervals.
- **Configurable**: Uses a JSON configuration file to customize data generation parameters.

## Getting Started

### Prerequisites

- Docker

### Installation

1. Clone the repository:

```bash
   git clone https://github.com/yourusername/fake_data_service.git
```

### Configuration

For connection to different messaging services, you will probably need credentials. Currently only Google Pub/Sub is supported, so to connect, you'll need to generate some credentials that give the application access to your Pub/Sub topic. You'll probably want to limit the scope of these creds, just in case. 

Get your [Google Cloud Credentials JSON file](https://www.youtube.com/watch?v=rWcLDax-VmM) and save it to the /_creds directory.


Easiest if you save it as "GOOGLE_APPLICATION_CREDENTIALS.json", otherwise you need to make the following changes:
- docker-compose.yml: Under "environment", change "GOOGLE_APPLICATION_CREDENTIALS=/app/_creds/GOOGLE_APPLICATION_CREDENTIALS.json" to "GOOGLE_APPLICATION_CREDENTIALS=/app/_creds/<YOUR_GOOGLE_CREDS_FILENAME>.json
- config.json: Change streaming.connection_creds.credentials_path to "<YOUR_GOOGLE_CREDS_FILENAME>.json"

Edit the `config.json` file to customize the data generation parameters, including the streaming interval and data records.
```json
{
   "streaming" : {                                                   # Config for the streaming service  
      "interval" : 1,                                                # How often to stream the data in seconds
      "service" : "pubsub",                                          # The service to use. Currently only Google Pub/Sub is supported
      "connection_creds" : {
         "project_id": "pub-sub-project-id",                         # The project ID where the Pub/Sub API is enabled
         "topic_id": "pub-sub-topic-id",                             # The ID of the Pub/Sub topic to receive data
         "credentials_path": "GOOGLE_APPLICATION_CREDENTIALS.json"   # The path to the credentials file
      }
   },
   "batch" : {                      # Config for the batch service
      "file_name" : "data_batch",   # The prefix of the batch files created. All files will be suffixed with the datetime of their creation
      "interval" : 10,              # How often to collect the streaming data
      "cleanup_after" : 60          # The maximum age of a batch file in seconds. All files created more than <cleanup_after> ago will be deleted
   },
   "data_description": [            # Each object in this list describes a datapoint generated in the record
      {
         "name": "sensor_id",                                        # The name of the field
         "data_type": "category",                                    # The data type, currently only 'category' and 'numeric' are supported
         "allowable_values": ["sensor_1", "sensor_2", "sensor_3"]    # The list of allowed values in the column
      },
      {
         "name": "value",
         "data_type": "numeric",
         "allowable_values": [0.0, 100.0]                            # The possible range that numeric values can take
      }
   ]            
}
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
│   ├── __init__.py                 
│   ├── config.py                   # Load and manage the JSON config
│   ├── data_generator.py           # Logic for generating fake data
│   ├── streaming_service.py        # Handles the streaming of data
│   ├── batch_service.py            # Handles batch export of accumulated data
│   ├── worker.py                   # Coordinates the data_generator, streaming_service, and batch_service
│   ├── main.py                     # Entry point of the application
│   └── stream_event_handlers/      # Holds the stream event handlers classes
│        ├── __init__.py            
│        └── base.py                # Holds the base event handler class
│        └── pubsub_handler.py      # Google Pub/Sub Event handler class
│   └── tests/                      # Directory for unit tests
│        ├── __init__.py            # Makes tests a package
│        └── test_data_generator.py # Tests for the data generator
│        └── test_config.py         # Tests for the config class
│
├── public/                         # Location where the batch files are stored - served on port 8080 in the app
│
├── docker-compose.yml              # Serve with docker-compose because it's much easier
├── Dockerfile                      # Dockerfile for containerization
├── requirements.txt                # Project dependencies
├── README.md                       # Project documentation
├── .dockerignore                   # Don't want to include the credentials file!
├── .gitignore                      # Don't want to include the credentials file!
├── LICENSE                         # License
└── config.json                     # Example JSON config file

```



### License

This project is licensed under Unlicense Agreement.

### Acknowledgments

- [Python](https://www.python.org/)
- [Docker](https://www.docker.com/)
