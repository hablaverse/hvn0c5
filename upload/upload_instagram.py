import os
import requests
import time
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

def upload_to_instagram(video_path, caption, is_story=False):
    media_type = 'STORIES' if is_story else 'REELS'

    print("\n" + "=" * 60)
    print(f"INSTAGRAM {media_type} UPLOAD STARTING")
    print("=" * 60)

    access_token = os.getenv('INSTAGRAM_ACCESS_TOKEN') or os.getenv('FACEBOOK_ACCESS_TOKEN')
    ig_user_id = os.getenv('INSTAGRAM_ACCOUNT_ID') or os.getenv('IG_USER_ID')

    def mask(s): return f"{s[:10]}...{s[-4:]}" if s and len(s) > 10 else ("PLACEHOLDER" if s == "***" else "MISSING")
    print(f"[instagram] IG User ID: {ig_user_id}")
    print(f"[instagram] Access Token: {mask(access_token)}")

    if not access_token:
        raise ValueError("INSTAGRAM_ACCESS_TOKEN not set")
    if not ig_user_id:
        raise ValueError("INSTAGRAM_ACCOUNT_ID not set")

    video_path_obj = Path(video_path)
    if not video_path_obj.exists():
        raise FileNotFoundError(f"Video file not found: {video_path}")

    file_size_mb = video_path_obj.stat().st_size / (1024 * 1024)
    print(f"[instagram] Video size: {file_size_mb:.2f} MB")

    caption_limited = caption[:2200] if len(caption) > 2200 else caption

    try:
        api_base = "https://graph.facebook.com/v21.0"

        print(f"[instagram] Uploading to file hosting...")
        with open(video_path, 'rb') as f:
            r = requests.put(
                'https://transfer.sh/video.mp4',
                data=f,
                timeout=300
            )
        if r.status_code == 200 and r.text.strip():
            video_url = r.text.strip()
            print(f"[instagram] transfer.sh URL: {video_url}")
        else:
            print(f"[instagram] transfer.sh failed ({r.status_code}), trying tmpfiles.org...")
            with open(video_path, 'rb') as f:
                r = requests.post(
                    'https://tmpfiles.org/api/v1/upload',
                    files={'file': ('video.mp4', f, 'video/mp4')},
                    timeout=180
                )
            if r.status_code != 200:
                raise Exception(f"Upload failed: {r.status_code}")
            tmp_data = r.json()
            if tmp_data.get('status') != 'success':
                raise Exception(f"tmpfiles.org failed: {tmp_data}")
            tmp_url = tmp_data.get('data', {}).get('url', '')
            video_url = tmp_url.replace('tmpfiles.org/', 'tmpfiles.org/dl/')
            print(f"[instagram] tmpfiles.org URL: {video_url}")

        print(f"[instagram] Creating Instagram {media_type} container...")
        container_params = {
            'media_type': media_type,
            'video_url': video_url,
            'access_token': access_token
        }
        if not is_story:
            container_params['caption'] = caption_limited

        container_response = requests.post(
            f"{api_base}/{ig_user_id}/media",
            params=container_params,
            timeout=60
        )

        if container_response.status_code != 200:
            raise Exception(f"Container Error: {container_response.text}")

        container_id = container_response.json().get('id')
        print(f"[instagram] Container: {container_id}")

        print(f"[instagram] Processing...")
        max_wait = 300
        waited = 0
        while waited < max_wait:
            status_response = requests.get(
                f"{api_base}/{container_id}",
                params={'fields': 'status_code', 'access_token': access_token},
                timeout=30
            )
            status_code = status_response.json().get('status_code', 'UNKNOWN')
            print(f"[instagram] {status_code} ({waited}s)")
            if status_code == 'FINISHED':
                print(f"[instagram] Processing complete!")
                break
            elif status_code == 'ERROR':
                raise Exception(f"Processing failed: {status_response.json().get('error_message', 'Unknown')}")
            time.sleep(5)
            waited += 5

        print(f"[instagram] Publishing...")
        time.sleep(2)
        for attempt in range(3):
            pr = requests.post(
                f"{api_base}/{ig_user_id}/media_publish",
                params={'creation_id': container_id, 'access_token': access_token},
                timeout=60
            )
            if pr.status_code == 200:
                media_id = pr.json().get('id')
                print(f"[instagram] SUCCESS! Media ID: {media_id}")
                print("=" * 60)
                return {'id': media_id, 'platform': 'instagram', 'status': 'success'}
            print(f"[instagram] Retry {attempt+1}...")
            time.sleep(10)
        raise Exception(f"Publish failed: {pr.text}")

    except Exception as e:
        print(f"[instagram] ERROR: {e}")
        print("=" * 60)
        raise