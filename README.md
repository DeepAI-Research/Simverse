# Blendgen
A synthetic data generator for video caption pairs.

https://github.com/RaccoonResearch/blendgen/assets/18633264/54346aa8-fde4-4c11-b210-52525082a650

*Medium shot, orbiting The Moon to the right. It's mid-day and the sky is clear. The background is an air museum with a few planes parked.*

Blendgen creates synthetic data that is usable for generative video and video captioning tasks. The data consists of videos and captions. The videos are generated using Blender, a 3D modeling software.

For example, a video could be:

## 🖥️ Setup

1. Download Blender. If you're on Linux, set it up with this script:

```bash
bash scripts/install_blender_linux.sh
```

2. If you're on a headless Linux server, install Xorg and start it:

```bash
sudo apt-get install xserver-xorg -y && \
  sudo python3 scripts/start_x_server.py start
```

3. Install the Python dependencies. Note that Python >3.8 is required:

```bash
pip install -r requirements.txt && pip install -e .
```

4. Download the datasets:
```bash
./scripts/get_data.sh
```

## 📸 Usage

## Generating Combinations

```bash
python3 blendgen/combiner.py --count 1000 --seed 42
```

## Batching

After setup, we can start to render objects using the `batch.py` script:

```bash
python3 blendgen/batch.py --start_index 0 --end_index 1000 --width 1024 --height 576
```

# 📁 Datasets

We are currently using the following datasets:
[Objaverse](https://huggingface.co/datasets/allenai/objaverse)

Backgrounds are loaded from:
https://polyhaven.com

# 🦝 Contributing

We welcome contributions! We're especially interested in help adding and refining datasets, improving generation quality, adding new features and dynamics and allowing the project to meet more use cases.

## How to contribute

1. Check out the issues here: https://github.com/RaccoonResearch/blendgen/issues
2. Join our Discord here: https://discord.gg/JMfbmHdPNB
3. Get in touch with us so we can coordinate on development.
4. Or, you know, just YOLO a pull request. We're pretty chill.

## Prerequisites

If you have never used Blender before, we recommend you to go through the following tutorials:

Blender Scripting Series:
https://www.youtube.com/watch?v=cyt0O7saU4Q&list=PLFtLHTf5bnym_wk4DcYIMq1DkjqB7kDb-

Blender Modeling Series:
https://www.youtube.com/playlist?list=PLjEaoINr3zgEPv5y--4MKpciLaoQYZB1Z

# 📜 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

If you use it, please cite us:

```bibtex
@misc{Blendgen,
  author = {Raccoon Research},
  title = {Blendgen: A Synthetic Data Generator for Video Caption Pairs},
  year = {2024},
  publisher = {GitHub},
  howpublished = {\url{https://github.com/RaccoonResearch/blendgen}}
}
```
