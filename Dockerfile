# Use a base Python image
FROM ubuntu:latest

RUN apt-get update && apt-get install -y python3 python3-pip

# Set the working directory in the container
WORKDIR /app

# Copy the Python application files into the container
COPY . .

RUN mkdir log

# Install application dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Expose the port your Flask application is running on
EXPOSE 5000

# Define the command to run your Python server
CMD ["python3", "app.py"]
