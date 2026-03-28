"""
Video Creator for Spanish Learning Content
Creates engaging videos with images, audio, and subtitles
"""

import os
import json
import subprocess
from pathlib import Path

# Try different moviepy import methods
try:
    from moviepy.editor import ImageClip, AudioFileClip, concatenate_videoclips
except ImportError:
    from moviepy import ImageClip, AudioFileClip, concatenate_videoclips

import wave
from vosk import Model, KaldiRecognizer

# Video settings
VIDEO_WIDTH = 1080
VIDEO_HEIGHT = 1920
FPS = 30


def generate_subtitles_with_vosk(audio_file: str, output_srt: str):
    """
    Generate word-level subtitles using Vosk
    """
    
    print(f"[subs] Generating subtitles with Vosk...")
    
    # Download Vosk model if needed
    model_path = "vosk-model-small-en-us-0.15"
    if not os.path.exists(model_path):
        print("[subs] Downloading Vosk model (~40MB)...")
        import urllib.request
        import zipfile
        
        url = "https://alphacephei.com/vosk/models/vosk-model-small-en-us-0.15.zip"
        zip_path = "vosk-model.zip"
        
        urllib.request.urlretrieve(url, zip_path)
        
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            zip_ref.extractall(".")
        
        os.remove(zip_path)
        print("[subs] Model downloaded!")
    
    # Convert MP3 to WAV for Vosk
    wav_file = audio_file.replace(".mp3", ".wav")
    subprocess.run([
        "ffmpeg", "-y", "-i", audio_file,
        "-ar", "16000", "-ac", "1", wav_file
    ], check=True, capture_output=True)
    
    # Load Vosk model
    model = Model(model_path)
    wf = wave.open(wav_file, "rb")
    rec = KaldiRecognizer(model, wf.getframerate())
    rec.SetWords(True)
    
    # Process audio
    words = []
    while True:
        data = wf.readframes(4000)
        if len(data) == 0:
            break
        if rec.AcceptWaveform(data):
            result = json.loads(rec.Result())
            if 'result' in result:
                for word_info in result['result']:
                    words.append({
                        'word': word_info['word'],
                        'start': word_info['start'],
                        'end': word_info['end']
                    })
    
    # Final result
    final_result = json.loads(rec.FinalResult())
    if 'result' in final_result:
        for word_info in final_result['result']:
            words.append({
                'word': word_info['word'],
                'start': word_info['start'],
                'end': word_info['end']
            })
    
    # Close the wave file before deleting
    wf.close()
    
    # Create SRT file
    with open(output_srt, "w", encoding="utf-8") as f:
        for i, word in enumerate(words, 1):
            start_time = format_srt_time(word['start'])
            end_time = format_srt_time(word['end'])
            
            f.write(f"{i}\n")
            f.write(f"{start_time} --> {end_time}\n")
            f.write(f"{word['word'].upper()}\n\n")
    
    print(f"[subs] ✅ Subtitles generated ({len(words)} words)")
    
    # Clean up WAV file (with retry for Windows file locking)
    import time
    for attempt in range(3):
        try:
            if os.path.exists(wav_file):
                os.remove(wav_file)
            break
        except PermissionError:
            if attempt < 2:
                time.sleep(0.5)
            else:
                print(f"[subs] ⚠️ Could not delete temp file: {wav_file}")
    
    return output_srt


def format_srt_time(seconds: float) -> str:
    """Convert seconds to SRT time format (HH:MM:SS,mmm)"""
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    secs = int(seconds % 60)
    millis = int((seconds % 1) * 1000)
    return f"{hours:02d}:{minutes:02d}:{secs:02d},{millis:03d}"


