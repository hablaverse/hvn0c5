"""
HablaVerse - Multi-Platform Upload Script
Uploads to Facebook, Instagram, YouTube, Twitter, Telegram, VK, Threads, TikTok

All upload modules are now integrated from the upload/ folder
"""

import os
import sys
import json
from pathlib import Path
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

# Import all upload modules from upload/ folder
try:
    from upload.upload_to_youtube import upload_to_youtube
    YOUTUBE_AVAILABLE = True
except ImportError as e:
    YOUTUBE_AVAILABLE = False
    print(f"[warning] YouTube upload module not available: {e}")

# Import rich description generator from root folder (for Facebook)
try:
    from upload_to_facebook import generate_facebook_description, generate_facebook_title
    print("[info] Using rich Facebook description from root folder")
except ImportError as e:
    print(f"[warning] Using fallback description: {e}")
    def generate_facebook_title(category): return f"Learn Spanish: {category} Phrases"
    def generate_facebook_description(phrases, category): return f"Learn Spanish: {category}"

try:
    from upload.upload_instagram import upload_to_instagram
    INSTAGRAM_AVAILABLE = True
except ImportError as e:
    INSTAGRAM_AVAILABLE = False
    print(f"[warning] Instagram upload module not available: {e}")

try:
    from upload.upload_facebook import upload_to_facebook, upload_to_facebook_story
    FACEBOOK_AVAILABLE = True
except ImportError as e:
    FACEBOOK_AVAILABLE = False
    print(f"[warning] Facebook upload module not available: {e}")

try:
    from upload.upload_twitter import upload_to_twitter
    TWITTER_AVAILABLE = True
except ImportError as e:
    TWITTER_AVAILABLE = False
    print(f"[warning] Twitter upload module not available: {e}")

try:
    from upload.upload_telegram import upload_to_telegram
    TELEGRAM_AVAILABLE = True
except ImportError as e:
    TELEGRAM_AVAILABLE = False
    print(f"[warning] Telegram upload module not available: {e}")

try:
    from upload.upload_vk import upload_to_vk
    VK_AVAILABLE = True
except ImportError as e:
    VK_AVAILABLE = False
    print(f"[warning] VK upload module not available: {e}")

try:
    from upload.upload_threads import upload_to_threads
    THREADS_AVAILABLE = True
except ImportError as e:
    THREADS_AVAILABLE = False
    print(f"[warning] Threads upload module not available: {e}")

try:
    from upload.upload_tiktok import upload_to_tiktok
    TIKTOK_AVAILABLE = True
except ImportError as e:
    TIKTOK_AVAILABLE = False
    print(f"[warning] TikTok upload module not available: {e}")


def get_latest_video():
    """Find the most recently generated video"""
    video_dir = Path("output")

    if not video_dir.exists():
        print("❌ No output directory found")
        return None

    videos = list(video_dir.glob("final_video.mp4"))

    if not videos:
        print("❌ No videos found in output directory")
        return None

    latest = max(videos, key=lambda p: p.stat().st_mtime)

    metadata_file = latest.parent / "metadata.json"
    metadata = {}
    if metadata_file.exists():
        with open(metadata_file, "r", encoding="utf-8") as f:
            metadata = json.load(f)

    return {
        "video_path": str(latest),
        "metadata": metadata,
        "category": metadata.get("category", "Spanish Learning"),
        "phrases": metadata.get("phrases", [])
    }


