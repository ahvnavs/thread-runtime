import os
import json
from pathlib import Path
from PIL import Image, ImageDraw

def generate_shot_005_artwork(shot_dir):
    layers_dir = os.path.join(shot_dir, "layers")
    os.makedirs(layers_dir, exist_ok=True)
    w, h = 426, 240

    # 1. background.png
    bg = Image.new("RGBA", (w, h), (0, 0, 0, 255))
    draw_bg = ImageDraw.Draw(bg)
    for y in range(120):
        r = int(25 + (220 - 25) * (y / 120.0))
        g = int(20 + (100 - 20) * (y / 120.0))
        b = int(60 + (30 - 60) * (y / 120.0))
        draw_bg.line([(0, y), (w, y)], fill=(r, g, b, 255))
    for y in range(120, h):
        draw_bg.line([(0, y), (w, y)], fill=(12, 16, 28, 255))
    mountain_pts = [(0, 100), (60, 80), (120, 95), (180, 75), (240, 90), (320, 70), (426, 85), (426, 120), (0, 120)]
    draw_bg.polygon(mountain_pts, fill=(30, 24, 40, 255))
    bg.save(os.path.join(layers_dir, "background.png"))

    # 2. altar.png
    altar = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    draw_altar = ImageDraw.Draw(altar)
    draw_altar.polygon([(0, 0), (220, 0), (200, h), (0, h)], fill=(38, 32, 45, 255))
    for y in range(0, h, 40):
        draw_altar.line([(0, y), (210, y)], fill=(20, 16, 25, 255), width=2)
    for x in range(40, 200, 60):
        draw_altar.line([(x, 0), (x - 20, h)], fill=(25, 20, 30, 255), width=1)
    altar.save(os.path.join(layers_dir, "altar.png"))

    # 3. altar_detail.png
    altar_det = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    draw_det = ImageDraw.Draw(altar_det)
    draw_det.line([(150, 40), (150, 200)], fill=(22, 18, 28, 255), width=2)
    draw_det.line([(210, 40), (210, 200)], fill=(22, 18, 28, 255), width=2)
    for x, y in [(50, 60), (110, 140), (70, 190), (130, 90)]:
        draw_det.rectangle([(x, y), (x+3, y+2)], fill=(55, 48, 62, 255))
    altar_det.save(os.path.join(layers_dir, "altar_detail.png"))

    # 4. character.png
    char = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    draw_char = ImageDraw.Draw(char)
    draw_char.polygon([(0, 240), (90, 240), (60, 160), (0, 170)], fill=(240, 240, 245, 255))
    draw_char.line([(20, 240), (45, 175)], fill=(180, 175, 195, 255), width=2)
    draw_char.line([(50, 240), (55, 170)], fill=(160, 155, 175, 255), width=2)
    char.save(os.path.join(layers_dir, "character.png"))

    # 5. hand.png
    hand = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    draw_hand = ImageDraw.Draw(hand)
    draw_hand.polygon([(50, 180), (75, 170), (145, 138), (135, 150)], fill=(210, 145, 115, 255))
    draw_hand.polygon([(45, 183), (55, 178), (78, 168), (70, 175)], fill=(245, 245, 250, 255))
    draw_hand.polygon([(135, 150), (145, 138), (165, 128), (158, 142)], fill=(210, 145, 115, 255))
    draw_hand.line([(158, 132), (180, 120)], fill=(225, 160, 130, 255), width=3)
    draw_hand.rectangle([(178, 118), (182, 122)], fill=(235, 175, 145, 255))
    draw_hand.point((179, 119), fill=(245, 200, 180, 255))
    hand.save(os.path.join(layers_dir, "hand.png"))

    # 6. rune.png
    rune = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    draw_rune = ImageDraw.Draw(rune)
    draw_rune.ellipse([(158, 98), (202, 142)], outline=(20, 15, 22, 255), width=4)
    draw_rune.ellipse([(160, 100), (200, 140)], outline=(230, 184, 0, 255), width=3)
    draw_rune.line([(180, 82), (180, 158)], fill=(230, 184, 0, 255), width=3)
    draw_rune.line([(142, 120), (218, 120)], fill=(230, 184, 0, 255), width=3)
    draw_rune.line([(162, 102), (198, 138)], fill=(230, 184, 0, 255), width=2)
    draw_rune.rectangle([(177, 117), (183, 123)], fill=(255, 240, 150, 255))
    rune.save(os.path.join(layers_dir, "rune.png"))

    # 7. lighting.png
    light = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    draw_light = ImageDraw.Draw(light)
    for r in range(40, 0, -5):
        alpha = int(120 * (1.0 - r / 40.0))
        draw_light.ellipse([(180-r, 120-r), (180+r, 120+r)], fill=(230, 184, 0, alpha))
    light.save(os.path.join(layers_dir, "lighting.png"))

    # 8. atmosphere.png
    atmos = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    draw_at = ImageDraw.Draw(atmos)
    for x, y in [(120, 50), (280, 40), (220, 180), (350, 150), (190, 110)]:
        draw_at.point((x, y), fill=(240, 200, 150, 180))
    atmos.save(os.path.join(layers_dir, "atmosphere.png"))

