# THREAD — CINEMATIC PIXELATED BITWISE LEGO MACHINE ARCHITECTURE

**CREATIVE & TECHNICAL NORTH STAR**:
> *"THREAD is a code-driven cinematic pixel world where authored visual 'bricks' are assembled, transformed, lit, and animated at bit/raster level to produce a film rather than a game."*  
> *"A cinematic pixelated bitwise Lego machine for storytelling."*

---

## 1. THE BRICK VOCABULARY

THREAD treats every visual, spatial, and temporal element as a composable, modular building block ("Brick"):

```text
🧱 Pixel Bricks      — Authored raster primitives (characters, rocks, flagship prows, monoliths, stars)
🧩 Bitwise Bricks    — Binary masks, ordered dithering, bitwise XOR patterns, palette remapping
🪟 Layer Bricks      — Z-ordered compositing planes (Background / Midground / Subject / Foreground / Atmosphere)
💡 Light Bricks      — Additive light masks, specular highlights, emissive runes, shadow falloff
🌊 Motion Bricks     — Ocean wave cycles, robe drapery shifts, thruster particles, subpixel camera velocity
🎨 Palette Bricks    — Strict 32-color indexed palettes with deterministic index shifting
🎥 Camera Bricks     — Tracking, pan, push-in, subpixel offsets, framing boundaries
⏱️ Timeline Bricks   — Integer microsecond timeline coordinates (timestamp_us) at 24.0 FPS
🔊 Audio Bricks      — Subtextual voice, ambient drones, SFX, orchestral cues locked to timeline
🔗 Transition Bricks — 1-frame spatial match cuts, palette snaps, bitwise mask transformations
```

---

## 2. THE ABSTRACT HIERARCHY

### Level 1: Brick (Authored Visual Primitive)
A **Brick** is the fundamental, reusable building block created by human art direction:
```text
Brick
├── identity (brick_id, name, semantic_category)
├── raster_data (426x240 PNG layer / sprite)
├── palette (32-color indexed palette map)
├── mask (binary alpha / bitwise pattern mask)
├── anchor (x, y coordinate)
├── transform (scale, rotation, opacity)
├── animation (pose_000, pose_001, pose_002 frame states)
├── material (granite, linen, bronze, obsidian, cyan_conduit)
└── provenance (creator, status: ORIGINAL_ART)
```

### Level 2: Shot (Composition & Orchestration)
A **Shot** assembles bricks, camera instructions, lighting masks, and temporal rules:
```text
Shot
├── shot_id
├── duration_us
├── bricks [background.brick, altar.brick, character.brick, hand.brick, rune.brick]
├── layers [z_index 0 .. 60]
├── camera (start_pan, end_pan, camera_duration_us)
├── lighting (light_mask, emissive_color, intensity_curve)
├── bitwise_effects (dithering_matrix, scanline_mask, palette_snap)
├── audio_events [audio_id, start_us, end_us, source]
└── subtitle_cues [cue_id, start_us, end_us, text]
```

### Level 3: Film (Unified Master Narrative)
A **Film** orchestrates all shots across the canonical integer microsecond timeline:
```text
Film
├── film_id
├── title
├── canonical_timeline (timestamp_us, frame_rate: 24)
├── shots [shot_001 .. shot_010]
├── master_audio_track
├── master_subtitle_track
└── metadata (screenplay_source, provenance_manifest)
```

---

## 3. THE BITWISE COMPOSITING PIPELINE

```text
AUTHORED BRICKS (Pixel & Mask Primitives)
                  │
                  ▼
         CANONICAL TIMELINE (Frame Index n ➔ timestamp_us)
                  │
                  ▼
         LAYER COMPOSITOR (Z-Sorting & Subpixel Camera Pan Offset)
                  │
                  ▼
      BITWISE MASK & PALETTE PIPELINE
        ├─ pixel_index = palette[base_index + light_shift]
        ├─ mask = hand_mask & light_mask
        ├─ dither = (x ^ y ^ frame_index) & 7
        └─ match_cut_snap = gold_rune ➔ cyan_conduit
                  │
                  ▼
      426 × 240 INTERNAL CANVAS (Integer Resolution)
                  │
                  ▼
      1280 × 720 DISPLAY PRESENTATION (3x Integer Nearest-Neighbor Scale)
```

---

## 4. PRODUCTION PRINCIPLE

```text
Human / Art Direction  ──► Creates authored Lego Bricks (Hand, Sleeve, Altar, Rune, Cyber Plating)
Code Engine            ──► Assembles, lights, transforms, and compositing Bricks at bitwise level
Canonical Timeline     ──► Conducts exact 24 FPS frame execution via timestamp_us
Camera System          ──► Films the assembled composition
Audio System           ──► Breathes naturalistic sound into the scene
The Audience           ──► Experiences Nolan-level cinematic filmmaking translated to pixel art
```
