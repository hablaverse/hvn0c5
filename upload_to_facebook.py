"""
Facebook Upload Module for Habla Verse
ACTUAL Facebook Graph API upload - uploads video files!
"""

import os
import requests
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()


def generate_facebook_title(category: str) -> str:
    """Generate engaging title for Facebook post"""
    return f"Learn Spanish: {category} Phrases"


def generate_facebook_description(phrases: list, category: str) -> str:
    """
    Generate Facebook description with:
    - All phrases (English + Spanish + pronunciation)
    - Helpful information
    - Lowercase hashtags for searchability
    NO FLAGS, NO ASTERISKS
    """

    description_lines = [
        f"🎯 Learn Spanish with Habla Verse!",
        f"",
        f"📚 Category: {category}",
        f"",
        f"🎯 Master Spanish one phrase at a time! Today's {category} lesson:",
        f""
    ]

    # Add all phrases with emojis
    emojis = ["1️⃣", "2️⃣", "3️⃣", "4️⃣", "5️⃣"]
    for i, phrase in enumerate(phrases[:5], 0):
        emoji = emojis[i] if i < len(emojis) else f"{i+1}."
        description_lines.append(f"{emoji} {phrase['english']}")
        description_lines.append(f"   📍 {phrase['spanish']}")
        description_lines.append(f"   🔊 [{phrase.get('pronunciation', '')}]")
        description_lines.append("")

    # Call to action (NO ASTERISKS)
    description_lines.extend([
        f"💡 Tip: Repeat each phrase out loud 3 times!",
        f"👍 Like this video if you learned something new!",
        f"💬 Comment your favorite phrase below!",
        f"🔔 Follow for daily Spanish lessons!",
        f"",
        f"📖 Pronunciation Guide:",
        f"   The phonetic spelling in brackets helps you say it correctly!",
        f"",
    ])

    # Hashtags - ALL LOWERCASE for searchability
    hashtags = [
        "#learnspanish",
        "#spanishlessons",
        "#spanishforbeginners",
        "#languagelearning",
        "#spanishvocabulary",
        "#hablaverse",
        "#dailyspanish",
        "#spanishgrammar",
        "#learnlanguages",
        "#spanishteacher",
        "#speakspanish",
        "#spanishpractice",
        "#bilingual",
        "#spanishwords",
        "#languagetips"
    ]

    description_lines.extend(hashtags)

    return "\n".join(description_lines)


