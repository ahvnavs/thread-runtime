# THREAD — STORY I / PART 1: VISUAL REFERENCE MATRIX & RECONCILIATION AUDIT

**TITLE**: *THE SACRIFICE OF IPHIGENIA: ECHOES AT AULIS*  
**CANONICAL NARRATIVE SOURCE**: `story/story_I/part_1/screenplay/SCREENPLAY.md`  
**STATUS**: AUTHORITATIVE VISUAL REFERENCE SPECIFICATION  
**USAGE NOTICE**: All external references are RESEARCH ONLY (`PRODUCTION_USE = REFERENCE_ONLY`). No third-party media is directly downloaded or embedded as runtime assets.  

---

## 1. RECONCILIATION & DISCREPANCY AUDIT

This audit reconciles the master screenplay (`SCREENPLAY.md`) against runtime configuration (`story.json`).

| Shot ID | Screenplay Time Range | Screenplay Dialogue / Narration | Runtime Subtitle Text (`story.json`) | Status / Reconciliation Directive |
| :--- | :--- | :--- | :--- | :--- |
| `shot_001` | `00:00.000 – 00:06.000` | *None* | "At Aulis, the winds died. A thousand ships lay motionless upon a stagnant sea." | **Flagged Discrepancy**: Screenplay specifies pure ambient stillness; runtime includes opening narration. Visual state remains locked to Screenplay Action (limp banners, glass sea). |
| `shot_002` | `00:06.000 – 00:12.000` | *None* | "The army rotted in the sun. Agamemnon watched from the high prow of his flagship." | **Flagged Discrepancy**: Screenplay specifies silent character tracking; runtime includes narration beat. Agamemnon visual framing matches Screenplay tracking spec. |
| `shot_003` | `00:12.000 – 00:18.000` | *None* | "Iphigenia walked toward the granite altar, her white linen robe trailing across dust." | **Flagged Discrepancy**: Narration occurs over Iphigenia's push-in approach. Visual robe and altar framing driven by Screenplay. |
| `shot_004` | `00:18.000 – 00:24.000` | Agamemnon: *"Forgive me... the winds demand their toll."* | "Her eyes held no fear—only the weight of a decree born before her birth." | **CRITICAL DISCREPANCY**: Screenplay specifies Agamemnon spoken line; `story.json` contains descriptive narration. **Directive**: Visual animation follows Screenplay (head turn, shadow over eyes, minimal mouth movement on spoken line). |
| `shot_005` | `00:24.000 – 00:30.000` | *None* | "A king who traded his daughter for a breeze to Troy." | **Flagged Discrepancy**: Close-up hand on rune is silent in Screenplay; `story.json` places narration here. Hand touch and gold illumination driven by Screenplay. |
| `shot_006` | `00:30.000 – 00:36.000` | Kaelen: *"The sacrifice was never forgotten."* | "[TEMPORAL MATCH CUT] Three thousand years later..." | **CRITICAL DISCREPANCY**: Screenplay specifies Kaelen spoken line; `story.json` includes temporal subtitle marker. Match cut geometry `(180, 120)` driven strictly by Screenplay. |
| `shot_007` | `00:36.000 – 00:42.000` | *None* | "Kaelen's hand touched the glowing cyan conduit of Aulis-9." | Visual face emergence from total darkness driven by Screenplay eye illumination spec. |
| `shot_008` | `00:42.000 – 00:48.000` | *None* | "An orbital core waiting for an identical sacrifice." | Visual dual release (sails snapping taut + engine plume) driven by Screenplay. |
| `shot_009` | `00:48.000 – 00:54.000` | *None* | "The thread connects what time separates." | Moonlit ocean fleet formation driven by Screenplay wide 35mm spec. |
| `shot_010` | `00:54.000 – 01:00.000` | *None* | "The wind begins to rise." | Final rune floating in space fading to black driven by Screenplay. |

---

## 2. VISUAL REFERENCE MATRIX (SHOT 001 – SHOT 010)