def generate_platform_metadata(category, phrases):
    """Generate platform-specific titles and descriptions"""

    # Use RICH Facebook description (from root folder) as the base for all platforms
    fb_description = generate_facebook_description(phrases, category)
    fb_title = generate_facebook_title(category)

    # Simple phrases text for other platforms
    phrases_text = "\n".join([f"• {p['english']} → {p['spanish']}" for p in phrases[:5]])

    return {
        "youtube": {
            "title": f"{fb_title} 🇪🇸 #Shorts",
            "description": fb_description + "\n\n#SpanishPhrases #Education #Shorts",
            "tags": ["Learn Spanish", "Spanish Lessons", "Language Learning", category, "Spanish Phrases"]
        },
        "instagram": {
            "caption": fb_description + "\n\n#Reels #SpanishReels #LearnOnInstagram"
        },
        "facebook": {
            "title": fb_title,
            "description": fb_description
        },
        "twitter": {
            "caption": f"🇪🇸 {fb_title}\n\n{phrases[0]['english'] if phrases else ''} → {phrases[0]['spanish'] if phrases else ''}\n\n#LearnSpanish #Spanish"
        },
        "telegram": {
            "caption": f"🇪🇸 <b>{fb_title}</b>\n\n{phrases_text}\n\n💡 Repeat each phrase out loud 3 times!"
        },
        "vk": {
            "title": fb_title,
            "description": fb_description
        },
        "threads": {
            "text": f"🇪🇸 {fb_title}\n\n{phrases[0]['english'] if phrases else ''} → {phrases[0]['spanish'] if phrases else ''}\n\n#LearnSpanish"
        },
        "tiktok": {
            "description": f"🇪🇸 Learn Spanish: {category} #LearnSpanish #Spanish #LanguageLearning #Education"
        }
    }