def create_video_from_images_and_audio(
    image_files: list,
    audio_file: str,
    output_file: str,
    subtitle_file: str = None
):
    """
    Create video from images and audio with optional subtitles
    Uses FFmpeg directly for better compatibility
    """
    
    print(f"[video] Creating video from {len(image_files)} images...")
    
    # Get audio duration
    cmd = [
        "ffprobe", "-v", "error",
        "-show_entries", "format=duration",
        "-of", "default=noprint_wrappers=1:nokey=1",
        str(audio_file)
    ]
    result = subprocess.run(cmd, capture_output=True, text=True)
    total_duration = float(result.stdout.strip())
    
    duration_per_image = total_duration / len(image_files)
    
    print(f"[video] Total duration: {total_duration:.1f}s, {duration_per_image:.1f}s per image")
    
    # Create video clips using FFmpeg
    temp_clips = []
    for i, img_path in enumerate(image_files):
        print(f"[video] Processing image {i+1}/{len(image_files)}...")
        
        temp_clip = Path(output_file).parent / f"temp_clip_{i:02d}.mp4"
        temp_clips.append(temp_clip)
        
        # Create video clip from image with FFmpeg
        cmd = [
            "ffmpeg", "-y",
            "-loop", "1",
            "-i", str(img_path),
            "-vf", f"scale={VIDEO_WIDTH}:{VIDEO_HEIGHT}:force_original_aspect_ratio=decrease,pad={VIDEO_WIDTH}:{VIDEO_HEIGHT}:(ow-iw)/2:(oh-ih)/2,fps={FPS}",
            "-t", str(duration_per_image),
            "-c:v", "libx264",
            "-pix_fmt", "yuv420p",
            "-preset", "medium",
            str(temp_clip)
        ]
        
        subprocess.run(cmd, check=True, capture_output=True)
    
    # Create concat file
    concat_file = Path(output_file).parent / "concat_list.txt"
    with open(concat_file, "w") as f:
        for clip in temp_clips:
            f.write(f"file '{clip.resolve()}'\n")
    
    # Concatenate clips
    print("[video] Concatenating clips...")
    temp_video = Path(output_file).parent / "temp_video.mp4"
    
    cmd = [
        "ffmpeg", "-y",
        "-f", "concat",
        "-safe", "0",
        "-i", str(concat_file),
        "-c", "copy",
        str(temp_video)
    ]
    
    subprocess.run(cmd, check=True, capture_output=True)
    
    # Add audio
    print("[video] Adding audio...")
    
    cmd = [
        "ffmpeg", "-y",
        "-i", str(temp_video),
        "-i", str(audio_file),
        "-c:v", "copy",
        "-c:a", "aac",
        "-shortest",
        str(output_file)
    ]
    
    subprocess.run(cmd, check=True, capture_output=True)
    
    print(f"[video] ✅ Video created: {output_file}")
    
    # Add subtitles if provided
    if subtitle_file and os.path.exists(subtitle_file):
        print("[video] Adding subtitles...")
        video_with_subs = str(output_file).replace(".mp4", "_temp_subs.mp4")
        
        # Use ffmpeg to burn subtitles
        subtitle_path = str(Path(subtitle_file).resolve()).replace("\\", "/").replace(":", "\\:")
        
        cmd = [
            "ffmpeg", "-y",
            "-i", str(output_file),
            "-vf", f"subtitles='{subtitle_path}':force_style='FontName=Arial Black,FontSize=24,PrimaryColour=&HFFFFFF,OutlineColour=&H000000,BorderStyle=1,Outline=2,Shadow=1,Alignment=2,MarginV=50'",
            "-c:a", "copy",
            video_with_subs
        ]
        
        subprocess.run(cmd, check=True, capture_output=True)
        
        # Replace original with subtitled version
        os.replace(video_with_subs, output_file)
        print(f"[video] ✅ Subtitles added")
    
    # Cleanup temp files
    print("[video] Cleaning up temporary files...")
    for clip in temp_clips:
        if clip.exists():
            clip.unlink()
    if temp_video.exists():
        temp_video.unlink()
    if concat_file.exists():
        concat_file.unlink()
    
    return output_file


