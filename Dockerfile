FROM --platform=linux/x86_64 ubuntu:24.04

RUN apt-get update && \
    apt-get install -y \
    wget \
    xz-utils \
    bzip2 \
    python3-pip \
    python3 \
    libglu1-mesa \
    libc6-dev \
    libxrender1 \
    libsm6 \
    libopenexr-dev \ 
	build-essential \ 
	zlib1g-dev \ 
	libxmu-dev \ 
	libxi-dev \ 
	libxxf86vm-dev \ 
	libfontconfig1 \ 
    libxkbcommon-x11-0 \
    libc6-amd64-cross && \
    ln -s /usr/x86_64-linux-gnu/lib64/ /lib64 && \
    LD_LIBRARY_PATH="$LD_LIBRARY_PATH:/lib64:/usr/x86_64-linux-gnu/lib" \
    && apt-get install -y software-properties-common && \
    add-apt-repository ppa:deadsnakes/ppa && \
    apt-get update && \
    apt-get install -y python3.10 python3.10-distutils && \
    update-alternatives --install /usr/bin/python3 python3 /usr/bin/python3.10 1 && \
    update-alternatives --install /usr/bin/python python /usr/bin/python3.10 1 && \
    python3 -m pip install --upgrade pip

RUN wget https://builder.blender.org/download/daily/archive/blender-4.1.1-stable+v41.e1743a0317bc-linux.x86_64-release.tar.xz && \
    tar -xvf blender-4.1.1-stable+v41.e1743a0317bc-linux.x86_64-release.tar.xz && \
    mv blender-4.1.1-stable+v41.e1743a0317bc-linux.x86_64-release blender && \
    rm blender-4.1.1-stable+v41.e1743a0317bc-linux.x86_64-release.tar.xz

COPY scripts/ ./scripts/
RUN bash scripts/get_data.sh

COPY requirements.txt .
RUN python3 -m pip install --no-cache-dir -r requirements.txt

RUN apt-get install -y libglu1-mesa-dev

COPY simian/ ./simian/
COPY data/ ./data/
COPY tests/ ./tests/

CMD ["celery", "-A", "simian.worker", "worker", "--loglevel=info", "--concurrency=1"]