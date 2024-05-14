FROM --platform=linux/x86_64 ubuntu:24.04

# Set the working directory in the container
WORKDIR /app

# Copy scripts and run the data retrieval script
COPY scripts/ ./scripts/
RUN bash scripts/get_data.sh

# Install dependencies and clean up unnecessary files in a single RUN command
RUN apt-get update && \
    apt-get install -y wget xz-utils python3-pip && \
    wget https://builder.blender.org/download/daily/archive/blender-4.1.1-stable+v41.e1743a0317bc-linux.x86_64-release.tar.xz && \
    tar -xvf blender-4.1.1-stable+v41.e1743a0317bc-linux.x86_64-release.tar.xz && \
    mv blender-4.1.1-stable+v41.e1743a0317bc-linux.x86_64-release blender && \
    rm blender-4.1.1-stable+v41.e1743a0317bc-linux.x86_64-release.tar.xz

# install python 3.10
RUN apt-get install -y software-properties-common && \
    add-apt-repository ppa:deadsnakes/ppa && \
    apt-get update && \
    apt-get install -y python3.10 python3.10-distutils && \
    update-alternatives --install /usr/bin/python3 python3 /usr/bin/python3.10 1 && \
    update-alternatives --install /usr/bin/python python /usr/bin/python3.10 1 && \
    python3 -m pip install --upgrade pip

RUN apt-get install libc6-dev -y

# Copy the requirements file and install Python dependencies
COPY requirements.txt .
RUN python3 -m pip install --no-cache-dir -r requirements.txt

# Copy the application code
COPY simian/ ./simian/
COPY data/ ./data/
COPY tests/ ./tests/

# Set the entrypoint to run the batch.py script with user-provided arguments
CMD ["celery", "-A", "simian.worker", "worker", "--loglevel=info", "--concurrency=1"]