### SHOT 001 — AULIS STILLNESS
* **REFERENCE_ID**: `REF_001_A` | **SHOT_ID**: `shot_001` | **CATEGORY**: A. Real-world grounding / H. Palette
  * **SOURCE_PLATFORM**: Unsplash / Aegean Dusk Landscape Photography
  * **SOURCE_URL**: `https://unsplash.com/search/photos/aegean-sunset` (Research Search Target)
  * **WHAT_TO_STUDY**: Horizon atmospheric layering, water reflectivity under twilight, violet-purple atmospheric haze.
  * **COMPOSITION_PRINCIPLE**: Horizon at lower 40%; massive 40% indigo sky; flat sea surface.
  * **LIGHTING_PRINCIPLE**: Desaturated twilight key with burnt-orange horizon accent (`#DC641E`).
  * **PALETTE_PRINCIPLE**: Sky `#19143C`, horizon `#DC641E`, sea `#0C101C`.
  * **PIXEL_TRANSLATION**: Bayer 4x4 matrix gradient for sky fog; mountains reduced to 2 horizontal tone bands.
  * **LICENSE/USAGE_STATUS**: Public research reference (`PRODUCTION_USE = REFERENCE_ONLY`).
* **REFERENCE_ID**: `REF_001_B` | **SHOT_ID**: `shot_001` | **CATEGORY**: G. Pixel-art technique / I. Motion
  * **SOURCE_PLATFORM**: Demoscene Landscape References
  * **SOURCE_URL**: `UNRESOLVED: demoscene_stagnant_water_palette_drift`
  * **WHAT_TO_STUDY**: Restrained 1-pixel luminance shifting for motionless glass sea.
  * **COMPOSITION_PRINCIPLE**: Extreme wide framing where human elements are tiny (8–12px).
  * **LIGHTING_PRINCIPLE**: Uniform dark exposure with low contrast.
  * **PALETTE_PRINCIPLE**: 4-color sea value step.
  * **PIXEL_TRANSLATION**: 1-pixel sea luminance drift calculated via frame bitwise operator.
  * **LICENSE/USAGE_STATUS**: Research reference (`PRODUCTION_USE = REFERENCE_ONLY`).

---

### SHOT 002 — AGAMEMNON / BURDEN
* **REFERENCE_ID**: `REF_002_A` | **SHOT_ID**: `shot_002` | **CATEGORY**: E. Character/anatomy / F. Material
  * **SOURCE_PLATFORM**: Archaeological Museum Collections / Classical Hellenic Armor
  * **SOURCE_URL**: `UNRESOLVED: hellenic_bronze_breastplate_musculata`
  * **WHAT_TO_STUDY**: Antique bronze surface patination, breastplate muscle contouring, heavy wool cloak drape.
  * **COMPOSITION_PRINCIPLE**: Character occupies 18–20% frame height at left third; right 70% open horizon.
  * **LIGHTING_PRINCIPLE**: Sunset rim light highlighting armor edge; low key face shadow.
  * **PALETTE_PRINCIPLE**: Slate armor `#2D2A32`, antique bronze `#D4AC0D`.
  * **PIXEL_TRANSLATION**: 2–3 specular bronze highlight clusters; face defined by dark shadow, grey beard, and 1 eye pixel.
  * **LICENSE/USAGE_STATUS**: Archaeological research reference (`PRODUCTION_USE = REFERENCE_ONLY`).
* **REFERENCE_ID**: `REF_002_B` | **SHOT_ID**: `shot_002` | **CATEGORY**: B. Cinematic composition / I. Motion
  * **SOURCE_PLATFORM**: Cinematic Framing References (70mm Masterworks)
  * **SOURCE_URL**: `UNRESOLVED: cinematic_tracking_shot_flagship_prow`
  * **WHAT_TO_STUDY**: Parallax separation between foreground deck rail and background sea horizon.
  * **COMPOSITION_PRINCIPLE**: Slow horizontal tracking left-to-right (0.1px/frame).
  * **LIGHTING_PRINCIPLE**: High contrast rim light against dark sky.
  * **PALETTE_PRINCIPLE**: Indigo sky, slate timber, bronze metal.
  * **PIXEL_TRANSLATION**: 3-layer z-index composition (`z=0` sea, `z=10` rail, `z=20` character).
  * **LICENSE/USAGE_STATUS**: Research reference (`PRODUCTION_USE = REFERENCE_ONLY`).

---

### SHOT 003 — IPHIGENIA / APPROACH
* **REFERENCE_ID**: `REF_003_A` | **SHOT_ID**: `shot_003` | **CATEGORY**: D. Architecture / E. Character
  * **SOURCE_PLATFORM**: Archaeological Photography / Temple of Artemis at Brauron
  * **SOURCE_URL**: `UNRESOLVED: temple_of_artemis_granite_altar_steps`
  * **WHAT_TO_STUDY**: Granite altar step geometry, brazier fire shadow patterns, chiton drapery folds.
  * **COMPOSITION_PRINCIPLE**: Asymmetric framing (Iphigenia at X=35%) advancing toward massive right-side altar pillar.
  * **LIGHTING_PRINCIPLE**: Dual light source: cold twilight sky (`#371C42`) vs warm golden brazier flame (`#B7950B`).
  * **PALETTE_PRINCIPLE**: Linen white `#FFFFFF`, amber fire `#B7950B`, twilight purple `#371C42`.
  * **PIXEL_TRANSLATION**: Linen robe shaded with cool purple shadows and warm amber highlight pixels.
  * **LICENSE/USAGE_STATUS**: Research reference (`PRODUCTION_USE = REFERENCE_ONLY`).

