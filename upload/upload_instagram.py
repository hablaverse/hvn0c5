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
    fb_page_id = os.getenv('FACEBOOK_PAGE_ID')

    def mask(s): return f"{s[:10]}...{s[-4:]}" if s and len(s) > 10 else ("PLACEHOLDER" if s == "***" else "MISSING")
    print(f"[instagram] IG User ID: {ig_user_id}")
    print(f"[instagram] FB Page ID: {fb_page_id}")
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
        video_url = None

        if access_token.startswith('IGAA'):
            print(f"[instagram] Detected IGAA token - using temporary hosting upload")
            with open(video_path_obj, 'rb') as video_file:
                files = {'file': ('video.mp4', video_file, 'video/mp4')}
                temp_response = requests.post(
                    'https://tmpfiles.org/api/v1/upload',
                    files=files,
                    timeout=180
                )
            if temp_response.status_code != 200:
                raise Exception(f"Failed to upload to temporary hosting: {temp_response.status_code}")
            temp_data = temp_response.json()
            if temp_data.get('status') != 'success':
                raise Exception(f"Temporary hosting failed: {temp_data}")
            temp_url = temp_data.get('data', {}).get('url', '')
            video_url = temp_url.replace('tmpfiles.org/', 'tmpfiles.org/dl/')
            print(f"[instagram] Temporary URL created: {video_url}")
        else:
            print(f"[instagram] Detected Facebook Page token - using Facebook direct upload")

            page_id_for_upload = fb_page_id or ig_user_id
            print(f"[instagram] Using page_id={page_id_for_upload} for video upload")

            file_size = video_path_obj.stat().st_size

            print(f"[instagram] Step 1: Initiating upload session on Facebook...")
            start_url = f"https://graph.facebook.com/v21.0/{page_id_for_upload}/video_reels"
            start_data = {
                'access_token': access_token,
                'upload_phase': 'start',
                'file_size': file_size
            }
            res_start = requests.post(start_url, data=start_data, timeout=30)

            if res_start.status_code != 200:
                raise Exception(f"Upload Start Phase Failed: {res_start.text}")

            start_json = res_start.json()
            video_id = start_json.get('video_id')
            upload_url = start_json.get('upload_url')

            if not video_id:
                raise Exception(f"No video_id returned. Response: {start_json}")

            print(f"[instagram] Step 2: Transferring file to Facebook servers...")
            headers = {
                'Authorization': f'OAuth {access_token}',
                'offset': '0',
                'file_size': str(file_size)
            }
            with open(video_path, 'rb') as f:
                res_transfer = requests.post(upload_url, headers=headers, data=f, timeout=600)

            if res_transfer.status_code != 200:
                raise Exception(f"Upload Transfer Phase Failed: {res_transfer.text}")

            print(f"[instagram] Step 3: Finalizing upload...")
            finish_url = f"https://graph.facebook.com/v21.0/{page_id_for_upload}/video_reels"
            finish_data = {
                'access_token': access_token,
                'upload_phase': 'finish',
                'video_id': video_id,
                'video_state': 'PUBLISHED'
            }
            res_finish = requests.post(finish_url, data=finish_data, timeout=60)

            if res_finish.status_code != 200:
                raise Exception(f"Upload Finish Phase Failed: {res_finish.text}")

            print(f"[instagram] Video uploaded to Facebook servers, video_id={video_id}")

            print(f"[instagram] Fetching video source URL...")
            video_url_resp = requests.get(
                f"https://graph.facebook.com/v21.0/{video_id}",
                params={'fields': 'source', 'access_token': access_token},
                timeout=30
            )
            if video_url_resp.status_code == 200:
                video_data = video_url_resp.json()
                video_url = video_data.get('source')
                print(f"[instagram] Facebook response: {video_data}")

            if not video_url:
                print(f"[instagram] Source URL not available, using catbox.moe instead")
                print(f"[instagram] Uploading to catbox.moe for reliable hosting...")
                with open(video_path, 'rb') as f:
                    cb_response = requests.post(
                        'https://catbox.moe/user/api.php',
                        data={'reqtype': 'fileupload'},
                        files={'fileToUpload': f},
                        timeout=180
                    )
                if cb_response.status_code == 200 and cb_response.text.strip():
                    video_url = cb_response.text.strip()
                    print(f"[instagram] catbox.moe URL: {video_url}")
                else:
                    raise Exception(f"catbox.moe upload failed: {cb_response.status_code} {cb_response.text}")

        print(f"[instagram] Step 4: Creating Instagram {media_type} container...")
        container_url = f"https://graph.facebook.com/v21.0/{ig_user_id}/media"
        container_params = {
            'media_type': media_type,
            'video_url': video_url,
            'access_token': access_token
        }
        if not is_story:
            container_params['caption'] = caption_limited
            container_params['share_to_feed'] = 'false'
            container_params['thumb_offset'] = '5000'

        container_response = requests.post(container_url, params=container_params, timeout=60)

        if container_response.status_code != 200:
            container_error = container_response.json() if container_response.text else {}
            error_msg = container_error.get('error', {}).get('message', 'Unknown error')
            print(f"[instagram] Container creation failed: {error_msg}")
            print(f"[instagram] Full response: {container_response.text[:500]}")
            raise Exception(f"Instagram Container Error: {error_msg}")

        container_id = container_response.json().get('id')
        print(f"[instagram] Container created: {container_id}")

        print(f"[instagram] Step 5: Waiting for video processing...")
        max_wait = 120
        waited = 0

        while waited < max_wait:
            status_url = f"https://graph.facebook.com/v21.0/{container_id}"
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

        print(f"[instagram] Step 6: Publishing to Instagram...")
        time.sleep(2)

        publish_url = f"https://graph.facebook.com/v21.0/{ig_user_id}/media_publish"
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