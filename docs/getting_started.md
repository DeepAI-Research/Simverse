# Getting Started

Below are some quick notes to get you up and running. Please read through the rest of the documentation for more detailed information.

## 🖥️ Setup

> **_NOTE:_** Simian requires Python 3.10 or 3.11.

1. Install Python 3.10. If you're on Linux, set it up with this <a href="https://gist.github.com/lalalune/986704a935d202ab2350ca90b2fc9755">gist</a>.

2. Install dependences:
```bash
pip install -r requirements.txt
```

3. Download the datasets:
```bash
./scripts/get_data.sh
```

4. [OPTIONAL] If you're on a headless Linux server, install Xorg and start it:

```bash
sudo apt-get install xserver-xorg -y && \
sudo python3 scripts/start_x_server.py start
```

## 📸 Usage

### Generating Combinations

```bash
python3 simian/combiner.py --count 1000 --seed 42
```

### Generating Videos

You can generate individually:
```bash
# MacOS
python simian/render.py

# Linux
python simian/render.py

## Kitchen sink
python simian/render.py -- --width 1920 --height 1080 --combination_index 0 --output_dir ./renders --hdri_path ./backgrounds --start_frame 1 --end_frame 65
```

Configure the flags as needed:
- `--width` and `--height` are the resolution of the video.
- `--combination_index` is the index of the combination to render.
- `--output_dir` is the directory to save the rendered video.
- `--hdri_path` is the directory containing the background images.
- `--start_frame` and `--end_frame` are the start and end frames of the video.

Or generate all or part of the combination set using the `batch.py` script:

```bash
python3 simian/batch.py --start_index 0 --end_index 1000 --width 1024 --height 576 --start_frame 1 --end_frame 65
```

### Clean up Captions

Make captions more prompt friendly.

> **_NOTE:_** Create a .env file and add your OpenAI API key
```bash
python3 scripts/openai_rephrase.py
```

### Distributed rendering
Rendering can be distributed across multiple machines using the "simian.py" and "worker.py" scripts.

You will need to set up Redis and obtain Huggingface API key to use this feature.

#### Set Up Redis
You can make a free Redis account [here](https://redis.io/try-free/).

For local testing and multiple local workers, you can use the following script to set up a local instance of Redis:
```bash
scripts/setup_redis.sh
```

#### Huggingface API Key

You can get a Huggingface API key [here](https://huggingface.co/settings/tokens).

Now, start your workers
```bash
export REDIS_HOST=<myhost>.com
export REDIS_PORT=1337
export REDIS_USER=default
export REDIS_PASSWORD=<somepassword>
export HF_TOKEN=<token>
export HF_REPO_ID=<repo_id>
celery -A simian.worker worker --loglevel=info
```

You can also build and run the worker with Docker
```bash
# build the container
docker build -t simian-worker .

# run the container with .env
docker run --env-file .env simian-worker

# run the container with environment variables
docker run -e REDIS_HOST={myhost} -e REDIS_PORT={port} -e REDIS_USER=default -e REDIS_PASSWORD={some password} -e HF_TOKEN={token} -e HF_REPO_ID={repo_id} simian-worker
```

Finally, issue work to your task queue

```bash
python3 simian/simian.py --start_index 0 --end_index 10 --width 1024 --height 576
```

If you want to use a custom or hosted Redis instance (recommended), you can add the redis details like this:
```bash
export REDIS_HOST=<myhost>.com
export REDIS_PORT=1337
export REDIS_USER=default
export REDIS_PASSWORD=<somepassword>
```

To run tests look into the test folder and run whichever test file you want

```bash
python object_test.py
```