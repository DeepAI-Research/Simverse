# Getting Started

Below are some quick notes to get you up and running. Please read through the rest of the documentation for more detailed information.

## 🖥️ Setup

1. Download Blender. If you're on Linux, set it up with this script:

```bash
bash scripts/install_blender_linux.sh
```

2. Download the datasets:
```bash
./scripts/get_data.sh
```

3. If you're on a headless Linux server, install Xorg and start it:

```bash
sudo apt-get install xserver-xorg -y && \
sudo python3 scripts/start_x_server.py start
```

## 📸 Usage

## Generating Combinations

```bash
python3 simian/combiner.py --count 1000 --seed 42
```

## Generating Videos

You can generate individually:
```bash
# MacOS
/Applications/Blender.app/Contents/MacOS/Blender --background --python simian/render.py -- --width 1920 --height 1080 --combination_index 0 --output_dir ./renders --hdri_path ./backgrounds

# Linux
blender --background --python simian/render.py -- --width 1920 --height 1080 --combination_index 0 --output_dir ./renders --hdri_path ./backgrounds
```

Or generate all or part of the combination set using the `batch.py` script:

```bash
python3 simian/batch.py --start_index 0 --end_index 1000 --width 1024 --height 576
```

## Distributed rendering
Rendering can be distributed across multiple machines using the "simian.py" and "worker.py" scripts.

First, make sure you have Redis set up
```bash
scripts/setup_redis.sh
```

Now, start your workers
```bash
celery -A simian.worker worker --loglevel=info
```

Now issue work to your task queue

```bash
python3 simian/simian.py --start_index 0 --end_index 10 --width 1024 --height 576
```