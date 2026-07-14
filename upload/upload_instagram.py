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

    print(f"[instagram] Credentials loaded")

    video_path_obj = Path(video_path)
    if not video_path_obj.exists():
        raise FileNotFoundError(f"Video file not found: {video_path}")

    file_size_mb = video_path_obj.stat().st_size / (1024 * 1024)
    print(f"[instagram] Video file found: {video_path}")
    print(f"[instagram] Video size: {file_size_mb:.2f} MB")

    caption_limited = caption[:2200] if len(caption) > 2200 else caption
    print(f"[instagram] Caption length: {len(caption_limited)} characters")

    try:
        api_base = "https://graph.facebook.com/v21.0"
        file_size = video_path_obj.stat().st_size

        print(f"[instagram] Step 1: Starting upload session...")
        start_url = f"{api_base}/{ig_user_id}/media"
        start_data = {
            'access_token': access_token,
            'media_type': media_type,
            'upload_phase': 'start',
            'file_size': file_size
        }
        if not is_story:
            start_data['caption'] = caption_limited

        res_start = requests.post(start_url, data=start_data, timeout=30)

        if res_start.status_code != 200:
            raise Exception(f"Start Phase Failed: {res_start.text}")

        start_json = res_start.json()
        video_id = start_json.get('video_id')
        upload_url = start_json.get('upload_url')

        if not video_id or not upload_url:
            raise Exception(f"No video_id or upload_url. Response: {start_json}")

        print(f"[instagram] Upload session started: video_id={video_id}")

        print(f"[instagram] Step 2: Uploading video directly to Instagram...")
        headers = {
            'Authorization': f'OAuth {access_token}',
            'offset': '0',
            'file_size': str(file_size)
        }
        with open(video_path, 'rb') as f:
            res_transfer = requests.post(upload_url, headers=headers, data=f, timeout=600)

        if res_transfer.status_code != 200:
            raise Exception(f"Transfer Phase Failed: {res_transfer.text}")

        print(f"[instagram] Video uploaded successfully")

        print(f"[instagram] Step 3: Finalizing container...")
        finish_url = f"{api_base}/{ig_user_id}/media"
        finish_data = {
            'access_token': access_token,
            'media_type': media_type,
            'upload_phase': 'finish',
            'video_id': video_id
        }
        if not is_story:
            finish_data['caption'] = caption_limited
            finish_data['share_to_feed'] = 'false'
            finish_data['thumb_offset'] = '5000'

        res_finish = requests.post(finish_url, data=finish_data, timeout=60)

        if res_finish.status_code != 200:
            raise Exception(f"Finish Phase Failed: {res_finish.text}")

        container_id = res_finish.json().get('id')
        print(f"[instagram] Container created: {container_id}")

        print(f"[instagram] Step 4: Waiting for video processing...")
        max_wait = 180
        waited = 0

        while waited < max_wait:
            status_url = f"{api_base}/{container_id}"
            status_params = {
                'fields': 'status_code',
                'access_token': access_token
            }
            status_response = requests.get(status_url, params=status_params, timeout=30)
            status_data = status_response.json()
            status_code = status_data.get('status_code', 'UNKNOWN')
            print(f"[instagram] Status: {status_code} (waited {waited}s)")
            if status_code == 'FINISHED':
                print(f"[instagram] Video processing complete!")
                break
            elif status_code == 'ERROR':
                error_msg = status_data.get('error_message', 'Video processing failed')
                raise Exception(error_msg)
            time.sleep(5)
            waited += 5

        if waited >= max_wait:
            print(f"[instagram] Processing timed out after {max_wait}s, attempting publish anyway...")

        print(f"[instagram] Step 5: Publishing to Instagram...")
        time.sleep(2)

        publish_url = f"{api_base}/{ig_user_id}/media_publish"
        publish_params = {
            'creation_id': container_id,
            'access_token': access_token
        }

        max_publish_retries = 3
        publish_response = None
        for attempt in range(max_publish_retries):
            publish_response = requests.post(publish_url, params=publish_params, timeout=60)
            if publish_response and publish_response.status_code == 200:
                break
            else:
                print(f"[instagram] Publish attempt {attempt+1} failed. Retrying...")
                time.sleep(10)

        if not publish_response or publish_response.status_code != 200:
            error_data = publish_response.json() if publish_response and publish_response.text else {}
            error_msg = error_data.get('error', {}).get('message', 'Unknown error')
            raise Exception(f"Instagram Publish Error: {error_msg}")

        media_id = publish_response.json().get('id')
        print(f"[instagram] SUCCESS! Video published to Instagram!")
        print(f"[instagram] Media ID: {media_id}")
        print("=" * 60)

        return {
            'id': media_id,
            'platform': 'instagram',
            'status': 'success'
        }

    except Exception as e:
        print(f"[instagram] ERROR!")
        print(f"[instagram] {str(e)}")
        print("=" * 60)
        raise

if __name__ == '__main__':
    video_file = Path('ielts_short.mp4')
    if video_file.exists():
        try:
            result = upload_to_instagram(str(video_file), "Test upload")
            print(f"\nSuccess! Result: {result}")
        except Exception as e:
            print(f"\nFailed: {e}")
    else:
        print(f"Video not found: {video_file}")