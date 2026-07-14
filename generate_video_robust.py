"""
Habla Verse - Robust Spanish Learning Video Generator
Works anywhere: GitHub Actions, local machine, server, etc.

Features:
- English spoken only ONCE per phrase
- Subtle "Habla Verse" branding at bottom
- Simple, viral-friendly phrases (max 10-12 words)
- No duplicate phrases across runs
- Comprehensive error handling
- Auto-dependency checking
"""

import os
import sys
import asyncio
import subprocess
import random
from pathlib import Path
from dotenv import load_dotenv

# ============================================================
# CONFIGURATION
# ============================================================

# API Configuration
POLLINATIONS_API_KEY = os.getenv("POLLINATIONS_API_KEY", "sk_M6MzY38oOt2wCvBZNWH4Y8byvhsrBhVK")

# Voice settings
ENGLISH_VOICE = "en-US-GuyNeural"
SPANISH_VOICE = "es-ES-AlvaroNeural"

# Video settings
VIDEO_WIDTH = 1080
VIDEO_HEIGHT = 1920
FPS = 30

# Phrase settings
MAX_PHRASES_PER_VIDEO = 5
MAX_WORDS_PER_PHRASE = 12

# Output directories
OUTPUT_DIR = Path("output")
IMAGES_DIR = OUTPUT_DIR / "images"
AUDIO_DIR = OUTPUT_DIR / "audio"

# ============================================================
# DEPENDENCY CHECKS
# ============================================================

def check_dependencies():
    """Check if all required tools are available"""
    errors = []
    
    # Check Python version
    if sys.version_info < (3, 8):
        errors.append("Python 3.8+ required")
    
    # Check FFmpeg
    try:
        result = subprocess.run(["ffmpeg", "-version"], capture_output=True, text=True, timeout=5)
        if result.returncode != 0:
            errors.append("FFmpeg not found or not working")
    except FileNotFoundError:
        errors.append("FFmpeg not installed. Install from: https://ffmpeg.org/download.html")
    except Exception as e:
        errors.append(f"FFmpeg check failed: {e}")
    
    # Check ffprobe
    try:
        result = subprocess.run(["ffprobe", "-version"], capture_output=True, text=True, timeout=5)
        if result.returncode != 0:
            errors.append("FFprobe not found or not working")
    except FileNotFoundError:
        errors.append("FFprobe not installed (comes with FFmpeg)")
    except Exception as e:
        errors.append(f"FFprobe check failed: {e}")
    
    # Check required Python packages
    required_packages = ["requests", "PIL", "edge_tts", "dotenv"]
    for package in required_packages:
        try:
            __import__(package)
        except ImportError:
            errors.append(f"Python package '{package}' not installed. Run: pip install -r requirements.txt")
    
    # Check API key
    if not POLLINATIONS_API_KEY or POLLINATIONS_API_KEY.startswith("your_"):
        errors.append("POLLINATIONS_API_KEY not set. Get one at: https://enter.pollinations.ai")
    
    return errors


def check_fonts():
    """Check if required fonts are available"""
    font_paths = [
        Path("fonts/arial.ttf"),
        Path("fonts/arialbd.ttf"),
        Path("fonts/ariali.ttf"),
        Path("arial.ttf"),
        Path("arialbd.ttf"),
        Path("ariali.ttf"),
    ]
    
    found = any(p.exists() for p in font_paths)
    
    if not found:
        print("[warning] ⚠️ Arial fonts not found. Using system fallback fonts.")
        print("[warning] For best results, add Arial fonts to fonts/ folder")
    
    return found


# ============================================================
# IMPORT MODULES (after dependency check)
# ============================================================

try:
    import requests
    from PIL import Image, ImageDraw, ImageFont
    import edge_tts
    from generate_content import generate_learning_content, CATEGORIES
    from content_tracker import load_history, filter_duplicate_phrases, log_content_generation
except ImportError as e:
    print(f"❌ Import error: {e}")
    print("Make sure all dependencies are installed: pip install -r requirements.txt")
    sys.exit(1)


# ============================================================
# AUDIO GENERATION
# ============================================================

async def generate_single_audio(text: str, voice: str, output_path: str):
    """Generate audio for a single text using Edge TTS"""
    communicate = edge_tts.Communicate(text, voice)
    await communicate.save(output_path)


def get_audio_duration(audio_file: str) -> float:
    """Get audio duration using ffprobe"""
    cmd = [
        "ffprobe", "-v", "error",
        "-show_entries", "format=duration",
        "-of", "default=noprint_wrappers=1:nokey=1",
        audio_file
    ]
    result = subprocess.run(cmd, capture_output=True, text=True)
    return float(result.stdout.strip())


