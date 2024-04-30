# blendgen
A synthetic data generator for video caption pairs.

https://github.com/RaccoonResearch/blendgen/assets/18633264/54346aa8-fde4-4c11-b210-52525082a650

Currently a work in progress <3 Watch this space for v0.1!

## 🖥️ Setup

1. Download Blender. If you're on Linux, set it up with this script:

```bash
bash install_blender_linux.sh
```

2. If you're on a headless Linux server, install Xorg and start it:

```bash
sudo apt-get install xserver-xorg -y && \
  sudo python3 start_x_server.py start
```

3. Install the Python dependencies. Note that Python >3.8 is required:

```bash
pip install -r requirements.txt && pip install -e .
```

4. Download the datasets:
```bash
./get_data.sh
```

## 📸 Usage

After setup, we can start to render objects using the `batch.py` script:

```bash
python3 batch.py
```

## Advanced usage

TODO: We will outline usage with tutorials here when ready.
