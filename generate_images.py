"""
Beautiful Image Generator for Spanish Learning Videos
Uses ONE pre-made background image for all phrases
"""

import os
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

# Image dimensions
IMAGE_WIDTH = 1080
IMAGE_HEIGHT = 1920

# Background image path
BACKGROUND_IMAGE = Path("background.png")


def create_default_background():
    """
    Create a beautiful default gradient background if none exists
    This only runs ONCE to create the background image
    """
    
    img = Image.new('RGB', (IMAGE_WIDTH, IMAGE_HEIGHT))
    draw = ImageDraw.Draw(img)
    
    # Create beautiful gradient (Spanish colors: red to orange to gold)
    for y in range(IMAGE_HEIGHT):
        ratio = y / IMAGE_HEIGHT
        
        if ratio < 0.4:
            # Top: Deep red to orange
            r = int(195 + (243 - 195) * (ratio / 0.4))
            g = int(20 + (115 - 20) * (ratio / 0.4))
            b = int(50 + (53 - 50) * (ratio / 0.4))
        elif ratio < 0.7:
            # Middle: Orange to gold
            r = int(243 + (255 - 243) * ((ratio - 0.4) / 0.3))
            g = int(115 + (193 - 115) * ((ratio - 0.4) / 0.3))
            b = int(53 + (7 - 53) * ((ratio - 0.4) / 0.3))
        else:
            # Bottom: Gold to yellow
            r = int(255)
            g = int(193 + (215 - 193) * ((ratio - 0.7) / 0.3))
            b = int(7 + (0 - 7) * ((ratio - 0.7) / 0.3))
        
        draw.rectangle([(0, y), (IMAGE_WIDTH, y + 1)], fill=(r, g, b))
    
    # Add subtle pattern for depth
    for i in range(0, IMAGE_WIDTH, 80):
        for j in range(0, IMAGE_HEIGHT, 80):
            draw.ellipse(
                [(i + 20, j + 20), (i + 60, j + 60)],
                outline=(255, 255, 255, 30),
                width=2
            )
    
    # Save background
    img.save(BACKGROUND_IMAGE, quality=95)
    print(f"[background] ✅ Created default background: {BACKGROUND_IMAGE}")
    
    return img


def load_background():
    """
    Load the background image (creates default if doesn't exist)
    """
    
    if not BACKGROUND_IMAGE.exists():
        print("[background] No background found, creating default...")
        return create_default_background()
    
    return Image.open(BACKGROUND_IMAGE)


