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
        file_size = video_path_obj.stat().st_size

        print(f"[instagram] Uploading video to Facebook servers (for Instagram...")
        page_id = os.getenv('FACEBOOK_PAGE_ID') or ig_user_id

        start_url = f"{api_base}/{page_id}/video_reels"
        start_data = {
            'access_token': access_token,
            'upload_phase': 'start',
            'file_size': file_size
        }
        res_start = requests.post(start_url, data=start_data, timeout=30)
        if res_start.status_code != 200:
            raise Exception(f"Start Failed: {res_start.text}")
        start_json = res_start.json()
        fb_video_id = start_json.get('video_id')
        fb_upload_url = start_json.get('upload_url')
        if not fb_video_id or not fb_upload_url:
            raise Exception(f"No video_id or upload_url: {start_json}")
        print(f"[instagram] Session started, video_id={fb_video_id}")

        headers = {
            'Authorization': f'OAuth {access_token}',
            'offset': '0',
            'file_size': str(file_size)
        }
        with open(video_path, 'rb') as f:
            res_transfer = requests.post(fb_upload_url, headers=headers, data=f, timeout=600)
        if res_transfer.status_code != 200:
            raise Exception(f"Transfer Failed: {res_transfer.text}")
        print(f"[instagram] Video transferred")

        print(f"[instagram] Publishing to Facebook + Instagram cross-post...")
        finish_url = f"{api_base}/{page_id}/video_reels"
        finish_data = {
            'access_token': access_token,
            'upload_phase': 'finish',
            'video_id': fb_video_id,
            'video_state': 'PUBLISHED',
            'instagram_visibility': 'PUBLISHED',
            'description': caption_limited
        }
        res_finish = requests.post(finish_url, data=finish_data, timeout=60)
        finish_json = res_finish.json()

        if res_finish.status_code == 200 and finish_json.get('success'):
            print(f"[instagram] SUCCESS! Video published to Facebook + Instagram!")
            print(f"[instagram] Video ID: {fb_video_id}")
            print("=" * 60)
            return {'id': str(fb_video_id), 'platform': 'instagram', 'status': 'success'}

        print(f"[instagram] Cross-post result: {finish_json}")
        print(f"[instagram] Cross-post not supported, falling back to IG container...")

        print(f"[instagram] Uploading to tmpfiles.org...")
        with open(video_path, 'rb') as f:
            tmp_resp = requests.post(
                'https://tmpfiles.org/api/v1/upload',
                files={'file': ('video.mp4', f, 'video/mp4')},
                timeout=180
            )
        if tmp_resp.status_code != 200:
            raise Exception(f"tmpfiles.org failed: {tmp_resp.status_code}")
        tmp_data = tmp_resp.json()
        if tmp_data.get('status') != 'success':
            raise Exception(f"tmpfiles.org failed: {tmp_data}")
        tmp_url = tmp_data.get('data', {}).get('url', '')
        video_url = tmp_url.replace('tmpfiles.org/', 'tmpfiles.org/dl/')
        print(f"[instagram] URL: {video_url}")

        print(f"[instagram] Creating Instagram {media_type} container...")
        container_params = {
            'media_type': media_type,
            'video_url': video_url,
            'access_token': access_token,
            'caption': caption_limited,
        }
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
            sr = requests.get(
                f"{api_base}/{container_id}",
                params={'fields': 'status_code', 'access_token': access_token},
                timeout=30
            )
            sc = sr.json().get('status_code', 'UNKNOWN')
            print(f"[instagram] {sc} ({waited}s)")
            if sc == 'FINISHED':
                print(f"[instagram] Processing complete!")
                break
            elif sc == 'ERROR':
                raise Exception(f"Processing failed")
            time.sleep(5)
            waited += 5

        print(f"[instagram] Publishing...")
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
            print(f"[instagram] Retry {attempt+1}")
            time.sleep(10)
        raise Exception(f"Publish failed: {pr.text if pr else 'No response'}")

    except Exception as e:
        print(f"[instagram] ERROR: {e}")
        print("=" * 60)
        raise

if __name__ == '__main__':
    video_file = Path('final_video.mp4')
    if video_file.exists():
        try:
            result = upload_to_instagram(str(video_file), "Test")
            print(f"\nSuccess! {result}")
        except Exception as e:
            print(f"\nFailed: {e}")
    else:
        print(f"Not found: {video_file}")