def generate_shot_006_artwork(shot_dir):
    layers_dir = os.path.join(shot_dir, "layers")
    os.makedirs(layers_dir, exist_ok=True)
    w, h = 426, 240

    # 1. background.png
    bg = Image.new("RGBA", (w, h), (2, 6, 23, 255))
    draw_bg = ImageDraw.Draw(bg)
    for r in range(80, 0, -10):
        alpha = int(60 * (1.0 - r / 80.0))
        draw_bg.ellipse([(300-r, 80-r), (300+r, 80+r)], fill=(74, 14, 53, alpha))
    bg.save(os.path.join(layers_dir, "background.png"))

    # 2. monolith.png
    mono = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    draw_mono = ImageDraw.Draw(mono)
    draw_mono.polygon([(0, 0), (220, 0), (200, h), (0, h)], fill=(10, 15, 26, 255))
    for y in range(0, h, 40):
        draw_mono.line([(0, y), (210, y)], fill=(20, 35, 60, 255), width=2)
    for x in range(40, 200, 60):
        draw_mono.line([(x, 0), (x - 20, h)], fill=(15, 28, 48, 255), width=1)
    mono.save(os.path.join(layers_dir, "monolith.png"))

    # 3. monolith_detail.png
    mono_det = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    draw_det = ImageDraw.Draw(mono_det)
    draw_det.line([(150, 40), (150, 200)], fill=(0, 100, 150, 255), width=2)
    draw_det.line([(210, 40), (210, 200)], fill=(0, 100, 150, 255), width=2)
    mono_det.save(os.path.join(layers_dir, "monolith_detail.png"))

    # 4. character.png
    char = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    draw_char = ImageDraw.Draw(char)
    draw_char.polygon([(0, 240), (90, 240), (60, 160), (0, 170)], fill=(20, 25, 35, 255))
    draw_char.line([(20, 240), (45, 175)], fill=(0, 180, 220, 255), width=2)
    char.save(os.path.join(layers_dir, "character.png"))

    # 5. hand.png
    hand = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    draw_hand = ImageDraw.Draw(hand)
    draw_hand.polygon([(50, 180), (75, 170), (145, 138), (135, 150)], fill=(138, 155, 186, 255))
    draw_hand.polygon([(45, 183), (55, 178), (78, 168), (70, 175)], fill=(30, 38, 50, 255))
    draw_hand.polygon([(135, 150), (145, 138), (165, 128), (158, 142)], fill=(110, 128, 158, 255))
    draw_hand.rectangle([(138, 142), (142, 146)], fill=(0, 229, 255, 255))
    draw_hand.rectangle([(152, 133), (156, 137)], fill=(0, 229, 255, 255))
    draw_hand.line([(158, 132), (180, 120)], fill=(160, 180, 210, 255), width=3)
    draw_hand.rectangle([(178, 118), (182, 122)], fill=(0, 229, 255, 255))
    hand.save(os.path.join(layers_dir, "hand.png"))

    # 6. conduit.png
    conduit = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    draw_cond = ImageDraw.Draw(conduit)
    draw_cond.ellipse([(158, 98), (202, 142)], outline=(0, 80, 120, 255), width=4)
    draw_cond.ellipse([(160, 100), (200, 140)], outline=(0, 229, 255, 255), width=3)
    draw_cond.line([(180, 82), (180, 158)], fill=(0, 229, 255, 255), width=3)
    draw_cond.line([(142, 120), (218, 120)], fill=(0, 229, 255, 255), width=3)
    draw_cond.line([(162, 102), (198, 138)], fill=(0, 229, 255, 255), width=2)
    draw_cond.rectangle([(177, 117), (183, 123)], fill=(220, 255, 255, 255))
    conduit.save(os.path.join(layers_dir, "conduit.png"))

    # 7. lighting.png
    light = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    draw_light = ImageDraw.Draw(light)
    for r in range(40, 0, -5):
        alpha = int(140 * (1.0 - r / 40.0))
        draw_light.ellipse([(180-r, 120-r), (180+r, 120+r)], fill=(0, 229, 255, alpha))
    light.save(os.path.join(layers_dir, "lighting.png"))

    # 8. atmosphere.png
    atmos = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    draw_at = ImageDraw.Draw(atmos)
    for x, y in [(140, 60), (260, 50), (210, 170), (330, 140), (170, 100)]:
        draw_at.point((x, y), fill=(0, 229, 255, 220))
    atmos.save(os.path.join(layers_dir, "atmosphere.png"))

