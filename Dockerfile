# Use Python 3.11 as the base image
FROM python:3.11-slim

# Set the working directory
WORKDIR /app

# Copy the requirements and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of your code (modules, brain.py, etc.)
COPY . .

# Explicitly tell Google Cloud to run your Flask Gateway
CMD exec gunicorn --bind :$PORT --workers 1 --threads 8 --timeout 0 social_gateway:app