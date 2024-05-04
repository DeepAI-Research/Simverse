# Simian
A synthetic data generator for video caption pairs.

https://github.com/RaccoonResearch/simian/assets/18633264/54346aa8-fde4-4c11-b210-52525082a650

*Medium shot, orbiting The Moon to the right. It's mid-day and the sky is clear. The background is an air museum with a few planes parked.*

Simian creates synthetic data that is usable for generative video and video captioning tasks. The data consists of videos and captions. The videos are generated using Blender, a 3D modeling software.

## ⚠️ Experimental Pre-Alpha

This project is in open development phase and is not ready for public use. Many things are still being actively developed for an initial release. Use at your own risk.

## 🖥️ Setup

### ⚠️ IMPORTANT: Simian requires Python 3.10 or lower to run. Blender does not support Python 3.11 yet.

1. Install Python 3.10. If you're on Linux, set it up with this (gist)[https://gist.github.com/lalalune/986704a935d202ab2350ca90b2fc9755]


2. Download the datasets:
```bash
./scripts/get_data.sh
```

3. [OPTIONAL] If you're on a headless Linux server, install Xorg and start it:

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
/Applications/Blender.app/Contents/MacOS/Blender --background --python simian/render.py -- --width 1920 --height 1080 --combination_index 0 --output_dir ./renders --background_path ./backgrounds

# Linux
blender --background --python simian/render.py -- --width 1920 --height 1080 --combination_index 0 --output_dir ./renders --background_path ./backgrounds
```

Or generate all or part of the combination set using the `batch.py` script:

```bash
python3 simian/batch.py --start_index 0 --end_index 1000 --width 1024 --height 576
```

### Distributed rendering
Rendering can be distributed across multiple machines using the "distributed.py" and "worker.py" scripts.

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
python3 simian/distributed.py --start_index 0 --end_index 10 --width 1024 --height 576
```

If you want to use a custom or hosted Redis instance (recommended), you can add th redis details like this:
```bash
EXPORT REDIS_URL=<my_redis_url>
```

## 📁 Datasets

We are currently using the following datasets:
[Objaverse](https://huggingface.co/datasets/allenai/objaverse)

Backgrounds are loaded from:
[Poly Haven](https://polyhaven.com)

## 🦝 Contributing

We welcome contributions! We're especially interested in help adding and refining datasets, improving generation quality, adding new features and dynamics and allowing the project to meet more use cases.

### How to contribute

1. Check out the issues here: https://github.com/RaccoonResearch/simian/issues
2. Join our Discord here: https://discord.gg/JMfbmHdPNB
3. Get in touch with us so we can coordinate on development.
4. Or, you know, just YOLO a pull request. We're pretty chill.

## 📜 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

If you use it, please cite us:

```bibtex
@misc{Simian,
  author = {Raccoon Research},
  title = {Simian: A Synthetic Data Generator for Video Caption Pairs},
  year = {2024},
  publisher = {GitHub},
  howpublished = {\url{https://github.com/RaccoonResearch/simian}}
}
```