---

### SHOT 004 — AGAMEMNON / GUILT
* **REFERENCE_ID**: `REF_004_A` | **SHOT_ID**: `shot_004` | **CATEGORY**: C. Lighting / E. Character
  * **SOURCE_PLATFORM**: Classical Fine Art / Low-Key Portraiture (Rembrandt/Caravaggio)
  * **SOURCE_URL**: `UNRESOLVED: low_key_chiaroscuro_head_turn_shadow`
  * **WHAT_TO_STUDY**: Deep shadow obscuring eyes upon head turn; single specular highlight extinction.
  * **COMPOSITION_PRINCIPLE**: Medium close-up centered; background 90% dark altar terrace.
  * **LIGHTING_PRINCIPLE**: Chiaroscuro key light falling off rapidly into dark indigo shadow (`#08060F`).
  * **PALETTE_PRINCIPLE**: Indigo `#19143C`, shadow black `#08060F`.
  * **PIXEL_TRANSLATION**: Eye highlight pixel turns off at F468; head turn executed over 36 frames.
  * **LICENSE/USAGE_STATUS**: Fine art research reference (`PRODUCTION_USE = REFERENCE_ONLY`).

---

### SHOT 005 — HAND / RUNE / CHOICE (PRIMARY MASTERPIECE TEST — PART 1)
* **REFERENCE_ID**: `REF_005_A` | **SHOT_ID**: `shot_005` | **CATEGORY**: F. Material / G. Pixel-art technique
  * **SOURCE_PLATFORM**: Epigraphic Inscription Collections / Gold Inlay Stone Carvings
  * **SOURCE_URL**: `UNRESOLVED: ancient_granite_rune_gold_inlay`
  * **WHAT_TO_STUDY**: Relief channel carving in dark granite; gold leaf specular illumination.
  * **COMPOSITION_PRINCIPLE**: Extended hand from bottom-left to center-right contact point `(180, 120)`.
  * **LIGHTING_PRINCIPLE**: Dark granite face illuminated solely by progressive gold rune emission (`#E6B800`).
  * **PALETTE_PRINCIPLE**: Granite gray `#26202D`, rune gold `#E6B800`, skin tone `#D29173`.
  * **PIXEL_TRANSLATION**: Progressive rune activation: 1 contact pixel at F612 -> channel spread over 70 frames.
  * **LICENSE/USAGE_STATUS**: Research reference (`PRODUCTION_USE = REFERENCE_ONLY`).

---

### SHOT 006 — MATCH CUT / KAELEN (PRIMARY MASTERPIECE TEST — PART 2)
* **REFERENCE_ID**: `REF_006_A` | **SHOT_ID**: `shot_006` | **CATEGORY**: B. Composition / D. Architecture / G. Pixel-art
  * **SOURCE_PLATFORM**: Demoscene Cyberpunk & Vector Interfaces
  * **SOURCE_URL**: `UNRESOLVED: cybernetic_conduit_cyan_interface_match_cut`
  * **WHAT_TO_STUDY**: High-contrast bioluminescent cyan interfaces against obsidian void black.
  * **COMPOSITION_PRINCIPLE**: **EXACT GEOMETRIC MATCH CUT**: Cybernetic hand touches cyan conduit at `(180, 120)`.
  * **LIGHTING_PRINCIPLE**: Instantaneous palette snap from Gold `#E6B800` to Electric Cyan `#00E5FF` at F720.
  * **PALETTE_PRINCIPLE**: Obsidian black `#020617`, electric cyan `#00E5FF`, metallic silver `#8A9BBO`.
  * **PIXEL_TRANSLATION**: Hand contour silhouette matches Shot 005; cyan pixels illuminate panel conduits.
  * **LICENSE/USAGE_STATUS**: Research reference (`PRODUCTION_USE = REFERENCE_ONLY`).

---