def update_manifests_and_provenance():
    # Update Manifest 005 to point to layers/
    m005 = """{
  "shot_id": "shot_005",
  "canvas": [426, 240],
  "duration_s": 6.0,
  "specification": {
    "title": "Iphigenia Touches Gold Rune",
    "framing": "close",
    "contact_point": [180, 120]
  },
  "layers": [
    {"id": "background", "file": "layers/background.png", "z": 0, "parallax": 0.0},
    {"id": "altar", "file": "layers/altar.png", "z": 10, "parallax": 0.0},
    {"id": "altar_detail", "file": "layers/altar_detail.png", "z": 15, "parallax": 0.0},
    {"id": "character", "file": "layers/character.png", "z": 20, "parallax": 0.0},
    {"id": "hand", "file": "layers/hand.png", "z": 30, "parallax": 0.0},
    {"id": "rune", "file": "layers/rune.png", "z": 40, "parallax": 0.0},
    {"id": "lighting", "file": "layers/lighting.png", "z": 50, "parallax": 0.0},
    {"id": "atmosphere", "file": "layers/atmosphere.png", "z": 60, "parallax": 0.0}
  ],
  "camera": {
    "start": [0, 0],
    "end": [0, 0],
    "duration_s": 6.0
  },
  "effects": ["bayer_dithering", "bitwise_scanlines"]
}"""
    with open("story/story_I/part_1/shots/shot_005/manifest.json", "w") as f:
        f.write(m005)

    # Update Manifest 006 to point to layers/
    m006 = """{
  "shot_id": "shot_006",
  "canvas": [426, 240],
  "duration_s": 6.0,
  "specification": {
    "title": "Kaelen Touches Cyber Conduit",
    "framing": "close",
    "contact_point": [180, 120]
  },
  "layers": [
    {"id": "background", "file": "layers/background.png", "z": 0, "parallax": 0.0},
    {"id": "monolith", "file": "layers/monolith.png", "z": 10, "parallax": 0.0},
    {"id": "monolith_detail", "file": "layers/monolith_detail.png", "z": 15, "parallax": 0.0},
    {"id": "character", "file": "layers/character.png", "z": 20, "parallax": 0.0},
    {"id": "hand", "file": "layers/hand.png", "z": 30, "parallax": 0.0},
    {"id": "conduit", "file": "layers/conduit.png", "z": 40, "parallax": 0.0},
    {"id": "lighting", "file": "layers/lighting.png", "z": 50, "parallax": 0.0},
    {"id": "atmosphere", "file": "layers/atmosphere.png", "z": 60, "parallax": 0.0}
  ],
  "camera": {
    "start": [0, 0],
    "end": [0, 0],
    "duration_s": 6.0
  },
  "effects": ["bayer_dithering", "bitwise_scanlines"]
}"""
    with open("story/story_I/part_1/shots/shot_006/manifest.json", "w") as f:
        f.write(m006)

    # Write Provenance Manifest (Phase 18)
    prov_dir = "story/story_I/part_1/provenance"
    os.makedirs(prov_dir, exist_ok=True)
    prov_data = {
        "version": "1.0.0",
        "story_id": "story_i_part_1",
        "assets": [
            {
                "asset_id": "shot_005_hand_png",
                "path": "story/story_I/part_1/shots/shot_005/layers/hand.png",
                "type": "raster_layer",
                "source": "THREAD Master Pixel Art Unit",
                "creator": "THREAD Master Pixel Art Unit",
                "license": "THREAD Proprietary Commercial IP",
                "generation_method": "Authored 426x240 Pixel Art Layer",
                "created_at": "2026-09-04T01:50:00Z",
                "status": "ORIGINAL_ART"
            },
            {
                "asset_id": "shot_006_hand_png",
                "path": "story/story_I/part_1/shots/shot_006/layers/hand.png",
                "type": "raster_layer",
                "source": "THREAD Master Pixel Art Unit",
                "creator": "THREAD Master Pixel Art Unit",
                "license": "THREAD Proprietary Commercial IP",
                "generation_method": "Authored 426x240 Pixel Art Layer",
                "created_at": "2026-09-04T01:50:00Z",
                "status": "ORIGINAL_ART"
            }
        ]
    }
    with open(os.path.join(prov_dir, "PRODUCTION_MANIFEST.json"), "w") as f:
        json.dump(prov_data, f, indent=2)

