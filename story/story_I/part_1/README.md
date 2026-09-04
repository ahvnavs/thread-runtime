# STORY I — PART 1: THE SACRIFICE OF IPHIGENIA: ECHOES AT AULIS

Welcome to Story I — Part 1: **The Sacrifice of Iphigenia: Echoes at Aulis** (60.0-Second HD Master).

---

## Quick Start (Playing & Watching)

To validate and inspect the story package:
```bash
thread validate story/story_I/part_1/story_i_part_1.json
thread timeline story/story_I/part_1/story_i_part_1.json
```

To render the complete 60-second 720p HD audiovisual master MP4 video file:
```bash
thread render story/story_I/part_1/story_i_part_1.json --output story/story_I/part_1/render/story_i_part_1_master.mp4
```

To execute the full production release pipeline (creates self-contained `.threadpkg` customer package with embedded MP4 & WebVTT subtitles):
```bash
thread release story/story_I/part_1/story_i_part_1.json --output-dir story/story_I/part_1/release
```

---

## Directory Structure

* `MASTER_BIBLE.md` — Master canon, thematic premise, and temporal laws.
* `screenplay/SCREENPLAY.md` — Complete shot-oriented screenplay and shot list (10 shots, 60.0s).
* `characters/CHARACTER_BIBLES.md` — Character profiles, wants, needs, fears, and visual palettes.
* `research/CANON_AND_ADAPTATION.md` — Mythological audit and public domain provenance classification.
* `CHAIN_OF_TITLE.md` — Legal provenance registry and risk assessment.
* `QA_REPORT.md` — Formal cinematic review scorecard.
* `PRODUCTION_MANIFEST.json` — Machine-readable build and asset manifest.
* `story_i_part_1.json` — Runnable story package file.
* `assets/subtitles/english.vtt` — WebVTT subtitles.