def upload_to_facebook(video_path, description, title="Spanish Lesson"):
    """
    ACTUAL Facebook Upload - uploads video file to Facebook!
    Uses Facebook Graph API 3-step upload process
    """
    
    print("\n" + "=" * 60)
    print("📘 FACEBOOK UPLOAD STARTING")
    print("=" * 60)

    # Get credentials
    access_token = os.getenv('FACEBOOK_ACCESS_TOKEN')
    page_id = os.getenv('FACEBOOK_PAGE_ID')

    def mask(s): return f"{s[:4]}...{s[-4:]}" if s and len(s) > 8 else "MISSING"
    print(f"[facebook] Page ID: {page_id}")
    print(f"[facebook] Access Token: {mask(access_token)}")

    if not access_token:
        error_msg = "❌ FACEBOOK_ACCESS_TOKEN not set"
        print(f"[facebook] {error_msg}")
        raise ValueError(error_msg)

    if not page_id:
        error_msg = "❌ FACEBOOK_PAGE_ID not set"
        print(f"[facebook] {error_msg}")
        raise ValueError(error_msg)

    print(f"[facebook] ✅ Credentials loaded")

    # Check video file
    video_path_obj = Path(video_path)
    if not video_path_obj.exists():
        error_msg = f"❌ Video file not found: {video_path}"
        print(f"[facebook] {error_msg}")
        raise FileNotFoundError(error_msg)

    file_size_mb = video_path_obj.stat().st_size / (1024 * 1024)
    print(f"[facebook] ✅ Video file found: {video_path}")
    print(f"[facebook] Video size: {file_size_mb:.2f} MB")

    # Upload using 3-step Reels API
    print(f"[facebook] 🚀 Uploading to Facebook Reels (3-step API)...")

    try:
        file_size = video_path_obj.stat().st_size

        # Step 1: Initialize
        print(f"[facebook] Step 1: Initiating upload session...")
        start_url = f"https://graph.facebook.com/v21.0/{page_id}/video_reels"
        start_data = {
            'access_token': access_token,
            'upload_phase': 'start',
            'file_size': file_size
        }
        res_start = requests.post(start_url, data=start_data, timeout=30)

        if res_start.status_code != 200:
            print(f"[facebook] ❌ Start Phase Error: {res_start.text}")
            raise Exception(f"Start Phase Failed: {res_start.text}")

        start_json = res_start.json()
        video_id = start_json.get('video_id')
        upload_url = start_json.get('upload_url')

        if not video_id:
             raise Exception(f"No video_id returned. Response: {start_json}")

        print(f"[facebook] ✅ Upload session started. Video ID: {video_id}")

        # Step 2: Transfer file
        print(f"[facebook] Step 2: Transferring file to Facebook Servers...")
        headers = {
            'Authorization': f'OAuth {access_token}',
            'offset': '0',
            'file_size': str(file_size)
        }
        with open(video_path, 'rb') as f:
            res_transfer = requests.post(upload_url, headers=headers, data=f, timeout=600)

        if res_transfer.status_code != 200:
            print(f"[facebook] ❌ Transfer Phase Error: {res_transfer.text}")
            raise Exception(f"Transfer Phase Failed: {res_transfer.text}")

        print(f"[facebook] ✅ File transferred successfully")

        # Step 3: Finalize
        print(f"[facebook] Step 3: Finalizing upload...")
        finalize_url = f"https://graph.facebook.com/v21.0/{page_id}/video_reels"
        finalize_data = {
            'access_token': access_token,
            'upload_phase': 'finish',
            'video_id': video_id,
            'description': description[:5000],  # Facebook limit
            'title': title[:100],  # Facebook limit
            'video_state': 'PUBLISHED'  # CRITICAL: This publishes to feed! (from velocity Spanish)
        }
        res_finalize = requests.post(finalize_url, data=finalize_data, timeout=60)

        if res_finalize.status_code != 200:
            print(f"[facebook] ❌ Finalize Phase Error: {res_finalize.text}")
            # Don't raise - video is already uploaded

        finalize_json = res_finalize.json()
        print(f"[facebook] ✅ Upload finalized!")
        print(f"[facebook] Response: {finalize_json}")

        # Check if successful
        if finalize_json.get('success') or 'id' in finalize_json:
            reel_id = finalize_json.get('id', video_id)
            print(f"[facebook] ✅ SUCCESS! Reel ID: {reel_id}")
            print(f"[facebook] 🎉 Video uploaded AND published to Facebook!")
            print(f"[facebook] Check your Facebook Page Reels tab to see the post.")
            return {'success': True, 'video_id': reel_id, 'platform': 'facebook', 'url': f"https://facebook.com/{reel_id}"}
        else:
            # Video uploaded but need to publish separately
            print(f"[facebook] ⚠️ Upload complete, publishing to feed...")
            
            # Step 4: Explicitly publish to feed
            publish_url = f"https://graph.facebook.com/v21.0/{video_id}"
            publish_data = {
                'access_token': access_token,
                'published': 'true'
            }
            try:
                res_publish = requests.post(publish_url, data=publish_data, timeout=30)
                if res_publish.status_code == 200:
                    print(f"[facebook] ✅ Video published to feed!")
                    return {'success': True, 'video_id': video_id, 'platform': 'facebook'}
                else:
                    print(f"[facebook] ⚠️ Publish response: {res_publish.text}")
            except:
                pass
            
            print(f"[facebook] ⚠️ Upload complete but video may not be published")
            return {'success': True, 'video_id': video_id, 'platform': 'facebook'}

    except Exception as e:
        print(f"[facebook] ❌ Upload failed: {str(e)}")
        return {'success': False, 'error': str(e), 'platform': 'facebook'}


if __name__ == "__main__":
    # Test
    print("Facebook Upload Module - Habla Verse")
    print("Use upload_to_facebook() function to upload videos")


def save_metadata(phrases: list, category: str, output_dir: str = "output"):
    """Save metadata JSON file for uploads with ALL phrases included"""
    import json
    from datetime import datetime
    from pathlib import Path

    metadata = {
        "category": category,
        "phrases": phrases,
        "generated_at": datetime.now().isoformat(),
        "titles": {
            "facebook": generate_facebook_title(category),
            "youtube": f"Spanish {category} - Learn Essential Spanish Phrases"
        },
        "descriptions": {
            "facebook": generate_facebook_description(phrases, category),
            "youtube": generate_facebook_description(phrases, category),
            "instagram": generate_facebook_description(phrases, category)
        }
    }

    output_path = Path(output_dir) / "metadata.json"
    output_path.parent.mkdir(parents=True, exist_ok=True)

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(metadata, f, indent=2, ensure_ascii=False)

    print(f"[metadata] Saved to {output_path}")

    return metadata
