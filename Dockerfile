FROM --platform=linux/x86_64 ubuntu:24.04

ENV DEBIAN_FRONTEND=noninteractive
ENV TZ=UTC

RUN apt-get update && \
    apt-get install -y \
    wget \
    xz-utils \
    bzip2 \
    python3-pip \
    python3 \
    && apt-get install -y software-properties-common && \
    add-apt-repository ppa:deadsnakes/ppa && \
    apt-get update && \
    apt-get install -y python3.11 python3.11-distutils && \
    update-alternatives --install /usr/bin/python3 python3 /usr/bin/python3.11 1 && \
    update-alternatives --install /usr/bin/python python /usr/bin/python3.11 1 && \
    python3 -m pip install --upgrade pip

COPY scripts/ ./scripts/
RUN bash scripts/get_data.sh

COPY requirements.txt .
RUN python3 -m pip install --no-cache-dir -r requirements.txt

COPY simian/ ./simian/
COPY data/ ./data/
COPY tests/ ./tests/

CMD ["celery", "-A", "simian.worker", "worker", "--loglevel=info", "--concurrency=1"]