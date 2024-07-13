FROM --platform=linux/x86_64 ubuntu:24.04

ENV DEBIAN_FRONTEND=noninteractive
ENV TZ=UTC

RUN apt-get update && \
    apt-get install -y \
    python3-pip \
    python3 \
    xorg \
    git \
    && apt-get install -y software-properties-common && \
    add-apt-repository ppa:deadsnakes/ppa && \
    apt-get update && \
    apt-get install -y python3.11 python3.11-distutils python3.11-dev && \
    update-alternatives --install /usr/bin/python3 python3 /usr/bin/python3.11 1 && \
    update-alternatives --install /usr/bin/python python /usr/bin/python3.11 1 && \
    apt-get clean \
    && rm -rf /var/lib/apt/lists/*

COPY scripts/ ./scripts/
RUN bash scripts/data/get_data.sh

COPY requirements.txt .

RUN python3.11 -m pip install --upgrade --ignore-installed setuptools wheel
RUN python3.11 -m pip install omegaconf requests argparse numpy scipy rich chromadb bpy boto3
RUN python3.11 -m pip install distributask==0.0.40

COPY simian/ ./simian/
COPY data/ ./data/

CMD ["python3.11", "-m", "celery", "-A", "simian.worker", "worker", "--loglevel=info", "--concurrency=1"]