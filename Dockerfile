# Use an official Python runtime as a parent image
FROM python:3.9-slim

# Set the working directory in the container
WORKDIR /app

# Copy the requirements file into the container
COPY requirements.txt .

# Install the dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of your application code into the container
COPY . .

# Set environment variable, but can override the GOOGLE_APPLICATION_CREDENTIALS at runtime:
    # docker run -d -p 8080:8080 -v /path/to/credentials.json:/app/config/credentials.json your-image-name
        # Here, /path/to/credentials.json should be the full path on your local machine, 
        # and /app/config/credentials.json is the target path in the container (as defined in the Dockerfile).

ENV GOOGLE_APPLICATION_CREDENTIALS=_creds/fakeout-440306-9fd1a97afe32.json

# Make port 80 available to the world outside this container
EXPOSE 80

# Run main.py when the container launches
CMD ["python", "src/main.py"]
