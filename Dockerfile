# Use an official Python runtime as the base image
FROM python:3.10-slim

# Set the working directory in the container
WORKDIR /app

RUN apt-get update && apt-get install -y wget

COPY scripts/ ./scripts/

RUN bash scripts/install_blender_linux.sh
RUN bash scripts/get_data.sh

# Copy the requirements file to the working directory
COPY requirements.txt .

# Install the Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the simian directory to the working directory
COPY simian/ ./simian/
COPY data/ ./data/
COPY distributed/ ./distributed/

COPY tests/ ./tests/
COPY requirements.txt ./requirements.txt

# Set the entrypoint to run the batch.py script with user-provided arguments
ENTRYPOINT ["python", "./distributed/worker.py"]