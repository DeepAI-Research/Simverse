# Simian
A synthetic data generator for video caption pairs.

<img src="docs/assets/simian_banner.png" style="width: 100%">

![docs](https://github.com/RaccoonResearch/simian/actions/workflows/mkdocs.yml/badge.svg)
![tests](https://github.com/RaccoonResearch/simian/actions/workflows/tests.yml/badge.svg)
[![License](https://img.shields.io/badge/License-MIT-blue)](https://github.com/RaccoonResearch/simian/blob/main/LICENSE)
[![stars](https://img.shields.io/github/stars/RaccoonResearch/simian?style=social)](https://github.com/RaccoonResearch/simian)
[![forks](https://img.shields.io/github/forks/RaccoonResearch/simian?style=social)](https://github.com/RaccoonResearch/simian)

Simian creates synthetic data that is usable for generative video and video captioning tasks. The data consists of videos and captions. The videos are generated using Blender, a 3D modeling software.

## ⚠️ Experimental Pre-Alpha

This project is in open development phase and is not ready for public use. Many things are still being actively developed for an initial release. Use at your own risk.

## 🖥️ Setup

### ⚠️ IMPORTANT: Simian requires Python 3.10 or lower to run.

1. Install Python 3.10. If you're on Linux, set it up with this <a href="https://gist.github.com/lalalune/986704a935d202ab2350ca90b2fc9755">gist</a>.


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

> **_NOTE:_**  Make sure you have [Blender](https://www.blender.org/download/) installed. 

You can generate individually:
```bash
# MacOS
# Download Blender for MacOS
/Applications/Blender.app/Contents/MacOS/Blender --background --python simian/render.py

# Linux
blender --background --python simian/render.py

## Kitchen sink
blender --background --python simian/render.py -- --width 1920 --height 1080 --combination_index 0 --output_dir ./renders --hdri_path ./backgrounds --start_frame 1 --end_frame 65
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

### Distributed rendering
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

If you want to use a custom or hosted Redis instance (recommended), you can add th redis details like this:
```bash
EXPORT REDIS_URL=<my_redis_url>
```

To run tests look into the test folder and run whichever test file you want

```bash
/Applications/Blender.app/Contents/MacOS/Blender --background --python object_test.py
```

## 📁 Datasets

We are currently using the following datasets:
[Objaverse](https://huggingface.co/datasets/allenai/objaverse)

Backgrounds are loaded from:
[Poly Haven](https://polyhaven.com)

## 🦝 Contributing

We welcome contributions! We're especially interested in help adding and refining datasets, improving generation quality, adding new features and dynamics and allowing the project to meet more use cases.

### How to contribute

1. Check out the issues <a href="https://github.com/RaccoonResearch/simian/issues">here</a>. 
2. Join our Discord <a href="https://discord.gg/JMfbmHdPNB">here</a>.
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

## Contributors ✨

<!-- ALL-CONTRIBUTORS-BADGE:START - Do not remove or modify this section -->
[![All Contributors](https://img.shields.io/badge/all_contributors-2-orange.svg?style=flat-square)](#contributors-)
<!-- ALL-CONTRIBUTORS-BADGE:END -->

This project follows the [all-contributors](https://github.com/all-contributors/all-contributors) specification. Contributions of any kind welcome!

<!-- ALL-CONTRIBUTORS-LIST:START - Do not remove or modify this section -->
<!-- prettier-ignore-start -->
<!-- markdownlint-disable -->
<table>
  <tbody>
    <tr>
      <td align="center" valign="top" width="14.28%"><a href="https://github.com/lalalune"><img src="https://avatars.githubusercontent.com/u/18633264?v=4?s=100" width="100px;" alt="M̵̞̗̝̼̅̏̎͝Ȯ̴̝̻̊̃̋̀Õ̷̼͋N̸̩̿͜ ̶̜̠̹̼̩͒"/><br /><sub><b>M̵̞̗̝̼̅̏̎͝Ȯ̴̝̻̊̃̋̀Õ̷̼͋N̸̩̿͜ ̶̜̠̹̼̩͒</b></sub></a><br /><a href="#infra-lalalune" title="Infrastructure (Hosting, Build-Tools, etc)">🚇</a> <a href="https://github.com/RaccoonResearch/Simian/commits?author=lalalune" title="Tests">⚠️</a> <a href="https://github.com/RaccoonResearch/Simian/commits?author=lalalune" title="Code">💻</a> <a href="https://github.com/RaccoonResearch/Simian/commits?author=eric-prog" title="Documentation">📖</a></td>
      <td align="center" valign="top" width="14.28%"><a href="https://ericsheen.tech/"><img src="https://avatars.githubusercontent.com/u/59460685?v=4?s=100" width="100px;" alt="Eric S"/><br /><sub><b>Eric S</b></sub></a><br /> <a href="https://github.com/RaccoonResearch/Simian/commits?author=eric-prog" title="Code">💻</a> <a href="https://github.com/RaccoonResearch/Simian/commits?author=eric-prog" title="Tests">⚠️</a> <a href="https://github.com/RaccoonResearch/Simian/commits?author=eric-prog" title="Documentation">📖</a></td>
    </tr>
  </tbody>
</table>

<!-- markdownlint-restore -->
<!-- prettier-ignore-end -->

<!-- ALL-CONTRIBUTORS-LIST:END -->

## Sponsors

<p style="text-align: center; margin-left: auto; margin-right: auto; max-width:800px;">
<center>Raccoon Research is sponsored by the following organizations:</center>
</p>
<p style="text-align: center; margin-left: auto; margin-right: auto; max-width:800px;">
<center><img src="docs/assets/DeepAI.png" width="200" alt="DeepAI" style="margin-left: auto; margin-right: auto;" /></center>
</p>
<p style="text-align: center; margin-left: auto; margin-right: auto; max-width:800px;">
<center>Interested in working with us? Join our <a href="https://discord.gg/JMfbmHdPNB">Discord</a> or post an <a href="https://github.com/RaccoonResearch/Simian/issues/new">issue</a> to get in touch.</center>
</p>