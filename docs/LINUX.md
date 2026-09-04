# THREAD Runtime — Linux Installation & Execution Guide

---

## 1. SYSTEM REQUIREMENTS

* **Operating System**: Linux (Ubuntu 22.04+, Debian 12+, or Fedora 38+)
* **Python**: Python 3.10+ (Python 3.14 recommended)
* **Processor**: Intel Core i5 / AMD Ryzen 5 or better
* **RAM**: 4 GB RAM minimum (16 GB recommended)
* **Graphics**: Integrated Graphics (Intel Iris Xe / AMD Radeon) or dedicated GPU

---

## 2. QUICK START (CLONE & PLAY)

```bash
# 1. Clone the repository
git clone https://github.com/user/thread-runtime.git
cd thread-runtime

# 2. Create virtual environment & install dependencies
python3 -m venv .venv
source .venv/bin/python -m pip install -e .

# 3. Launch Story I — Part 1
./thread play story_I/part_1
```

Alternatively:

```bash
python3 -m thread_runtime story/story_I/part_1/story.json
```

---

## 3. OFFLINE VERIFICATION PROCEDURE

The THREAD runtime operates 100% offline without network dependencies:

```bash
# Disable networking or disconnect interface
sudo ip link set dev eth0 down

# Run Story I — Part 1
./thread play story_I/part_1
```

All story data, assets, audio, and subtitles resolve locally from `story/story_I/part_1/`.