def upload_to_all_platforms(video_path, metadata, category):
    """Upload to all configured social media platforms"""

    results = {
        "timestamp": datetime.now().isoformat(),
        "category": category,
        "video": video_path,
        "uploads": {},
        "platforms_attempted": [],
        "platforms_successful": [],
        "platforms_failed": [],
        "platforms_skipped": []
    }

    print("\n" + "="*80)
    print("🚀 HABLAVERSE - MULTI-PLATFORM UPLOAD")
    print("="*80)
    print(f"Video: {video_path}")
    print(f"Category: {category}")
    print("="*80)

    if not Path(video_path).exists():
        print(f"❌ Video file not found: {video_path}")
        return results

    # Generate platform-specific metadata
    platform_meta = generate_platform_metadata(category, metadata.get("phrases", []))

    # ===== YOUTUBE =====
    print(f"\n📺 YOUTUBE UPLOAD...")
    results["platforms_attempted"].append("youtube")

    if YOUTUBE_AVAILABLE:
        yt_client_id = os.getenv("YOUTUBE_CLIENT_ID")
        yt_client_secret = os.getenv("YOUTUBE_CLIENT_SECRET")
        yt_refresh_token = os.getenv("YOUTUBE_REFRESH_TOKEN")

        if yt_client_id and yt_client_secret and yt_refresh_token:
            print(f"   ✅ Credentials found")
            try:
                upload_result = upload_to_youtube(
                    video_path=video_path,
                    title=platform_meta["youtube"]["title"],
                    description=platform_meta["youtube"]["description"],
                    tags=platform_meta["youtube"]["tags"]
                )
                results["uploads"]["youtube"] = {"status": "success", "result": upload_result}
                results["platforms_successful"].append("youtube")
                print(f"   ✅ YouTube upload successful")
            except Exception as e:
                print(f"   ❌ YouTube upload failed: {e}")
                results["uploads"]["youtube"] = {"status": "failed", "error": str(e)}
                results["platforms_failed"].append("youtube")
        else:
            print(f"   ⚠️  No YouTube credentials (skipped)")
            results["uploads"]["youtube"] = {"status": "skipped", "reason": "No credentials"}
            results["platforms_skipped"].append("youtube")
    else:
        print(f"   ❌ YouTube module not available")
        results["uploads"]["youtube"] = {"status": "failed", "error": "Module not available"}
        results["platforms_failed"].append("youtube")

    # ===== INSTAGRAM =====
    print(f"\n📸 INSTAGRAM UPLOAD...")
    results["platforms_attempted"].append("instagram")

    if INSTAGRAM_AVAILABLE:
        ig_token = os.getenv("INSTAGRAM_ACCESS_TOKEN")
        ig_account_id = os.getenv("INSTAGRAM_ACCOUNT_ID")

        if ig_token and ig_account_id:
            print(f"   ✅ Credentials found")
            try:
                upload_result = upload_to_instagram(
                    video_path=video_path,
                    caption=platform_meta["instagram"]["caption"],
                    is_story=False
                )
                results["uploads"]["instagram"] = {"status": "success", "result": upload_result}
                results["platforms_successful"].append("instagram")
                print(f"   ✅ Instagram upload successful")
            except Exception as e:
                print(f"   ❌ Instagram upload failed: {e}")
                results["uploads"]["instagram"] = {"status": "failed", "error": str(e)}
                results["platforms_failed"].append("instagram")
        else:
            print(f"   ⚠️  No Instagram credentials (skipped)")
            results["uploads"]["instagram"] = {"status": "skipped", "reason": "No credentials"}
            results["platforms_skipped"].append("instagram")
    else:
        print(f"   ❌ Instagram module not available")
        results["uploads"]["instagram"] = {"status": "failed", "error": "Module not available"}
        results["platforms_failed"].append("instagram")

    # ===== INSTAGRAM STORY =====
    print(f"\n📸 INSTAGRAM STORY UPLOAD...")
    results["platforms_attempted"].append("instagram_story")

    if INSTAGRAM_AVAILABLE:
        ig_token = os.getenv("INSTAGRAM_ACCESS_TOKEN")
        ig_account_id = os.getenv("INSTAGRAM_ACCOUNT_ID")

        if ig_token and ig_account_id:
            print(f"   ✅ Credentials found")
            try:
                upload_result = upload_to_instagram(
                    video_path=video_path,
                    caption=platform_meta["instagram"]["caption"],
                    is_story=True
                )
                if upload_result.get("status") == "success":
                    results["uploads"]["instagram_story"] = {"status": "success", "result": upload_result}
                    results["platforms_successful"].append("instagram_story")
                    print(f"   ✅ Instagram Story upload successful")
                else:
                    results["uploads"]["instagram_story"] = {"status": "failed", "error": upload_result}
                    results["platforms_failed"].append("instagram_story")
                    print(f"   ❌ Instagram Story upload failed")
            except Exception as e:
                print(f"   ❌ Instagram Story upload failed: {e}")
                results["uploads"]["instagram_story"] = {"status": "failed", "error": str(e)}
                results["platforms_failed"].append("instagram_story")
        else:
            print(f"   ⚠️  No Instagram credentials (skipped)")
            results["uploads"]["instagram_story"] = {"status": "skipped", "reason": "No credentials"}
            results["platforms_skipped"].append("instagram_story")
    else:
        print(f"   ❌ Instagram module not available")
        results["uploads"]["instagram_story"] = {"status": "failed", "error": "Module not available"}
        results["platforms_failed"].append("instagram_story")

    # ===== FACEBOOK =====
    print(f"\n📘 FACEBOOK UPLOAD...")
    results["platforms_attempted"].append("facebook")

    if FACEBOOK_AVAILABLE:
        fb_token = os.getenv("FACEBOOK_ACCESS_TOKEN")
        fb_page_id = os.getenv("FACEBOOK_PAGE_ID")

        if fb_token and fb_page_id:
            print(f"   ✅ Credentials found")
            try:
                # Use RICH description from root folder (with all phrases)
                fb_description = generate_facebook_description(
                    metadata.get("phrases", []),
                    category
                )
                fb_title = generate_facebook_title(category)
                
                upload_result = upload_to_facebook(
                    video_path=video_path,
                    description=fb_description,
                    title=fb_title
                )
                results["uploads"]["facebook"] = {"status": "success", "result": upload_result}
                results["platforms_successful"].append("facebook")
                print(f"   ✅ Facebook upload successful")
            except Exception as e:
                print(f"   ❌ Facebook upload failed: {e}")
                results["uploads"]["facebook"] = {"status": "failed", "error": str(e)}
                results["platforms_failed"].append("facebook")
        else:
            print(f"   ⚠️  No Facebook credentials (skipped)")
            results["uploads"]["facebook"] = {"status": "skipped", "reason": "No credentials"}
            results["platforms_skipped"].append("facebook")
    else:
        print(f"   ❌ Facebook module not available")
        results["uploads"]["facebook"] = {"status": "failed", "error": "Module not available"}
        results["platforms_failed"].append("facebook")

    # ===== FACEBOOK STORY =====
    print(f"\n📘 FACEBOOK STORY UPLOAD...")
    results["platforms_attempted"].append("facebook_story")

    if FACEBOOK_AVAILABLE:
        fb_token = os.getenv("FACEBOOK_ACCESS_TOKEN")
        fb_page_id = os.getenv("FACEBOOK_PAGE_ID")

        if fb_token and fb_page_id:
            print(f"   ✅ Credentials found")
            try:
                upload_result = upload_to_facebook_story(video_path=video_path)
                results["uploads"]["facebook_story"] = {"status": "success", "result": upload_result}
                results["platforms_successful"].append("facebook_story")
                print(f"   ✅ Facebook Story upload successful")
            except Exception as e:
                print(f"   ❌ Facebook Story upload failed: {e}")
                results["uploads"]["facebook_story"] = {"status": "failed", "error": str(e)}
                results["platforms_failed"].append("facebook_story")
        else:
            print(f"   ⚠️  No Facebook credentials (skipped)")
            results["uploads"]["facebook_story"] = {"status": "skipped", "reason": "No credentials"}
            results["platforms_skipped"].append("facebook_story")
    else:
        print(f"   ❌ Facebook module not available")
        results["uploads"]["facebook_story"] = {"status": "failed", "error": "Module not available"}
        results["platforms_failed"].append("facebook_story")

    # ===== TWITTER/X =====
    print(f"\n🐦 TWITTER/X UPLOAD...")
    results["platforms_attempted"].append("twitter")

    if TWITTER_AVAILABLE:
        twitter_key = os.getenv("TWITTER_API_KEY")
        twitter_secret = os.getenv("TWITTER_API_SECRET")
        twitter_token = os.getenv("TWITTER_ACCESS_TOKEN")
        twitter_secret_token = os.getenv("TWITTER_ACCESS_SECRET")

        if twitter_key and twitter_secret and twitter_token and twitter_secret_token:
            print(f"   ✅ Credentials found")
            try:
                upload_result = upload_to_twitter(
                    video_path=video_path,
                    caption=platform_meta["twitter"]["caption"]
                )
                results["uploads"]["twitter"] = {"status": "success", "result": upload_result}
                results["platforms_successful"].append("twitter")
                print(f"   ✅ Twitter upload successful")
            except Exception as e:
                print(f"   ❌ Twitter upload failed: {e}")
                results["uploads"]["twitter"] = {"status": "failed", "error": str(e)}
                results["platforms_failed"].append("twitter")
        else:
            print(f"   ⚠️  No Twitter credentials (skipped)")
            results["uploads"]["twitter"] = {"status": "skipped", "reason": "No credentials"}
            results["platforms_skipped"].append("twitter")
    else:
        print(f"   ❌ Twitter module not available")
        results["uploads"]["twitter"] = {"status": "failed", "error": "Module not available"}
        results["platforms_failed"].append("twitter")

    # ===== TELEGRAM =====
    print(f"\n📱 TELEGRAM UPLOAD...")
    results["platforms_attempted"].append("telegram")

    if TELEGRAM_AVAILABLE:
        tg_token = os.getenv("TELEGRAM_BOT_TOKEN")
        tg_channel = os.getenv("TELEGRAM_CHANNEL_ID")

        if tg_token and tg_channel:
            print(f"   ✅ Credentials found")
            try:
                upload_result = upload_to_telegram(
                    video_path=video_path,
                    caption=platform_meta["telegram"]["caption"]
                )
                if upload_result.get('status') == 'success' or upload_result.get('ok'):
                    results["uploads"]["telegram"] = {"status": "success", "result": upload_result}
                    results["platforms_successful"].append("telegram")
                    print(f"   ✅ Telegram upload successful")
                else:
                    results["uploads"]["telegram"] = {"status": "failed", "error": upload_result}
                    results["platforms_failed"].append("telegram")
                    print(f"   ❌ Telegram upload failed")
            except Exception as e:
                print(f"   ❌ Telegram upload failed: {e}")
                results["uploads"]["telegram"] = {"status": "failed", "error": str(e)}
                results["platforms_failed"].append("telegram")
        else:
            print(f"   ⚠️  No Telegram credentials (skipped)")
            results["uploads"]["telegram"] = {"status": "skipped", "reason": "No credentials"}
            results["platforms_skipped"].append("telegram")
    else:
        print(f"   ❌ Telegram module not available")
        results["uploads"]["telegram"] = {"status": "failed", "error": "Module not available"}
        results["platforms_failed"].append("telegram")

    # ===== VK (VKontakte) =====
    print(f"\n📱 VK (VKontakte) UPLOAD...")
    results["platforms_attempted"].append("vk")

    if VK_AVAILABLE:
        vk_token = os.getenv("VK_ACCESS_TOKEN")
        vk_group_id = os.getenv("VK_GROUP_ID")

        if vk_token and vk_group_id:
            print(f"   ✅ Credentials found")
            try:
                upload_result = upload_to_vk(
                    video_path=video_path,
                    description=platform_meta["vk"]["description"],
                    title=platform_meta["vk"]["title"]
                )
                if upload_result.get('success'):
                    results["uploads"]["vk"] = {"status": "success", "result": upload_result}
                    results["platforms_successful"].append("vk")
                    print(f"   ✅ VK upload successful")
                else:
                    results["uploads"]["vk"] = {"status": "failed", "error": upload_result}
                    results["platforms_failed"].append("vk")
                    print(f"   ❌ VK upload failed")
            except Exception as e:
                print(f"   ❌ VK upload failed: {e}")
                results["uploads"]["vk"] = {"status": "failed", "error": str(e)}
                results["platforms_failed"].append("vk")
        else:
            print(f"   ⚠️  No VK credentials (skipped)")
            results["uploads"]["vk"] = {"status": "skipped", "reason": "No credentials"}
            results["platforms_skipped"].append("vk")
    else:
        print(f"   ❌ VK module not available")
        results["uploads"]["vk"] = {"status": "failed", "error": "Module not available"}
        results["platforms_failed"].append("vk")

    # ===== THREADS =====
    print(f"\n🧵 THREADS UPLOAD...")
    results["platforms_attempted"].append("threads")

    if THREADS_AVAILABLE:
        threads_token = os.getenv("THREADS_ACCESS_TOKEN")
        threads_user_id = os.getenv("THREADS_USER_ID")

        if threads_token and threads_user_id:
            print(f"   ✅ Credentials found")
            try:
                upload_result = upload_to_threads(
                    video_path=video_path,
                    text=platform_meta["threads"]["text"]
                )
                results["uploads"]["threads"] = {"status": "success", "result": upload_result}
                results["platforms_successful"].append("threads")
                print(f"   ✅ Threads upload successful")
            except Exception as e:
                print(f"   ❌ Threads upload failed: {e}")
                results["uploads"]["threads"] = {"status": "failed", "error": str(e)}
                results["platforms_failed"].append("threads")
        else:
            print(f"   ⚠️  No Threads credentials (skipped)")
            results["uploads"]["threads"] = {"status": "skipped", "reason": "No credentials"}
            results["platforms_skipped"].append("threads")
    else:
        print(f"   ❌ Threads module not available")
        results["uploads"]["threads"] = {"status": "failed", "error": "Module not available"}
        results["platforms_failed"].append("threads")

    # ===== TIKTOK =====
    print(f"\n🎵 TIKTOK UPLOAD...")
    results["platforms_attempted"].append("tiktok")

    if TIKTOK_AVAILABLE:
        tiktok_token = os.getenv("TIKTOK_ACCESS_TOKEN")
        tiktok_account_id = os.getenv("TIKTOK_ACCOUNT_ID")

        if tiktok_token and tiktok_account_id:
            print(f"   ✅ Credentials found")
            try:
                upload_result = upload_to_tiktok(
                    video_path=video_path,
                    description=platform_meta["tiktok"]["description"]
                )
                results["uploads"]["tiktok"] = {"status": "success", "result": upload_result}
                results["platforms_successful"].append("tiktok")
                print(f"   ✅ TikTok upload successful")
            except Exception as e:
                print(f"   ❌ TikTok upload failed: {e}")
                results["uploads"]["tiktok"] = {"status": "failed", "error": str(e)}
                results["platforms_failed"].append("tiktok")
        else:
            print(f"   ⚠️  No TikTok credentials (skipped)")
            results["uploads"]["tiktok"] = {"status": "skipped", "reason": "No credentials"}
            results["platforms_skipped"].append("tiktok")
    else:
        print(f"   ❌ TikTok module not available")
        results["uploads"]["tiktok"] = {"status": "failed", "error": "Module not available"}
        results["platforms_failed"].append("tiktok")

    # ===== SUMMARY =====
    print("\n" + "="*80)
    print("📊 UPLOAD SUMMARY")
    print("="*80)

    total = len(results["platforms_attempted"])
    successful = len(results["platforms_successful"])
    failed = len(results["platforms_failed"])
    skipped = len(results["platforms_skipped"])

    print(f"\n📈 Overall Status:")
    print(f"   ├─ Total Platforms: {total}")
    print(f"   ├─ ✅ Successful: {successful}")
    print(f"   ├─ ❌ Failed: {failed}")
    print(f"   └─ ⚠️  Skipped: {skipped}")

    if total > 0:
        success_rate = (successful / total) * 100
        print(f"\n🎯 Success Rate: {success_rate:.0f}%")

    if results["platforms_successful"]:
        print(f"\n✅ SUCCESSFUL UPLOADS ({len(results['platforms_successful'])}):")
        for platform in results["platforms_successful"]:
            print(f"   ✅ {platform.upper()}")

    if results["platforms_failed"]:
        print(f"\n❌ FAILED UPLOADS ({len(results['platforms_failed'])}):")
        for platform in results["platforms_failed"]:
            platform_data = results["uploads"].get(platform, {})
            error = platform_data.get("error", "Unknown error")
            if isinstance(error, dict):
                error = str(error)
            print(f"   ❌ {platform.upper()}: {error[:60]}...")

    if results["platforms_skipped"]:
        print(f"\n⚠️  SKIPPED PLATFORMS ({len(results['platforms_skipped'])}):")
        for platform in results["platforms_skipped"]:
            print(f"   ⚠️  {platform.upper()} - Add credentials in .env to enable")
        print(f"\n💡 Add credentials in .env file to enable these platforms")

    print("\n" + "="*80)

    # Save results
    results_file = Path("output") / f"upload_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    results_file.parent.mkdir(exist_ok=True)
    with open(results_file, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2, ensure_ascii=False)

    print(f"\n💾 Results saved: {results_file}")
    print("="*80)

    return results


