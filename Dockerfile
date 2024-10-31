# Use an official Python runtime as a parent image
FROM python:3.9-slim

# Set the working directory in the container
WORKDIR /app

# Copy the current directory contents into the container at /app
COPY . /app

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Set the environment variable to point to the credentials file location
# Ensure GOOGLE_APPLICATION_CREDENTIALS points to a path within the container
# Credentials will be mounted at runtime: 
    # docker run -d -p 8080:8080 -v /path/to/credentials.json:/app/config/credentials.json your-image-name
# Here, /path/to/credentials.json should be the full path on your local machine, 
    # and /app/config/credentials.json is the target path in the container (as defined in the Dockerfile).
ENV GOOGLE_APPLICATION_CREDENTIALS="/app/config/credentials.json"

# Make port 80 available to the world outside this container
EXPOSE 80

# Run main.py when the container launches
CMD ["python", "src/main.py"]
