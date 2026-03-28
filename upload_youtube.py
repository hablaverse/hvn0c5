"""
YouTube Upload Script
Uploads videos to YouTube with proper metadata
"""

import os
import pickle
from pathlib import Path
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from dotenv import load_dotenv

load_dotenv()

SCOPES = ['https://www.googleapis.com/auth/youtube.upload']

def get_authenticated_service():
    """Get authenticated YouTube service"""
    creds = None
    
    # Try to load credentials from pickle file
    token_file = Path('token.pickle')
    if token_file.exists():
        with open(token_file, 'rb') as token:
            creds = pickle.load(token)
    
    # If no valid credentials, try to get them
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            # Try OAuth flow
            client_id = os.getenv('YOUTUBE_CLIENT_ID')
            client_secret = os.getenv('YOUTUBE_CLIENT_SECRET')
            refresh_token = os.getenv('YOUTUBE_REFRESH_TOKEN')
            
            if client_id and client_secret and refresh_token:
                creds = Credentials(
                    None,
                    refresh_token=refresh_token,
                    token_uri='https://oauth2.googleapis.com/token',
                    client_id=client_id,
                    client_secret=client_secret,
                    scopes=SCOPES
                )
            else:
                print("[youtube] ⚠️ No YouTube credentials configured")
                return None
        
        # Save credentials for future use
        with open(token_file, 'wb') as token:
            pickle.dump(creds, token)
    
    return build('youtube', 'v3', credentials=creds)


def upload_video(video_file: str, title: str, description: str, tags: list = None):
    """Upload video to YouTube"""
    
    print(f"[youtube] Uploading: {title}")
    
    youtube = get_authenticated_service()
    
    if not youtube:
        return None
    
    # Prepare video metadata
    body = {
        'snippet': {
            'title': title[:100],  # YouTube title limit
            'description': description[:5000],  # YouTube description limit
            'tags': tags or ['Learn Spanish', 'Spanish Lessons', 'Language Learning'],
            'categoryId': '27'  # Education category
        },
        'status': {
            'privacyStatus': 'public',  # Options: public, private, unlisted
            'selfDeclaredMadeForKids': False
        }
    }
    
    # Upload video
    media = MediaFileUpload(video_file, mimetype='video/mp4', resumable=True)
    
    try:
        request = youtube.videos().insert(
            part=','.join(body.keys()),
            body=body,
            media_body=media
        )
        
        response = request.execute()
        
        video_id = response.get('id')
        video_url = f"https://youtu.be/{video_id}"
        
        print(f"[youtube] ✅ Uploaded! Video ID: {video_id}")
        print(f"[youtube] URL: {video_url}")
        
        return {'video_id': video_id, 'video_url': video_url, 'platform': 'youtube'}
        
    except Exception as e:
        print(f"[youtube] ❌ Error: {str(e)}")
        return None


def generate_video_metadata(category: str, num_phrases: int):
    """Generate YouTube title, description, and tags"""
    
    title = f"Learn Spanish: {num_phrases} {category} Phrases 🇪🇸"
    
    description = f"""Learn {num_phrases} essential Spanish phrases for {category}!

✅ English phrase
✅ Spanish translation  
✅ Pronunciation guide

Perfect for beginners who want to improve their Spanish skills!

#LearnSpanish #SpanishLessons #LanguageLearning #Education #Spanish"""
    
    tags = [
        'Learn Spanish',
        'Spanish Lessons',
        'Language Learning',
        'Spanish for Beginners',
        'Spanish Phrases',
        'Education',
        category
    ]
    
    return title, description, tags


if __name__ == "__main__":
    print("YouTube upload module ready")
    print("Configure credentials in .env or run OAuth flow first")