def main():
    """Main upload workflow"""

    print("\n" + "="*80)
    print("🇪🇸 HABLAVERSE - AUTOMATED MULTI-PLATFORM UPLOAD 🇪🇸")
    print("="*80)

    video = get_latest_video()

    if not video:
        print("\n❌ No video found! Run generate_video_robust.py first.")
        sys.exit(1)

    print(f"\n✅ Found latest video:")
    print(f"   Category: {video['category']}")
    print(f"   Video: {video['video_path']}")
    print(f"   Phrases: {len(video['phrases'])}")

    results = upload_to_all_platforms(
        video['video_path'],
        video['metadata'],
        video['category']
    )

    successful = len(results.get("platforms_successful", []))
    failed = len(results.get("platforms_failed", []))
    skipped = len(results.get("platforms_skipped", []))

    if successful > 0:
        print(f"\n✅ Upload complete! {successful} platform(s) successful.")
        if skipped > 0:
            print(f"💡 {skipped} platform(s) skipped - add credentials in .env to enable them")
        sys.exit(0)
    elif failed > 0:
        print(f"\n⚠️  All attempted uploads failed ({failed} failed, {skipped} skipped).")
        print("💡 Check the error messages above and verify your credentials")
        sys.exit(1)
    else:
        print(f"\n⚠️  All uploads skipped ({skipped} skipped).")
        print("💡 Add credentials in .env file to enable uploads")
        sys.exit(1)


if __name__ == "__main__":
    main()