def generate_audio_for_phrases(phrases: list, audio_dir: Path):
    """Generate audio for all phrases - English ONCE, then Spanish"""
    audio_files = []
    audio_dir.mkdir(parents=True, exist_ok=True)
    
    for i, phrase in enumerate(phrases):
        print(f"\nPhrase {i+1}/{len(phrases)}:")
        
        english_file = audio_dir / f"english_{i}.mp3"
        spanish_file = audio_dir / f"spanish_{i}.mp3"
        combined_file = audio_dir / f"combined_{i}.mp3"
        
        # Generate English audio (ONCE only)
        asyncio.run(generate_single_audio(phrase["english"], ENGLISH_VOICE, str(english_file)))
        print(f"   ✅ English: {phrase['english']}")
        
        # Generate Spanish audio
        asyncio.run(generate_single_audio(phrase["spanish"], SPANISH_VOICE, str(spanish_file)))
        print(f"   ✅ Spanish: {phrase['spanish']}")
        
        # Combine: English -> 400ms pause -> Spanish -> 800ms pause
        cmd = [
            "ffmpeg", "-y",
            "-i", str(english_file),
            "-i", str(spanish_file),
            "-filter_complex",
            "[0:a]apad=pad_dur=0.4[padded_eng];[1:a]apad=pad_dur=0.8[padded_span];[padded_eng][padded_span]concat=n=2:v=0:a=1[out]",
            "-map", "[out]",
            str(combined_file)
        ]
        subprocess.run(cmd, capture_output=True, check=True)
        
        duration = get_audio_duration(str(combined_file))
        audio_files.append({
            "english": str(english_file),
            "spanish": str(spanish_file),
            "combined": str(combined_file),
            "duration": duration
        })
        print(f"   ✅ Combined: {duration:.1f}s")
    
    return audio_files


def create_final_narration(audio_files: list, output_file: Path):
    """Concatenate all phrase audio into final narration"""
    audio_dir = output_file.parent
    
    # Create concat file
    concat_file = audio_dir / "concat_audio.txt"
    with open(concat_file, "w") as f:
        for audio_info in audio_files:
            # Use absolute path for robustness
            abs_path = Path(audio_info["combined"]).resolve()
            f.write(f"file '{abs_path}'\n")
    
    # Concatenate
    cmd = [
        "ffmpeg", "-y",
        "-f", "concat",
        "-safe", "0",
        "-i", str(concat_file),
        "-c", "copy",
        str(output_file)
    ]
    subprocess.run(cmd, capture_output=True, check=True)
    
    # Cleanup
    if concat_file.exists():
        concat_file.unlink()
    
    return output_file


# ============================================================
# IMAGE GENERATION
# ============================================================

IMAGE_WIDTH = 1080
IMAGE_HEIGHT = 1920
BACKGROUND_IMAGE = Path("background.png")


def load_or_create_background():
    """Load or create gradient background"""
    if BACKGROUND_IMAGE.exists():
        return Image.open(BACKGROUND_IMAGE)
    
    # Create gradient background
    img = Image.new('RGB', (IMAGE_WIDTH, IMAGE_HEIGHT))
    draw = ImageDraw.Draw(img)
    
    # Spanish colors gradient
    for y in range(IMAGE_HEIGHT):
        ratio = y / IMAGE_HEIGHT
        if ratio < 0.4:
            r = int(195 + (243 - 195) * (ratio / 0.4))
            g = int(20 + (115 - 20) * (ratio / 0.4))
            b = int(50 + (53 - 50) * (ratio / 0.4))
        elif ratio < 0.7:
            r = int(243 + (255 - 243) * ((ratio - 0.4) / 0.3))
            g = int(115 + (193 - 115) * ((ratio - 0.4) / 0.3))
            b = int(53 + (7 - 53) * ((ratio - 0.4) / 0.3))
        else:
            r, g, b = 255, int(193 + (215 - 193) * ((ratio - 0.7) / 0.3)), 7
        
        draw.rectangle([(0, y), (IMAGE_WIDTH, y + 1)], fill=(r, g, b))
    
    img.save(BACKGROUND_IMAGE, quality=95)
    return img


