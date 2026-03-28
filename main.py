"""
HablaVerse - Main Automation Script
Generates video AND uploads to all social media platforms
"""

import os
import sys
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

print("="*80)
print("🇪🇸 HABLAVERSE - AUTOMATED SPANISH LEARNING BOT")
print("="*80)
print()

# Step 1: Generate video
print("[1/2] GENERATING VIDEO...")
print("="*80)

try:
    from generate_video_robust import generate_video
    video_path = generate_video()
    
    if not video_path:
        print("\n❌ Video generation failed!")
        sys.exit(1)
    
    print(f"\n✅ Video generated: {video_path}")
    print()
    
except Exception as e:
    print(f"\n❌ Video generation error: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# Step 2: Upload to all platforms
print("\n[2/2] UPLOADING TO SOCIAL MEDIA...")
print("="*80)

try:
    from upload_all_platforms import main as upload_main
    upload_main()
    
except Exception as e:
    print(f"\n❌ Upload error: {e}")
    import traceback
    traceback.print_exc()
    # Continue anyway - video was generated successfully
    print("\n⚠️  Upload failed, but video was generated successfully!")
    print(f"   Video location: {video_path}")
    sys.exit(0)

print("\n" + "="*80)
print("✅ HABLAVERSE - COMPLETE!")
print("="*80)
print()
print("🎉 Video generated AND uploaded to all platforms!")
print()