def create_complete_video(
    phrases: list,
    image_dir: str,
    audio_file: str,
    output_file: str = "output/final_video.mp4",
    audio_files: list = None
):
    """
    Create complete video from phrases, images, and audio
    NO SUBTITLES - text is already on images
    Uses actual audio durations for perfect sync!
    """
    
    # Get all image files
    image_files = sorted(Path(image_dir).glob("*.jpg"))
    
    if len(image_files) != len(phrases):
        raise ValueError(f"Mismatch: {len(image_files)} images vs {len(phrases)} phrases")
    
    # If audio_files provided, use actual durations for each phrase
    if audio_files:
        print(f"[video] Using actual audio durations for perfect sync!")
        create_video_with_durations(image_files, audio_file, output_file, audio_files)
    else:
        # Fallback: equal time division
        create_video_from_images_and_audio(
            image_files,
            audio_file,
            output_file,
            subtitle_file=None
        )
    
    return output_file


def create_video_with_durations(
    image_files: list,
    audio_file: str,
    output_file: str,
    audio_files: list
):
    """
    Create video using actual audio durations for each phrase
    This ensures perfect sync between images and audio!
    """
    
    print(f"[video] Creating video from {len(image_files)} images with precise timing...")
    
    # Create video clips with actual durations
    temp_clips = []
    for i, (img_path, audio_info) in enumerate(zip(image_files, audio_files)):
        duration = audio_info['duration']  # Actual duration from audio generation
        print(f"[video] Image {i+1}/{len(image_files)}: {duration:.2f}s")
        
        temp_clip = Path(output_file).parent / f"temp_clip_{i:02d}.mp4"
        temp_clips.append(temp_clip)
        
        # Create video clip from image with exact duration
        cmd = [
            "ffmpeg", "-y",
            "-loop", "1",
            "-i", str(img_path),
            "-vf", f"scale={VIDEO_WIDTH}:{VIDEO_HEIGHT}:force_original_aspect_ratio=decrease,pad={VIDEO_WIDTH}:{VIDEO_HEIGHT}:(ow-iw)/2:(oh-ih)/2,fps={FPS}",
            "-t", str(duration),  # Use actual duration!
            "-c:v", "libx264",
            "-pix_fmt", "yuv420p",
            "-preset", "medium",
            str(temp_clip)
        ]
        
        subprocess.run(cmd, check=True, capture_output=True)
    
    # Create concat file
    concat_file = Path(output_file).parent / "concat_list.txt"
    with open(concat_file, "w") as f:
        for clip in temp_clips:
            f.write(f"file '{clip.resolve()}'\n")
    
    # Concatenate clips
    print("[video] Concatenating clips...")
    temp_video = Path(output_file).parent / "temp_video.mp4"
    
    cmd = [
        "ffmpeg", "-y",
        "-f", "concat",
        "-safe", "0",
        "-i", str(concat_file),
        "-c", "copy",
        str(temp_video)
    ]
    
    subprocess.run(cmd, check=True, capture_output=True)
    
    # Add audio
    print("[video] Adding audio...")
    
    cmd = [
        "ffmpeg", "-y",
        "-i", str(temp_video),
        "-i", str(audio_file),
        "-c:v", "copy",
        "-c:a", "aac",
        "-shortest",
        str(output_file)
    ]
    
    subprocess.run(cmd, check=True, capture_output=True)
    
    print(f"[video] ✅ Video created: {output_file}")
    
    # Cleanup temp files
    print("[video] Cleaning up temporary files...")
    for clip in temp_clips:
        if clip.exists():
            clip.unlink()
    if temp_video.exists():
        temp_video.unlink()
    if concat_file.exists():
        concat_file.unlink()
    
    return output_file


if __name__ == "__main__":
    # Test video creation
    print("This module should be imported and used by main.py")
    print("Run main.py to generate a complete video")