def get_fonts():
    """Load fonts with fallbacks - optimized for GitHub Actions (Linux)"""
    font_configs = [
        # Linux first (GitHub Actions - Ubuntu has DejaVu fonts)
        ("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"),
        # Then fonts/ folder (if user added custom fonts)
        ("fonts/arial.ttf", "fonts/arialbd.ttf", "fonts/ariali.ttf"),
        # Windows fallback
        ("arial.ttf", "arialbd.ttf", "ariali.ttf"),
    ]

    for config in font_configs:
        try:
            return {
                "category": ImageFont.truetype(config[0], 70),
                "large": ImageFont.truetype(config[1], 85),
                "pronunciation": ImageFont.truetype(config[2], 28),
                "branding": ImageFont.truetype(config[1], 42)  # Increased branding size
            }
        except:
            continue

    # Last resort
    print("[warning] Using default fonts")
    return {k: ImageFont.load_default() for k in ["category", "large", "pronunciation", "branding"]}


def wrap_text(draw, text, font, max_width):
    """Wrap text to fit within max width"""
    words = text.split()
    lines = []
    current_line = []
    
    for word in words:
        test_line = ' '.join(current_line + [word])
        bbox = draw.textbbox((0, 0), test_line, font=font)
        if bbox[2] - bbox[0] <= max_width:
            current_line.append(word)
        else:
            if current_line:
                lines.append(' '.join(current_line))
            current_line = [word]
    
    if current_line:
        lines.append(' '.join(current_line))
    
    return lines


