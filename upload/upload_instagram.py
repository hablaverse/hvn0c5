import os
import json
from pathlib import Path
from dotenv import load_dotenv
from instagrapi import Client
from instagrapi.exceptions import LoginRequired, ClientError

load_dotenv()

def upload_to_instagram(video_path, caption, is_story=False):
    print("\n" + "=" * 60)
    print("INSTAGRAM REELS UPLOAD STARTING")
    print("=" * 60)

    username = os.getenv('INSTAGRAM_USERNAME')
    password = os.getenv('INSTAGRAM_PASSWORD')
    session_file = Path('instagram_session.json')

    if not username or not password:
        raise ValueError("INSTAGRAM_USERNAME and INSTAGRAM_PASSWORD must be set in .env")

    video_path_obj = Path(video_path)
    if not video_path_obj.exists():
        raise FileNotFoundError(f"Video not found: {video_path}")

    cl = Client()
    cl.delay_range = [1, 3]

    try:
        if session_file.exists():
            with open(session_file) as f:
                cl.set_settings(json.load(f))
            cl.login(username, password)
            print(f"[instagram] Logged in using saved session")
        else:
            cl.login(username, password)
            with open(session_file, 'w') as f:
                json.dump(cl.get_settings(), f)
            print(f"[instagram] Logged in and saved session")

        print(f"[instagram] Uploading video: {video_path}")
        print(f"[instagram] Size: {video_path_obj.stat().st_size / 1024 / 1024:.2f} MB")

        if is_story:
            result = cl.story_upload(video_path, caption=caption[:2200])
            print(f"[instagram] Story uploaded! ID: {result.id}")
        else:
            result = cl.clip_upload(video_path, caption=caption[:2200])
            print(f"[instagram] Reel uploaded! ID: {result.id}")

        print(f"[instagram] SUCCESS! Video published!")
        print("=" * 60)

        with open(session_file, 'w') as f:
            json.dump(cl.get_settings(), f)

        return {
            'id': str(result.id),
            'platform': 'instagram',
            'status': 'success'
        }

    except LoginRequired:
        print(f"[instagram] Session expired, logging in fresh...")
        if session_file.exists():
            session_file.unlink()
        cl.login(username, password)
        return upload_to_instagram(video_path, caption, is_story)

    except ClientError as e:
        print(f"[instagram] Instagram API error: {e}")
        raise

    except Exception as e:
        print(f"[instagram] ERROR: {e}")
        print("=" * 60)
        raise

if __name__ == '__main__':
    video_file = Path('final_video.mp4')
    if video_file.exists():
        try:
            result = upload_to_instagram(str(video_file), "Test upload via instagrapi")
            print(f"\nSuccess! Result: {result}")
        except Exception as e:
            print(f"\nFailed: {e}")
    else:
        print(f"Video not found: {video_file}")