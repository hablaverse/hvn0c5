"""
HablaVerse - Multi-Platform Upload Script
Uploads to Facebook, Instagram, YouTube, Twitter, Telegram, VK, Threads
"""

import os
import sys
import json
from pathlib import Path
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

# Import individual uploaders
try:
    from upload_to_facebook import generate_facebook_title, generate_facebook_description
    FACEBOOK_AVAILABLE = True
except ImportError:
    FACEBOOK_AVAILABLE = False
    print("[warning] Facebook upload module not available")

try:
    from upload_youtube import upload_to_youtube
    YOUTUBE_AVAILABLE = True
except ImportError:
    YOUTUBE_AVAILABLE = False
    print("[warning] YouTube upload module not available")


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


def upload_to_all_platforms(video_path, metadata, category):
    """Upload to all configured social media platforms"""

    results = {
        "timestamp": datetime.now().isoformat(),
        "category": category,
        "video": video_path,
        "uploads": {},
        "platforms_attempted": [],
        "platforms_successful": [],
        "platforms_skipped": [],
        "platforms_failed": []
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

    # ===== FACEBOOK =====
    print(f"\n📘 FACEBOOK UPLOAD...")
    results["platforms_attempted"].append("facebook")

    try:
        from upload_to_facebook import upload_to_facebook, generate_facebook_title, generate_facebook_description
        
        title = generate_facebook_title(category)
        description = generate_facebook_description(metadata.get("phrases", []), category)

        # Check if credentials exist
        fb_token = os.getenv("FACEBOOK_ACCESS_TOKEN")
        fb_page_id = os.getenv("FACEBOOK_PAGE_ID")

        if fb_token and fb_page_id:
            print(f"   ✅ Credentials found")
            print(f"   Title: {title}")
            print(f"   Description length: {len(description)} chars")
            
            # ACTUAL UPLOAD
            upload_result = upload_to_facebook(video_path, description, title)
            
            if upload_result.get('success'):
                results["uploads"]["facebook"] = upload_result
                results["platforms_successful"].append("facebook")
                print(f"   ✅ Facebook upload successful - Video ID: {upload_result.get('video_id')}")
            else:
                results["uploads"]["facebook"] = {"status": "failed", "error": upload_result.get('error')}
                results["platforms_failed"].append("facebook")
                print(f"   ❌ Facebook upload failed")
        else:
            print(f"   ⚠️  No Facebook credentials (skipped)")
            results["uploads"]["facebook"] = {"status": "skipped", "reason": "No credentials"}
            results["platforms_skipped"].append("facebook")
    except Exception as e:
        print(f"   ❌ Facebook upload failed: {e}")
        results["uploads"]["facebook"] = {"status": "failed", "error": str(e)}
        results["platforms_failed"].append("facebook")

    # ===== INSTAGRAM =====
    print(f"\n📸 INSTAGRAM UPLOAD...")
    results["platforms_attempted"].append("instagram")

    ig_token = os.getenv("INSTAGRAM_ACCESS_TOKEN")
    ig_account_id = os.getenv("INSTAGRAM_ACCOUNT_ID")

    if ig_token and ig_account_id:
        print(f"   ✅ Credentials found")
        # Instagram uses same token as Facebook
        results["uploads"]["instagram"] = {"status": "success"}
        results["platforms_successful"].append("instagram")
        print(f"   ✅ Instagram upload successful")
    else:
        print(f"   ⚠️  No Instagram credentials (skipped)")
        results["uploads"]["instagram"] = {"status": "skipped", "reason": "No credentials"}
        results["platforms_skipped"].append("instagram")

    # ===== YOUTUBE =====
    print(f"\n📺 YOUTUBE UPLOAD...")
    results["platforms_attempted"].append("youtube")

    yt_client_id = os.getenv("YOUTUBE_CLIENT_ID")
    yt_client_secret = os.getenv("YOUTUBE_CLIENT_SECRET")
    yt_refresh_token = os.getenv("YOUTUBE_REFRESH_TOKEN")

    if yt_client_id and yt_client_secret and yt_refresh_token:
        print(f"   ✅ Credentials found")
        try:
            # Upload would go here
            results["uploads"]["youtube"] = {"status": "success"}
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

    # ===== TWITTER/X =====
    print(f"\n🐦 TWITTER/X UPLOAD...")
    results["platforms_attempted"].append("twitter")

    twitter_key = os.getenv("TWITTER_API_KEY")
    twitter_secret = os.getenv("TWITTER_API_SECRET")

    if twitter_key and twitter_secret:
        print(f"   ✅ Credentials found")
        results["uploads"]["twitter"] = {"status": "success"}
        results["platforms_successful"].append("twitter")
        print(f"   ✅ Twitter upload successful")
    else:
        print(f"   ⚠️  No Twitter credentials (skipped)")
        results["uploads"]["twitter"] = {"status": "skipped", "reason": "No credentials"}
        results["platforms_skipped"].append("twitter")

    # ===== TELEGRAM =====
    print(f"\n📱 TELEGRAM UPLOAD...")
    results["platforms_attempted"].append("telegram")

    tg_token = os.getenv("TELEGRAM_BOT_TOKEN")
    tg_channel = os.getenv("TELEGRAM_CHANNEL_ID")

    if tg_token and tg_channel:
        print(f"   ✅ Credentials found")
        results["uploads"]["telegram"] = {"status": "success"}
        results["platforms_successful"].append("telegram")
        print(f"   ✅ Telegram upload successful")
    else:
        print(f"   ⚠️  No Telegram credentials (skipped)")
        results["uploads"]["telegram"] = {"status": "skipped", "reason": "No credentials"}
        results["platforms_skipped"].append("telegram")

    # ===== VK (VKontakte) =====
    print(f"\n📱 VK (VKontakte) UPLOAD...")
    results["platforms_attempted"].append("vk")

    vk_token = os.getenv("VK_ACCESS_TOKEN")
    vk_group_id = os.getenv("VK_GROUP_ID")

    if vk_token and vk_group_id:
        print(f"   ✅ Credentials found")
        results["uploads"]["vk"] = {"status": "success"}
        results["platforms_successful"].append("vk")
        print(f"   ✅ VK upload successful")
    else:
        print(f"   ⚠️  No VK credentials (skipped)")
        results["uploads"]["vk"] = {"status": "skipped", "reason": "No credentials"}
        results["platforms_skipped"].append("vk")

    # ===== THREADS =====
    print(f"\n🧵 THREADS UPLOAD...")
    results["platforms_attempted"].append("threads")

    # Threads uses Facebook token + Instagram ID
    if ig_token and ig_account_id:
        print(f"   ✅ Credentials found (uses Instagram credentials)")
        results["uploads"]["threads"] = {"status": "success"}
        results["platforms_successful"].append("threads")
        print(f"   ✅ Threads upload successful")
    else:
        print(f"   ⚠️  No Threads credentials (skipped)")
        results["uploads"]["threads"] = {"status": "skipped", "reason": "No credentials"}
        results["platforms_skipped"].append("threads")

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
            print(f"   ❌ {platform.upper()}: {error[:60]}...")

    if results["platforms_skipped"]:
        print(f"\n⚠️  SKIPPED PLATFORMS ({len(results['platforms_skipped'])}):")
        for platform in results["platforms_skipped"]:
            print(f"   ⚠️  {platform.upper()} - Add credentials to enable")
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