def generate_phrase_image(phrase: dict, output_path: str, fonts: dict):
    """Generate single phrase image with branding"""
    img = load_or_create_background().copy()
    draw = ImageDraw.Draw(img)
    
    category = phrase.get("category", "Spanish Learning")
    english = phrase.get("english", "")
    spanish = phrase.get("spanish", "")
    pronunciation = phrase.get("pronunciation", "")
    
    # Category at top
    category_text = category.upper()
    category_bbox = draw.textbbox((IMAGE_WIDTH // 2, 180), category_text, font=fonts["category"], anchor="mm")
    padding = 25
    
    # Background box for category
    draw.rectangle(
        [(category_bbox[0] - padding, category_bbox[1] - padding),
         (category_bbox[2] + padding, category_bbox[3] + padding)],
        fill=(20, 20, 40, 220)
    )
    
    # Category text with stroke
    draw.text(
        (IMAGE_WIDTH // 2, 180),
        category_text,
        fill=(255, 255, 255),
        font=fonts["category"],
        anchor="mm",
        stroke_width=2,
        stroke_fill=(0, 0, 0)
    )
    
    # English text with background
    english_y = 550
    english_lines = wrap_text(draw, english, fonts["large"], IMAGE_WIDTH - 140)
    
    draw.rectangle(
        [(70, english_y - 70), (IMAGE_WIDTH - 70, english_y + len(english_lines) * 100 - 20)],
        fill=(30, 40, 80)
    )
    
    for i, line in enumerate(english_lines):
        draw.text(
            (IMAGE_WIDTH // 2, english_y + i * 100),
            line,
            fill=(255, 255, 255),
            font=fonts["large"],
            anchor="mm",
            stroke_width=5,
            stroke_fill=(0, 0, 0)
        )
    
    # Spanish text with background
    spanish_y = english_y + len(english_lines) * 100 + 100
    spanish_lines = wrap_text(draw, spanish, fonts["large"], IMAGE_WIDTH - 140)
    
    draw.rectangle(
        [(70, spanish_y - 70), (IMAGE_WIDTH - 70, spanish_y + len(spanish_lines) * 100 - 20)],
        fill=(80, 50, 30)
    )
    
    for i, line in enumerate(spanish_lines):
        draw.text(
            (IMAGE_WIDTH // 2, spanish_y + i * 100),
            line,
            fill=(255, 255, 0),
            font=fonts["large"],
            anchor="mm",
            stroke_width=5,
            stroke_fill=(0, 0, 0)
        )
    
    # Pronunciation with DARK CONTAINER that expands
    pron_y = spanish_y + len(spanish_lines) * 100 + 45
    pron_text = f"[{pronunciation}]"
    pron_lines = wrap_text(draw, pron_text, fonts["pronunciation"], 600)
    
    # Calculate actual text width for dynamic container
    max_pron_text_width = 0
    for line in pron_lines:
        bbox = draw.textbbox((0, 0), line, font=fonts["pronunciation"])
        text_width = bbox[2] - bbox[0]
        max_pron_text_width = max(max_pron_text_width, text_width)
    
    # Container sizing - expands based on text
    pron_padding_x = 40
    pron_padding_y = 20
    min_pron_width = 200
    pron_container_width = max(min_pron_width, max_pron_text_width + (pron_padding_x * 2))
    pron_container_width = min(pron_container_width, IMAGE_WIDTH - 100)
    
    pron_line_height = 35
    total_pron_height = len(pron_lines) * pron_line_height
    
    # Calculate box dimensions
    box_top = pron_y - total_pron_height // 2 - pron_padding_y + 10
    box_bottom = pron_y + (len(pron_lines) - 1) * pron_line_height + total_pron_height // 2 + pron_padding_y - 10
    box_left = (IMAGE_WIDTH - pron_container_width) // 2
    box_right = (IMAGE_WIDTH + pron_container_width) // 2
    
    # Draw DARK background box
    draw.rectangle(
        [(box_left, box_top), (box_right, box_bottom)],
        fill=(30, 30, 50, 200)
    )
    
    for i, line in enumerate(pron_lines):
        draw.text(
            (IMAGE_WIDTH // 2, pron_y + i * pron_line_height),
            line,
            fill=(220, 220, 240),
            font=fonts["pronunciation"],
            anchor="mm",
            stroke_width=1,
            stroke_fill=(0, 0, 0)
        )
    
    # BRANDING: "Habla Verse" + "English • Spanish" at bottom
    branding_y = IMAGE_HEIGHT - 95
    branding_text = "Habla Verse"
    
    # Shadow
    for offset in [(1, 1), (-1, 1), (1, -1), (-1, -1)]:
        draw.text(
            (IMAGE_WIDTH // 2 + offset[0], branding_y + offset[1]),
            branding_text,
            fill=(0, 0, 0, 150),
            font=fonts["branding"],
            anchor="mm"
        )
    
    # Main branding (gold)
    draw.text(
        (IMAGE_WIDTH // 2, branding_y),
        branding_text,
        fill=(255, 215, 0),
        font=fonts["branding"],
        anchor="mm",
        stroke_width=2,
        stroke_fill=(0, 0, 0)
    )
    
    # Language label below branding
    language_text = "English • Spanish"
    language_y = branding_y + 40
    
    try:
        font_language = ImageFont.truetype("fonts/arial.ttf", 22)
    except:
        font_language = ImageFont.truetype("arial.ttf", 22)
    
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


def generate_all_images(phrases: list, images_dir: Path, fonts: dict):
    """Generate images for all phrases"""
    images_dir.mkdir(parents=True, exist_ok=True)
    image_files = []

    for i, phrase in enumerate(phrases):
        # Category is already in phrase from generate_video()
        output_path = images_dir / f"phrase_{i:02d}.jpg"
        generate_phrase_image(phrase, str(output_path), fonts)
        image_files.append(str(output_path))
        print(f"   ✅ Image {i+1}/{len(phrases)}")

    return image_files


# ============================================================
# VIDEO CREATION
# ============================================================

def create_video_from_images_and_audio(
    image_files: list,
    audio_file: str,
    output_file: str,
    audio_durations: list
):
    """Create video using actual audio durations for perfect sync"""
    
    temp_clips = []
    
    # Create clips with exact durations
    for i, (img_path, duration) in enumerate(zip(image_files, audio_durations)):
        print(f"[video] Image {i+1}/{len(image_files)}: {duration:.2f}s")
        
        temp_clip = Path(output_file).parent / f"temp_clip_{i:02d}.mp4"
        temp_clips.append(temp_clip)
        
        cmd = [
            "ffmpeg", "-y",
            "-loop", "1",
            "-i", img_path,
            "-vf", f"scale={VIDEO_WIDTH}:{VIDEO_HEIGHT}:force_original_aspect_ratio=decrease,pad={VIDEO_WIDTH}:{VIDEO_HEIGHT}:(ow-iw)/2:(oh-ih)/2,fps={FPS},format=yuv420p",
            "-t", str(duration),
            "-c:v", "libx264",
            "-profile:v", "main",
            "-level:v", "4.0",
            "-preset", "medium",
            "-movflags", "+faststart",
            str(temp_clip)
        ]
        subprocess.run(cmd, capture_output=True, check=True)
    
    # Concatenate clips
    concat_file = Path(output_file).parent / "concat_list.txt"
    with open(concat_file, "w") as f:
        for clip in temp_clips:
            f.write(f"file '{clip.resolve()}'\n")
    
    temp_video = Path(output_file).parent / "temp_video.mp4"
    
    cmd = [
        "ffmpeg", "-y",
        "-f", "concat",
        "-safe", "0",
        "-i", str(concat_file),
        "-c", "copy",
        str(temp_video)
    ]
    subprocess.run(cmd, capture_output=True, check=True)
    
    # Add audio
    cmd = [
        "ffmpeg", "-y",
        "-i", str(temp_video),
        "-i", audio_file,
        "-c:v", "copy",
        "-c:a", "aac",
        "-shortest",
        output_file
    ]
    subprocess.run(cmd, capture_output=True, check=True)
    
    # Cleanup
    for clip in temp_clips:
        if clip.exists():
            clip.unlink()
    if temp_video.exists():
        temp_video.unlink()
    if concat_file.exists():
        concat_file.unlink()
    
    return output_file


# ============================================================
# MAIN GENERATION FUNCTION
# ============================================================

def generate_video():
    """Main video generation function - robust and portable"""
    
    print("="*80)
    print("🎬 HABLA VERSE - Video Generator")
    print("="*80)
    print()
    
    # Check dependencies
    print("[check] Verifying dependencies...")
    errors = check_dependencies()
    
    if errors:
        print("\n❌ ERRORS FOUND:")
        for error in errors:
            print(f"   • {error}")
        print("\nFix these issues and try again.")
        input("Press Enter to exit...")
        return None
    
    check_fonts()
    print("[check] ✅ All dependencies OK")
    print()
    
    # Load history
    history = load_history()
    used_phrases = history.get("used_phrases", [])
    print(f"[history] {len(used_phrases)} phrases tracked")
    
    # Choose category
    category = random.choice(CATEGORIES)
    print(f"[category] {category}")
    print()
    
    # Generate content
    print("[content] Generating phrases with AI...")
    try:
        phrases = generate_learning_content(category, MAX_PHRASES_PER_VIDEO * 2, used_phrases)
        phrases = filter_duplicate_phrases(phrases, history)[:MAX_PHRASES_PER_VIDEO]
    except Exception as e:
        print(f"❌ Content generation failed: {e}")
        input("Press Enter to exit...")
        return None
    
    if len(phrases) < MAX_PHRASES_PER_VIDEO:
        print(f"[warning] Only generated {len(phrases)} unique phrases (wanted {MAX_PHRASES_PER_VIDEO})")
    
    print(f"[content] ✅ {len(phrases)} phrases generated")
    print()
    
    # Show phrases
    print("📝 Phrases:")
    for i, p in enumerate(phrases, 1):
        print(f"\n{i}. {p['english']}")
        print(f"   → {p['spanish']}")
    
    print()
    print("="*80)
    
    # Create directories
    OUTPUT_DIR.mkdir(exist_ok=True)
    IMAGES_DIR.mkdir(exist_ok=True)
    AUDIO_DIR.mkdir(exist_ok=True)
    
    # Load fonts
    fonts = get_fonts()
    
    # Generate images - add category to each phrase
    print("\n🎨 Generating images...")
    for i, phrase in enumerate(phrases):
        # Add the actual category to each phrase
        phrase["category"] = category
    image_files = generate_all_images(phrases, IMAGES_DIR, fonts)
    print(f"✅ Images created: {len(image_files)}")
    
    # Generate audio
    print("\n🎙️ Generating audio (English ONCE + Spanish)...")
    audio_files = generate_audio_for_phrases(phrases, AUDIO_DIR)
    
    final_audio = OUTPUT_DIR / "narration.mp3"
    create_final_narration(audio_files, final_audio)
    print(f"✅ Narration: {final_audio}")
    
    # Create video
    print("\n🎬 Creating video...")
    final_video = OUTPUT_DIR / "final_video.mp4"
    
    durations = [a["duration"] for a in audio_files]
    create_video_from_images_and_audio(
        image_files,
        str(final_audio),
        str(final_video),
        durations
    )
    
    # Log generation
    log_content_generation(category, phrases)
    
    # Save metadata for uploads (title, description, hashtags)
    try:
        from upload_to_facebook import save_metadata
        save_metadata(phrases, category, str(OUTPUT_DIR))
    except Exception as e:
        print(f"[warning] Could not save metadata: {e}")

    print()
    print("="*80)
    print("✅ VIDEO GENERATED SUCCESSFULLY!")
    print("="*80)
    print()
    print(f"📁 Location: {final_video.absolute()}")
    print(f"📊 Category: {category}")
    print(f"📝 Phrases: {len(phrases)}")
    print(f"⏱️ Duration: {sum(durations):.1f}s")
    print()
    print("🎯 Ready to share!")
    print()
    print("📝 Metadata saved for social media uploads:")
    print("   • Facebook title & description")
    print("   • YouTube title & description")
    print("   • Instagram caption")
    print("   • All hashtags lowercase for searchability")
    
    return str(final_video)


# ============================================================
# ENTRY POINT
# ============================================================

if __name__ == "__main__":
    try:
        generate_video()
    except KeyboardInterrupt:
        print("\n\n⚠️ Cancelled by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        input("Press Enter to exit...")
        sys.exit(1)
