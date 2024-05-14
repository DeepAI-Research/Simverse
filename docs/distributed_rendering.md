# Distributed Rendering

Distributed rendering is handled by the `distributed` and `worker` modules. The `distributed` module is responsible for distributing the rendering of videos across multiple machines. It uses Redis to manage the queue of combinations to render and the workers that render the videos. The worker module is responsible for taking a combination from the queue, rendering the video, and uploading the video to a specified location.

## Setup for Redis and Huggingface API Key

We use a .env file at the root of the project to store the Redis URL. This file is read by the `distributed` and `worker` modules to connect to the Redis server. The .env file should look like this:

```bash
REDIS_HOST=<myhost>.com
REDIS_PORT=1337
REDIS_USER=default
REDIS_PASSWORD=<somepassword>
HF_TOKEN=<token>
HF_REPO_ID=<repo_id>
```

You can also bypass the .env file and just directly set the environment variables, for example:
```bash
export REDIS_HOST=<myhost>.com
export REDIS_PORT=1337
export REDIS_USER=default
export REDIS_PASSWORD=<somepassword>
export HF_TOKEN=<token>
export HF_REPO_ID=<repo_id>
```

## Starting a worker

To start a worker, run the following command:

```bash
celery -A simian.worker worker --loglevel=info
```

You can also build and run the Dockerfile
```bash
# build the container
docker build -t simian-worker .

# run the container with .env
docker run --env-file .env simian-worker

# run the container with environment variables
docker run -e REDIS_HOST={myhost} -e REDIS_PORT={port} -e REDIS_USER=default -e REDIS_PASSWORD={some password} -e HF_TOKEN={token} -e HF_REPO_ID={repo_id} simian-worker
```

## Starting the distributed rendering

To add the job to the queue, run the following command:

```bash
python3 simian/simian.py --start_index 0 --end_index 10 --width 1024 --height 576
```

::: simian.distributed
    :docstring:
    :members:
    :undoc-members:
    :show-inheritance:

::: simian.worker
    :docstring:
    :members:
    :undoc-members:
    :show-inheritance: