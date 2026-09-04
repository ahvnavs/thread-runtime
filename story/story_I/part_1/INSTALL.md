# INSTALLATION & CUSTOMER PLAYBACK GUIDE

## Customer Package Architecture
The THREAD Story Package (`.threadpkg`) is a 100% self-contained zip archive containing:
1. `manifest.json` (SHA-256 integrity digest)
2. `story.json` (Branching story package & cinematic scene timeline)
3. `media/audiovisual.mp4` (Self-contained H.264 video + 44.1kHz AAC stereo audio master)
4. `subtitles/english.vtt` (WebVTT subtitle captions)
5. `manifests/scene_manifest.json` (Asset provenance audit registry)

No developer workspace paths, internet connection, or AI APIs are required.

## Playback Options

### Option 1: Direct Audiovisual MP4 Video
Open `release/story-i-part-1-aulis_audiovisual.mp4` (or extract `media/audiovisual.mp4` from `story-i-part-1-aulis.threadpkg`) in any standard media player (VLC, Windows Media Player, QuickTime).

### Option 2: Interactive HTML5 Browser Player
Open `release/playback/index.html` in any web browser.

### Option 3: THREAD CLI Runtime Engine
Extract package or run directly:
```bash
thread unpack story-i-part-1-aulis.threadpkg --dest customer_install/
thread info customer_install/story.json
thread play customer_install/story.json
```