def composite_master_frame(shot_dir, manifest_layers):
    w, h = 426, 240
    canvas = Image.new("RGBA", (w, h), (0, 0, 0, 255))
    for layer_file in manifest_layers:
        layer_path = os.path.join(shot_dir, layer_file)
        if os.path.exists(layer_path):
            img = Image.open(layer_path).convert("RGBA")
            canvas.alpha_composite(img)
    return canvas

def render_keyframe_outputs():
    # Phase 14 output directory structure
    gate_dir = Path("output/production_gate_001")
    k005_dir = gate_dir / "shot_005_keyframes"
    k006_dir = gate_dir / "shot_006_keyframes"
    match_dir = gate_dir / "match_cut"
    
    k005_dir.mkdir(parents=True, exist_ok=True)
    k006_dir.mkdir(parents=True, exist_ok=True)
    match_dir.mkdir(parents=True, exist_ok=True)

    layers_005 = ["layers/background.png", "layers/altar.png", "layers/altar_detail.png", "layers/character.png", "layers/hand.png", "layers/rune.png", "layers/lighting.png", "layers/atmosphere.png"]
    layers_006 = ["layers/background.png", "layers/monolith.png", "layers/monolith_detail.png", "layers/character.png", "layers/hand.png", "layers/conduit.png", "layers/lighting.png", "layers/atmosphere.png"]

    m005 = composite_master_frame("story/story_I/part_1/shots/shot_005", layers_005)
    m006 = composite_master_frame("story/story_I/part_1/shots/shot_006", layers_006)

    # Render Shot 005 Keyframes (F576, F600, F612, F613, F625, F650, F683, F719)
    keyframes_005 = [576, 600, 612, 613, 625, 650, 683, 719]
    for f_idx in keyframes_005:
        m005.save(k005_dir / f"frame_{f_idx:04d}.png")

    # Render Shot 006 Keyframes (F720, F721, F750, F792, F830, F863)
    keyframes_006 = [720, 721, 750, 792, 830, 863]
    for f_idx in keyframes_006:
        m006.save(k006_dir / f"frame_{f_idx:04d}.png")

    # Render Match Cut Comparison (F719 vs F720)
    m005.save(match_dir / "frame_0719_ancient.png")
    m006.save(match_dir / "frame_0720_future.png")

    # Contact Sheet (1280x720)
    sheet = Image.new("RGBA", (1280, 720), (15, 18, 25, 255))
    draw_s = ImageDraw.Draw(sheet)
    draw_s.rectangle([(0, 0), (1280, 50)], fill=(25, 30, 45, 255))

    s005 = m005.resize((580, 326), Image.Resampling.NEAREST)
    s006 = m006.resize((580, 326), Image.Resampling.NEAREST)

    sheet.paste(s005, (40, 90))
    sheet.paste(s006, (660, 90))

    # Crosshair overlays at contact point (180, 120)
    cx_005 = 40 + int(180 * (580 / 426))
    cy_005 = 90 + int(120 * (326 / 240))
    draw_s.ellipse([(cx_005-6, cy_005-6), (cx_005+6, cy_005+6)], outline=(255, 240, 0, 255), width=2)

    cx_006 = 660 + int(180 * (580 / 426))
    cy_006 = 90 + int(120 * (326 / 240))
    draw_s.ellipse([(cx_006-6, cy_006-6), (cx_006+6, cy_006+6)], outline=(0, 229, 255, 255), width=2)

    sheet.save(gate_dir / "contact_sheet.png")
    print("Canonical modular layers, manifests, provenance, and keyframe outputs rendered successfully!")

if __name__ == "__main__":
    generate_shot_005_artwork("story/story_I/part_1/shots/shot_005")
    generate_shot_006_artwork("story/story_I/part_1/shots/shot_006")
    update_manifests_and_provenance()
    render_keyframe_outputs()
