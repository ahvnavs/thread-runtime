# THREAD — Code-Driven Cinematic Game Runtime

THREAD is a **Linux-runnable, code-driven cinematic game runtime**. It behaves technically like a lightweight 2D game engine, but its primary experience is a **long, authored cinematic cutscene** rather than gameplay.

---

## Story I — Part 1: The Aulis Strand

The repository includes **Story I — Part 1**, featuring the tragic sacrifice at ancient Aulis linked through temporal match cuts to the far-future orbital core of Aulis-9.

---

## Installation & Launch

```bash
# Clone repository
git clone https://github.com/user/thread-runtime.git
cd thread-runtime

# Setup virtual environment
python3 -m venv .venv
source .venv/bin/activate
pip install -e .

# Launch Story I — Part 1
./thread play story_I/part_1
```

For detailed Linux installation steps and offline verification, see [`docs/LINUX.md`](file:///Ubuntu-26.04/home/ahvnav/projects/thread-runtime/docs/LINUX.md).

---

## Technical Specifications

* **Resolution**: 1280x720 720p HD (Native 426x240 internal pixel canvas upscaled 3x)
* **Frame Rate**: 24.0 fps deterministic timeline playback
* **Rendering**: Code-driven pixel/raster renderer with Bayer 4x4 ordered dithering & bitwise scanline modulation
* **Dependencies**: Python standard library, NumPy, Pillow, FFmpeg (100% Free, Local & Offline)
* **Recurring Cost**: ₹0.00 (Zero)
