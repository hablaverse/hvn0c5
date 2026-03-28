"""
Dual-Language Text-to-Speech Generator
Uses Edge TTS for high-quality English and Spanish voices
"""

import os
import asyncio
from pathlib import Path
import edge_tts
from pydub import AudioSegment

# Voice configurations
ENGLISH_VOICE = "en-US-GuyNeural"  # Male English voice (change to en-US-JennyNeural for female)
SPANISH_VOICE = "es-ES-AlvaroNeural"  # Male Spanish voice (change to es-ES-ElviraNeural for female)

# Alternative voices:
# English: en-US-ChristopherNeural, en-US-EricNeural, en-GB-RyanNeural
# Spanish: es-MX-JorgeNeural (Mexican), es-AR-TomasNeural (Argentinian)


async def generate_single_audio(text: str, voice: str, output_path: str):
    """Generate audio for a single text using specified voice"""
    communicate = edge_tts.Communicate(text, voice)
    await communicate.save(output_path)


def generate_phrase_audio(phrase_data: dict, output_dir: str, phrase_index: int):
    """
    Generate audio for a single phrase with English and Spanish
    
    Creates:
    - english_X.mp3: English phrase
    - spanish_X.mp3: Spanish translation
    - combined_X.mp3: English -> pause -> Spanish -> pause
    """
    
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    
    english_text = phrase_data["english"]
    spanish_text = phrase_data["spanish"]
    
    english_file = output_dir / f"english_{phrase_index}.mp3"
    spanish_file = output_dir / f"spanish_{phrase_index}.mp3"
    combined_file = output_dir / f"combined_{phrase_index}.mp3"
    
    print(f"[tts] Generating audio for phrase {phrase_index}...")
    
    # Generate English audio
    asyncio.run(generate_single_audio(english_text, ENGLISH_VOICE, str(english_file)))
    print(f"[tts]   ✅ English: {english_text[:50]}...")
    
    # Generate Spanish audio
    asyncio.run(generate_single_audio(spanish_text, SPANISH_VOICE, str(spanish_file)))
    print(f"[tts]   ✅ Spanish: {spanish_text[:50]}...")
    
    # Combine with pauses
    english_audio = AudioSegment.from_mp3(english_file)
    spanish_audio = AudioSegment.from_mp3(spanish_file)
    
    # Create pauses (800ms silence)
    pause = AudioSegment.silent(duration=800)
    
    # Combine: English -> pause -> Spanish -> pause
    combined = english_audio + pause + spanish_audio + pause
    
    # Export combined audio
    combined.export(combined_file, format="mp3")
    print(f"[tts]   ✅ Combined audio saved")
    
    return {
        "english": str(english_file),
        "spanish": str(spanish_file),
        "combined": str(combined_file),
        "duration": len(combined) / 1000.0  # Duration in seconds
    }


def generate_all_audio(phrases: list, output_dir: str = "audio"):
    """
    Generate audio for all phrases
    
    Returns list of audio info dicts
    """
    
    audio_files = []
    
    for i, phrase in enumerate(phrases):
        audio_info = generate_phrase_audio(phrase, output_dir, i)
        audio_files.append(audio_info)
    
    print(f"\n[tts] ✅ Generated audio for {len(phrases)} phrases")
    
    # Calculate total duration
    total_duration = sum(info["duration"] for info in audio_files)
    print(f"[tts] Total duration: {total_duration:.1f} seconds ({total_duration/60:.1f} minutes)")
    
    return audio_files