def create_phrase_image(phrase_data: dict, output_path: str):
    """
    Create image using the SAME background for all phrases
    Only the text changes!
    """
    
    # Load background (reuse same image every time)
    img = load_background().copy()
    draw = ImageDraw.Draw(img)
    
    # Load fonts (cross-platform compatible - optimized for GitHub Actions/Linux)
    try:
        # Try fonts/ folder first (if user added fonts there)
        font_category = ImageFont.truetype("fonts/arial.ttf", 70)
        font_large = ImageFont.truetype("fonts/arialbd.ttf", 85)
        font_pronunciation = ImageFont.truetype("fonts/ariali.ttf", 28)
        font_branding = ImageFont.truetype("fonts/arialbd.ttf", 42)
    except:
        try:
            # Linux system fonts (GitHub Actions - Ubuntu)
            font_category = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 70)
            font_large = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 85)
            font_pronunciation = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 28)
            font_branding = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 42)
        except:
            try:
                # Windows system fonts
                font_category = ImageFont.truetype("arial.ttf", 70)
                font_large = ImageFont.truetype("arialbd.ttf", 85)
                font_pronunciation = ImageFont.truetype("ariali.ttf", 28)
                font_branding = ImageFont.truetype("arialbd.ttf", 42)
            except:
                # Last resort: use default but with warning
                print("[fonts] ⚠️ WARNING: Could not load fonts! Text will be tiny!")
                print("[fonts] Installing fonts on Linux: sudo apt-get install fonts-dejavu")
                font_category = ImageFont.load_default()
                font_large = ImageFont.load_default()
                font_pronunciation = ImageFont.load_default()
                font_branding = ImageFont.load_default()
    
    # Get text
    category = phrase_data.get("category", "Spanish Learning")
    english = phrase_data.get("english", "")
    spanish = phrase_data.get("spanish", "")
    pronunciation = phrase_data.get("pronunciation", "")
    
    # Helper: wrap text
    def wrap_text(text, font, max_width):
        words = text.split()
        lines = []
        current_line = []
        
        for word in words:
            test_line = ' '.join(current_line + [word])
            bbox = draw.textbbox((0, 0), test_line, font=font)
            width = bbox[2] - bbox[0]
            
            if width <= max_width:
                current_line.append(word)
            else:
                if current_line:
                    lines.append(' '.join(current_line))
                current_line = [word]
        
        if current_line:
            lines.append(' '.join(current_line))
        
        return lines
    
    # Draw category at top with IMPRESSIVE styling
    category_text = category.upper()
    category_bbox = draw.textbbox((IMAGE_WIDTH // 2, 180), category_text, font=font_category, anchor="mm")
    
    # Draw gradient background box for category with glow
    padding = 25
    
    # Glow effect (limited iterations to prevent coordinate inversion)
    for i in range(min(padding, 15)):  # Max 15 iterations to prevent issues
        alpha = int(200 - (i * 10))
        if alpha > 0:
            draw.rectangle(
                [
                    (category_bbox[0] - padding + i, category_bbox[1] - padding + i),
                    (category_bbox[2] + padding - i, category_bbox[3] + padding - i)
                ],
                outline=(138, 43, 226, alpha)  # Purple glow
            )
    
    # Solid background
    draw.rectangle(
        [
            (category_bbox[0] - padding, category_bbox[1] - padding),
            (category_bbox[2] + padding, category_bbox[3] + padding)
        ],
        fill=(20, 20, 40, 220)
    )
    
    # Draw category text with glow
    for offset in [(2,2), (-2,2), (2,-2), (-2,-2)]:
        draw.text(
            (IMAGE_WIDTH // 2 + offset[0], 180 + offset[1]),
            category_text,
            fill=(138, 43, 226),  # Purple glow
            font=font_category,
            anchor="mm"
        )
    
    draw.text(
        (IMAGE_WIDTH // 2, 180),
        category_text,
        fill=(255, 255, 255),
        font=font_category,
        anchor="mm",
        stroke_width=2,
        stroke_fill=(0, 0, 0)
    )
    
    # Draw English with solid background
    english_y = 550
    english_lines = wrap_text(english, font_large, IMAGE_WIDTH - 140)

    total_height = len(english_lines) * 100

    # Solid background for English (dark blue)
    box_top = english_y - 70
    box_bottom = english_y + total_height - 20

    draw.rectangle(
        [(70, box_top), (IMAGE_WIDTH - 70, box_bottom)],
        fill=(30, 40, 80)  # Dark blue, solid
    )

    # Draw English text (no glow, just stroke for visibility)
    for i, line in enumerate(english_lines):
        y_pos = english_y + (i * 100)

        # Main text with thick stroke
        draw.text(
            (IMAGE_WIDTH // 2, y_pos),
            line,
            fill=(255, 255, 255),
            font=font_large,
            anchor="mm",
            stroke_width=5,
            stroke_fill=(0, 0, 0)
        )
    
    
    # Draw Spanish with solid background
    spanish_y = english_y + (len(english_lines) * 100) + 100
    spanish_lines = wrap_text(spanish, font_large, IMAGE_WIDTH - 140)

    total_height = len(spanish_lines) * 100

    # Solid background for Spanish (warm brown)
    box_top = spanish_y - 70
    box_bottom = spanish_y + total_height - 20

    draw.rectangle(
        [(70, box_top), (IMAGE_WIDTH - 70, box_bottom)],
        fill=(80, 50, 30)  # Warm brown, solid
    )
    
    # Draw Spanish text (bright yellow for visibility)
    for i, line in enumerate(spanish_lines):
        y_pos = spanish_y + (i * 100)
        
        # Main text with thick stroke
        draw.text(
            (IMAGE_WIDTH // 2, y_pos),
            line,
            fill=(255, 255, 0),  # Bright yellow
            font=font_large,
            anchor="mm",
            stroke_width=5,
            stroke_fill=(0, 0, 0)
        )
    
    # Draw pronunciation (subtle, elegant) with DARK CONTAINER that expands
    pronunciation_y = spanish_y + (len(spanish_lines) * 100) + 45
    pronunciation_text = f"[{pronunciation}]"

    # Wrap pronunciation text if too long
    max_pron_width = 600  # Max width before wrapping
    pron_lines = wrap_text(pronunciation_text, font_pronunciation, max_pron_width)

    # Calculate actual text width for dynamic container sizing
    max_pron_text_width = 0
    for line in pron_lines:
        bbox = draw.textbbox((0, 0), line, font=font_pronunciation)
        text_width = bbox[2] - bbox[0]
        max_pron_text_width = max(max_pron_text_width, text_width)

    # Container sizing with padding - expands based on text length
    pron_padding_x = 40
    pron_padding_y = 20
    min_pron_width = 200
    pron_container_width = max(min_pron_width, max_pron_text_width + (pron_padding_x * 2))
    pron_container_width = min(pron_container_width, IMAGE_WIDTH - 100)  # Max constraint

    # Calculate total height for all pronunciation lines
    pron_line_height = 35
    total_pron_height = len(pron_lines) * pron_line_height

    # Calculate box dimensions - container expands vertically and horizontally
    box_top = pronunciation_y - total_pron_height // 2 - pron_padding_y + 10
    box_bottom = pronunciation_y + (len(pron_lines) - 1) * pron_line_height + total_pron_height // 2 + pron_padding_y - 10
    box_left = (IMAGE_WIDTH - pron_container_width) // 2
    box_right = (IMAGE_WIDTH + pron_container_width) // 2

    # Draw DARK background box for pronunciation (darker, more visible)
    draw.rectangle(
        [(box_left, box_top), (box_right, box_bottom)],
        fill=(30, 30, 50, 200)  # Dark container, more opaque
    )

    # Draw each pronunciation line
    for i, pron_line in enumerate(pron_lines):
        y_pos = pronunciation_y + (i * pron_line_height)
        draw.text(
            (IMAGE_WIDTH // 2, y_pos),
            pron_line,
            fill=(220, 220, 240),
            font=font_pronunciation,
            anchor="mm",
            stroke_width=1,
            stroke_fill=(0, 0, 0)
        )

    # Add "Habla Verse" branding at bottom with language labels
    branding_y = IMAGE_HEIGHT - 95
    branding_text = "Habla Verse"

    try:
        font_branding = ImageFont.truetype("fonts/arialbd.ttf", 42)  # Increased from 32
        font_language = ImageFont.truetype("fonts/arial.ttf", 22)  # Increased from 18
    except:
        try:
            font_branding = ImageFont.truetype("arialbd.ttf", 42)
            font_language = ImageFont.truetype("arial.ttf", 22)
        except:
            font_branding = ImageFont.load_default()
            font_language = ImageFont.load_default()

    # Get text width for centering
    branding_bbox = draw.textbbox((0, 0), branding_text, font=font_branding)
    branding_width = branding_bbox[2] - branding_bbox[0]

    # Subtle glow effect for branding
    for offset in [(1, 1), (-1, 1), (1, -1), (-1, -1)]:
        draw.text(
            (IMAGE_WIDTH // 2 + offset[0], branding_y + offset[1]),
            branding_text,
            fill=(0, 0, 0, 150),
            font=font_branding,
            anchor="mm"
        )

    # Main branding text (elegant gold color)
    draw.text(
        (IMAGE_WIDTH // 2, branding_y),
        branding_text,
        fill=(255, 215, 0),  # Gold color
        font=font_branding,
        anchor="mm",
        stroke_width=2,
        stroke_fill=(0, 0, 0)
    )

    # Add "English • Spanish" language label below branding (smaller, subtle)
    language_text = "English • Spanish"
    language_y = branding_y + 40  # Increased spacing
    
    language_bbox = draw.textbbox((0, 0), language_text, font=font_language)
    language_width = language_bbox[2] - language_bbox[0]

    # Draw black outline/shadow first for visibility
    for offset in [(1, 0), (-1, 0), (0, 1), (0, -1), (1, 1), (-1, -1), (1, -1), (-1, 1)]:
        draw.text(
            (IMAGE_WIDTH // 2 + offset[0], language_y + offset[1]),
            language_text,
            fill=(0, 0, 0),  # Black outline
            font=font_language,
            anchor="mm"
        )
    
    # Main text (bright white for contrast)
    draw.text(
        (IMAGE_WIDTH // 2, language_y),
        language_text,
        fill=(255, 255, 255),  # Bright white
        font=font_language,
        anchor="mm"
    )

    # Save
    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    img.save(output_path, quality=95, optimize=True)
    
    return output_path


def generate_complete_image(phrase_data: dict, output_path: str):
    """
    Generate image with text on the SAME background
    """
    return create_phrase_image(phrase_data, output_path)


if __name__ == "__main__":
    # Test
    test_phrase = {
        "english": "Good morning! How are you?",
        "spanish": "¡Buenos días! ¿Cómo estás?",
        "pronunciation": "BWEH-nos DEE-as KOH-moh es-TAHS",
        "category": "Daily Greetings"
    }
    
    output = "test_output/test_image.jpg"
    generate_complete_image(test_phrase, output)
    print(f"\n✅ Test image generated: {output}")
