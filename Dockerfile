# Use an official Python runtime as the base image
FROM python:3.10-slim

# Set the working directory in the container
WORKDIR /app

RUN apt-get update && apt-get install -y wget xz-utils

COPY scripts/ ./scripts/

RUN wget https://builder.blender.org/download/daily/archive/blender-4.1.1-stable+v41.e1743a0317bc-linux.x86_64-release.tar.xz
RUN tar -xvf blender-4.1.1-stable+v41.e1743a0317bc-linux.x86_64-release.tar.xz
RUN mv blender-4.1.1-stable+v41.e1743a0317bc-linux.x86_64-release blender
RUN bash scripts/get_data.sh

# Copy the requirements file to the working directory
COPY requirements.txt .

# Install the Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the simian directory to the working directory
COPY simian/ ./simian/
COPY data/ ./data/

COPY tests/ ./tests/
COPY requirements.txt ./requirements.txt
COPY .env ./.env

# Set the entrypoint to run the batch.py script with user-provided arguments
ENTRYPOINT ["python", "./simian/worker.py"]