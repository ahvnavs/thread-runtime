# THREAD Runtime — Production Contract & Specification

**Document Version**: 1.0.0  
**Status**: FROZEN / STABLE BASELINE  
**Effective Build**: Cycle 7 Production Gate  

---

## 1. Executive Overview

THREAD Runtime is a portable, offline-first cinematic story runtime. It separates authored narrative data, cinematic timeline specifications, and 2D/3D presentation from executable runtime infrastructure.

THREAD is **not a game engine**. It does not support combat, health, XP, quests, progression, RPG mechanics, skill trees, or game AI.

---

## 2. Architecture & Layer Separation

```text
                    STORY PACKAGE (.threadpkg)
                                │
              ┌─────────────────┴─────────────────┐
              │                                   │
       Narrative Model                     Cinematic Model
       (Scenes, Choices, State)            (Shots, Camera, Cues, Transitions)
              │                                   │
              └─────────────────┬─────────────────┘
                                │
                        Runtime Scheduler
                       (CinematicTimeline)
                                │
                       Presenter / Renderer
                       (2D Compositor / Web)
                                │
              ┌─────────────────┴─────────────────┐
              │                                   │
           Visual                               Audio
         (H.264 Video)                       (AAC Audio)
              │                                   │
              └─────────────────┬─────────────────┘
                                │
                      Final Release Artifact
                    (Self-Contained Audiovisual MP4)
```

---

## 3. Core Technical Guarantees

1. **Zero Runtime External Cloud Dependencies**: Playback executes 100% offline without API calls, network sockets, cloud inference, or telemetry.
2. **Deterministic Timeline Execution**: Integer millisecond precise event scheduling (`delta_ms`).
3. **Data-Only Specification**: Zero `eval()`, `exec()`, lambda functions, or dynamic Python code execution from story data files.
4. **Isolated Path Operations**: Package unpacking enforces Zip Slip protection preventing directory traversal outside the target output path.
5. **Asset Provenance Enforcement**: Releases require explicit asset tracking (`ORIGINAL`, `PUBLIC_DOMAIN`, `OPEN_LICENSE`, `GENERATED`). Unverified assets (`UNKNOWN`, `REJECTED`) block release packaging.

---

## 4. Audiovisual Output Contract

* **Container**: MPEG-4 (.mp4)
* **Video Codec**: H.264 (libx264)
* **Audio Codec**: AAC (Advanced Audio Coding)
* **Resolution**: 1280x720 (720p HD Baseline)
* **Frame Rate**: 24.0 fps
* **Audio Sample Rate**: 44,100 Hz (Stereo 16-bit PCM source mixed to AAC)
* **Duration Tolerance**: Exact millisecond match to `CinematicScene.duration_ms`.

---

## 5. CLI Interface Contract

* `thread doctor` — Environment, resource, and media tool diagnostics.
* `thread info <story>` — Inspects story metadata and scene counts.
* `thread validate <story>` — Validates schema, referential integrity, and reachability.
* `thread pack <story> <output.threadpkg>` — Bundles story into archive.
* `thread unpack <package.threadpkg> <dest>` — Safely extracts archive.
* `thread inspect <package.threadpkg>` — Inspects manifest and contents.
* `thread cinematic-info <story>` — Inspects cinematic shot timelines.
* `thread cinematic-validate <story>` — Validates cinematic timing and match-cut targets.
* `thread timeline <story> [scene_id]` — Outputs deterministic debug authoring view.
* `thread render <story> [--output path]` — Renders audiovisual MP4 video.
* `thread release <story> [--output-dir path]` — Executes production release gate.

---

## 6. Versioning Rules

* **Runtime Version**: `0.1.0` (Semantic Versioning `MAJOR.MINOR.PATCH`).
* **Package Format Version**: `1.0`.
* **Schema Version**: `1.0`.
* Story package updates do not require runtime version bumps unless package format schema changes.
