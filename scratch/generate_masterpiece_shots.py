import os
from PIL import Image, ImageDraw

def create_shot_005_layers(output_dir):
    os.makedirs(output_dir, exist_ok=True)
    width, height = 426, 240

    # 1. background.png - Dark Granite Altar Pillar
    bg = Image.new("RGBA", (width, height), (38, 32, 45, 255)) # #26202d
    draw_bg = ImageDraw.Draw(bg)
    # Draw granite block seams and subtle stone texture
    for y in range(0, height, 40):
        draw_bg.line([(0, y), (width, y)], fill=(25, 20, 30, 255), width=2)
    for x in range(0, width, 80):
        draw_bg.line([(x, 0), (x, height)], fill=(20, 16, 25, 255), width=1)
    bg.save(os.path.join(output_dir, "background.png"))

    # 2. subject.png - Gold Rune carved into Stone at (180, 120)
    sub = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    draw_sub = ImageDraw.Draw(sub)
    # Gold Rune Symbol centered around (180, 120)
    # Circle + Cross + Carved Channel Inlay
    draw_sub.ellipse([(160, 100), (200, 140)], outline=(230, 184, 0, 255), width=3) # Gold #e6b800
    draw_sub.line([(180, 85), (180, 155)], fill=(230, 184, 0, 255), width=3)
    draw_sub.line([(145, 120), (215, 120)], fill=(230, 184, 0, 255), width=3)
    draw_sub.line([(160, 100), (200, 140)], fill=(230, 184, 0, 255), width=2)
    # Bright center contact node at exactly (180, 120)
    draw_sub.rectangle([(178, 118), (182, 122)], fill=(255, 240, 150, 255))
    sub.save(os.path.join(output_dir, "subject.png"))

    # 3. foreground.png - Iphigenia's Extended Hand reaching to (180, 120)
    fg = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    draw_fg = ImageDraw.Draw(fg)
    # Arm extending from bottom-left (50, 240) to contact point (180, 120)
    # Robe sleeve
    draw_fg.polygon([(30, 240), (100, 240), (140, 150), (90, 170)], fill=(245, 245, 250, 255))
    # Hand and fingers touching (180, 120)
    draw_fg.polygon([(90, 170), (140, 150), (178, 120), (160, 140)], fill=(210, 145, 115, 255)) # Skin #d29173
    # Index finger reaching point (180, 120)
    draw_fg.line([(150, 132), (180, 120)], fill=(210, 145, 115, 255), width=3)
    fg.save(os.path.join(output_dir, "foreground.png"))

def create_shot_006_layers(output_dir):
    os.makedirs(output_dir, exist_ok=True)
    width, height = 426, 240

    # 1. background.png - Void Black Obsidian Monolith Structure
    bg = Image.new("RGBA", (width, height), (2, 6, 23, 255)) # Void black #020617
    draw_bg = ImageDraw.Draw(bg)
    # Metallic panel seams & dark tech grid
    for y in range(0, height, 30):
        draw_bg.line([(0, y), (width, y)], fill=(10, 20, 40, 255), width=1)
    for x in range(0, width, 60):
        draw_bg.line([(x, 0), (x, height)], fill=(10, 20, 40, 255), width=1)
    bg.save(os.path.join(output_dir, "background.png"))

    # 2. subject.png - Electric Cyan Quantum Core Conduit at (180, 120) (Identical match geometry)
    sub = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    draw_sub = ImageDraw.Draw(sub)
    # Cyan Conduit Interface centered around (180, 120)
    draw_sub.ellipse([(160, 100), (200, 140)], outline=(0, 229, 255, 255), width=3) # Electric Cyan #00e5ff
    draw_sub.line([(180, 85), (180, 155)], fill=(0, 229, 255, 255), width=3)
    draw_sub.line([(145, 120), (215, 120)], fill=(0, 229, 255, 255), width=3)
    draw_sub.line([(160, 100), (200, 140)], fill=(0, 229, 255, 255), width=2)
    # Bright center cyan contact node at exactly (180, 120)
    draw_sub.rectangle([(178, 118), (182, 122)], fill=(220, 255, 255, 255))
    sub.save(os.path.join(output_dir, "subject.png"))

    # 3. foreground.png - Kaelen's Cybernetic Hand reaching to (180, 120) (Identical match geometry)
    fg = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    draw_fg = ImageDraw.Draw(fg)
    # Cybernetic Arm extending from bottom-left (50, 240) to contact point (180, 120)
    # Dark carbon-fiber sleeve
    draw_fg.polygon([(30, 240), (100, 240), (140, 150), (90, 170)], fill=(25, 30, 40, 255))
    # Cybernetic metallic hand
    draw_fg.polygon([(90, 170), (140, 150), (178, 120), (160, 140)], fill=(138, 155, 186, 255)) # Metallic silver #8a9bba
    # Cyber finger joint & contact line
    draw_fg.line([(150, 132), (180, 120)], fill=(0, 229, 255, 255), width=3) # Cyan glowing joints
    fg.save(os.path.join(output_dir, "foreground.png"))

if __name__ == "__main__":
    create_shot_005_layers("story/story_I/part_1/shots/shot_005")
    create_shot_006_layers("story/story_I/part_1/shots/shot_006")
    print("Masterpiece match cut layers generated successfully!")
