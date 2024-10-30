# Fake Out

## Overview

Fake Out is a Python application that generates fake streaming data and periodically exports it as a batch file. 


## Features

- **Streaming Data Generation**: Continuously generates fake data records based on user-defined configurations.
- **Batch Export**: Exports accumulated streaming data to a batch file at specified intervals.
- **Configurable**: Uses a JSON configuration file to customize data generation parameters.

## Project Structure

fake-out/
│
├── src/                       # Source code directory
│   ├── __init__.py            # Makes src a package
│   ├── config.py              # Load and manage the JSON config
│   ├── data_generator.py       # Logic for generating fake data
│   ├── streaming_service.py     # Handles the streaming of data
│   ├── batch_export.py         # Handles batch export of accumulated data
│   └── main.py                 # Entry point of the application
│
├── tests/                     # Directory for unit tests
│   ├── __init__.py            # Makes tests a package
│   └── test_data_generator.py  # Tests for the data generator
│
├── Dockerfile                  # Dockerfile for containerization
├── requirements.txt            # Project dependencies
├── README.md                   # Project documentation
└── config.json                 # Example JSON config file





## Getting Started

### Prerequisites

- Python 3.7 or later
- pip (Python package installer)

### Installation

1. Clone the repository:

```bash
   git clone https://github.com/yourusername/fake_data_service.git
   cd fake_data_service
   pip install -r requirements.txt
```

### Configuration

Edit the `config.json` file to customize the data generation parameters, including the streaming interval and data records.

### Running the Service

To start the fake data service, you can run the following command after building the Docker image:

```bash
docker build -t fake_data_service .
docker run -p 80:80 fake_data_service
```

### Running Tests

To run the unit tests, use the following command:

```bash
pytest
```

### License

This project is licensed under the MIT License.

### Acknowledgments

- [Python](https://www.python.org/)
- [Docker](https://www.docker.com/)