### SHOT 007 — EYES / AWAKENING
* **REFERENCE_ID**: `REF_007_A` | **SHOT_ID**: `shot_007` | **CATEGORY**: C. Lighting / G. Pixel-art technique
  * **SOURCE_PLATFORM**: High-Contrast Cyberpunk Pixel Portraiture
  * **SOURCE_URL**: `UNRESOLVED: cybernetic_portrait_glowing_eyes_shadow`
  * **WHAT_TO_STUDY**: Selective facial light emission; cybernetic temple seam illumination against void black.
  * **COMPOSITION_PRINCIPLE**: Close-up portrait where 90% of frame is total darkness (`#020617`).
  * **LIGHTING_PRINCIPLE**: Self-illuminating cyan irises (`#00E5FF`) and emerald temple seam (`#5DED2F`).
  * **PALETTE_PRINCIPLE**: Void black `#020617`, cyan `#00E5FF`, emerald `#5DED2F`.
  * **PIXEL_TRANSLATION**: 1 cyan pixel at F864 -> iris cluster at F900 -> temple seam line at F936.
  * **LICENSE/USAGE_STATUS**: Research reference (`PRODUCTION_USE = REFERENCE_ONLY`).

---

### SHOT 008 — DUAL RELEASE
* **REFERENCE_ID**: `REF_008_A` | **SHOT_ID**: `shot_008` | **CATEGORY**: A. Real-world / I. Motion
  * **SOURCE_PLATFORM**: Nautical Photography & Space Launch Imaging (NASA/Unsplash)
  * **SOURCE_URL**: `https://unsplash.com/search/photos/rocket-launch-thruster` (Research Search Target)
  * **WHAT_TO_STUDY**: Billowing canvas sail snapping in gale wind vs rocket engine plume particle physics.
  * **COMPOSITION_PRINCIPLE**: Dual-era split composition: sails below, starship thrusters above.
  * **LIGHTING_PRINCIPLE**: Maximum brightness flare with intense specular highlights.
  * **PALETTE_PRINCIPLE**: Deep blue `#0055FF`, white canvas `#FFFFFF`, cyan thruster `#00E5FF`.
  * **PIXEL_TRANSLATION**: Canvas snaps from limp to taut over 35 frames; 2-pixel sea spray & star particles drift.
  * **LICENSE/USAGE_STATUS**: NASA/Public domain research reference (`PRODUCTION_USE = REFERENCE_ONLY`).

---

### SHOT 009 — FLEET / DESTINY
* **REFERENCE_ID**: `REF_009_A` | **SHOT_ID**: `shot_009` | **CATEGORY**: B. Composition / F. Material
  * **SOURCE_PLATFORM**: Classical Marine Painting & Moonlight Photography
  * **SOURCE_URL**: `UNRESOLVED: moonlit_naval_fleet_formation_night`
  * **WHAT_TO_STUDY**: Moonlight glint on rolling ocean waves, scale reduction across multi-ship fleet.
  * **COMPOSITION_PRINCIPLE**: Wide 35mm composition with 3 depth tiers (foreground, midground, background clusters).
  * **LIGHTING_PRINCIPLE**: Cold moonlight silver key (`#D0D8E8`) casting long water glint trails.
  * **PALETTE_PRINCIPLE**: Moonlight silver `#D0D8E8`, deep ocean `#09101D`.
  * **PIXEL_TRANSLATION**: Foreground ship 40px height; midground 15px; background 2–4px clusters.
  * **LICENSE/USAGE_STATUS**: Fine art research reference (`PRODUCTION_USE = REFERENCE_ONLY`).

---

### SHOT 010 — RUNE / MYSTERY
* **REFERENCE_ID**: `REF_010_A` | **SHOT_ID**: `shot_010` | **CATEGORY**: A. Real-world / H. Palette
  * **SOURCE_PLATFORM**: Hubble / James Webb Space Telescope Public Archives
  * **SOURCE_URL**: `https://images.nasa.gov/details-PIA23647` (NASA Public Space Photography)
  * **WHAT_TO_STUDY**: Deep space nebula gas filaments, extreme cosmic scale contrast.
  * **COMPOSITION_PRINCIPLE**: 85% void black; small nebula at center-right; floating cyan rune at center.
  * **LIGHTING_PRINCIPLE**: Soft nebular luminescence surrounding high-intensity cyan rune emission.
  * **PALETTE_PRINCIPLE**: Void black `#020617`, cyan rune `#00E5FF`, magenta nebula `#4A0E35`.
  * **PIXEL_TRANSLATION**: Rune fades in over 36 frames, holds, then dissolves into total blackness.
  * **LICENSE/USAGE_STATUS**: NASA Public Domain reference (`PRODUCTION_USE = REFERENCE_ONLY`).

---
**[END OF VISUAL REFERENCE MATRIX]**