def create_final_narration(audio_files: list, output_file: str):
    """
    Combine all phrase audio into final narration with soft background music
    """
    
    print("[tts] Creating final narration...")
    
    # Combine all phrase audio
    combined = AudioSegment.empty()
    
    for audio_info in audio_files:
        combined_audio = AudioSegment.from_mp3(audio_info["combined"])
        combined += combined_audio
    
    # Load user's background music
    music_file = Path("music.mp3")
    
    if music_file.exists():
        print("[music] Loading background music from music.mp3...")
        background_music = AudioSegment.from_mp3(str(music_file))
        
        # Mix narration with background music (music VERY soft - barely noticeable)
        print("[music] Mixing narration with background music...")
        background_music = background_music - 25  # Reduce volume by 25dB (VERY soft)
        
        # Ensure background music matches narration length
        if len(background_music) < len(combined):
            # Loop background music if needed
            loops_needed = (len(combined) // len(background_music)) + 1
            background_music = background_music * loops_needed
        
        background_music = background_music[:len(combined)]
        
        # Mix together
        final_audio = combined.overlay(background_music)
    else:
        print("[music] ⚠️ music.mp3 not found, using narration only")
        final_audio = combined
    
    # Export
    Path(output_file).parent.mkdir(parents=True, exist_ok=True)
    final_audio.export(output_file, format="mp3", bitrate="192k")
    
    duration = len(final_audio) / 1000
    print(f"[tts] ✅ Final narration saved: {output_file}")
    print(f"[tts] Duration: {duration:.1f} seconds")
    
    return output_file


def generate_background_music(duration_ms: int):
    """
    Generate soft, beautiful piano-like background music
    Very low volume, calming melody
    """
    from pydub.generators import Sine, Square
    
    # Piano-like sound uses harmonics (fundamental + overtones)
    def piano_note(frequency, duration):
        """Create a piano-like note with harmonics"""
        # Fundamental frequency
        fundamental = Sine(frequency).to_audio_segment(duration=duration)
        
        # Add harmonics (overtones) for piano-like timbre
        harmonic2 = Sine(frequency * 2).to_audio_segment(duration=duration) - 12
        harmonic3 = Sine(frequency * 3).to_audio_segment(duration=duration) - 18
        harmonic4 = Sine(frequency * 4).to_audio_segment(duration=duration) - 24
        
        # Mix harmonics
        piano = fundamental.overlay(harmonic2).overlay(harmonic3).overlay(harmonic4)
        
        # Add envelope (attack, decay, sustain, release) for piano feel
        piano = piano.fade_in(50).fade_out(200)
        
        return piano
    
    # Beautiful, calming melody (C major scale pattern)
    # Note frequencies (in Hz)
    notes = {
        'C4': 261.63,
        'D4': 293.66,
        'E4': 329.63,
        'F4': 349.23,
        'G4': 392.00,
        'A4': 440.00,
        'B4': 493.88,
        'C5': 523.25
    }
    
    # Create a gentle, repeating melody (each note 1 second)
    note_duration = 1000  # 1 second per note
    
    # Melody pattern: C-E-G-E-F-D-E-C (peaceful, repetitive)
    melody_pattern = ['C4', 'E4', 'G4', 'E4', 'F4', 'D4', 'E4', 'C4']
    
    # Build melody
    melody = AudioSegment.silent(duration=0)
    
    for note_name in melody_pattern:
        note = piano_note(notes[note_name], note_duration)
        melody += note
    
    # Calculate how many times to loop
    melody_length = len(melody)
    loops_needed = (duration_ms // melody_length) + 1
    
    # Loop melody to match duration
    full_music = melody * loops_needed
    full_music = full_music[:duration_ms]
    
    # Add smooth fade in/out
    full_music = full_music.fade_in(3000).fade_out(3000)
    
    return full_music


if __name__ == "__main__":
    # Test TTS generation
    test_phrases = [
        {
            "english": "Good morning! How are you?",
            "spanish": "¡Buenos días! ¿Cómo estás?",
            "pronunciation": "BWEH-nos DEE-as KOH-moh es-TAHS"
        },
        {
            "english": "Thank you very much!",
            "spanish": "¡Muchas gracias!",
            "pronunciation": "MOO-chas GRAH-see-as"
        },
        {
            "english": "Where is the bathroom?",
            "spanish": "¿Dónde está el baño?",
            "pronunciation": "DOHN-deh es-TAH el BAH-nyoh"
        }
    ]
    
    # Generate audio for all phrases
    audio_files = generate_all_audio(test_phrases, "test_output/audio")
    
    # Create final narration
    create_final_narration(audio_files, "test_output/final_narration.mp3")
    
    print("\n✅ Test audio generation complete!")
