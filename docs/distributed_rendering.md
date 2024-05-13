# Distributed Rendering

Distributed rendering is handled by the `distributed` and `worker` modules. The `distributed` module is responsible for distributing the rendering of videos across multiple machines. It uses Redis to manage the queue of combinations to render and the workers that render the videos. The worker module is responsible for taking a combination from the queue, rendering the video, and uploading the video to a specified location.

## Setup for Redis

We use a .env file at the root of the project to store the Redis URL. This file is read by the `distributed` and `worker` modules to connect to the Redis server. The .env file should look like this:

```bash
REDIS_HOST=<myhost>.com
REDIS_PORT=13657
REDIS_USER=default
REDIS_PASSWORD=<somepassword>
```

## Starting a worker

To start a worker, run the following command:

```bash
celery -A simian.worker worker --loglevel=info
```

## Starting the distributed rendering

To start the distributed rendering, run the following command:

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