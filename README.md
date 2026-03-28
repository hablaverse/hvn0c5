# 🇪🇸 HablaVerse - Automated Spanish Learning Bot

**Your Spanish Learning Universe** - Automatically generate and upload Spanish learning videos to 7 social media platforms!

---

## 🎯 What This Bot Does

Automatically generates Spanish learning videos AND uploads to:
- ✅ **Facebook** - Page posts
- ✅ **Instagram** - Reels  
- ✅ **YouTube** - Full videos
- ✅ **Twitter/X** - Video tweets
- ✅ **Telegram** - Channel posts
- ✅ **VK (VKontakte)** - Community posts
- ✅ **Threads** - Video posts

**All in ONE command!**

---

## 🚀 Quick Start

### **1. Install Dependencies**
```bash
pip install -r requirements.txt
```

### **2. Create .env File**
```bash
cp .env.template .env
```

Edit `.env` and add at minimum:
```env
POLLINATIONS_API_KEY=your_api_key_here
```

Get your free API key from: https://enter.pollinations.ai

### **3. Run Bot**
```bash
python main.py
```

That's it! The bot will:
1. Generate a video
2. Upload to all configured platforms
3. Save results

---

## 📁 Project Structure

```
hablaverse/
├── main.py                     ← Main automation script (RUN THIS)
├── generate_video_robust.py    ← Video generator
├── upload_all_platforms.py     ← Multi-platform uploader
├── upload_to_facebook.py       ← Facebook/Instagram metadata
├── generate_content.py         ← AI content generation
├── generate_images.py          ← Image creation
├── generate_audio.py           ← Audio generation
├── create_video.py             ← Video assembly
├── content_tracker.py          ← Duplicate prevention
├── .env.template               ← Credentials template
├── requirements.txt            ← Dependencies
├── README.md                   ← This file
├── .github/workflows/          ← GitHub Actions automation
└── output/                     ← Generated videos
```

---

## 🔑 Environment Variables (.env)

### **Required (Minimum):**
```env
POLLINATIONS_API_KEY=your_api_key_here
```

### **Facebook + Instagram + Threads:**
```env
FACEBOOK_ACCESS_TOKEN=your_facebook_page_token
FACEBOOK_PAGE_ID=your_page_id
INSTAGRAM_ACCESS_TOKEN=your_facebook_page_token  # Same as Facebook!
INSTAGRAM_ACCOUNT_ID=your_instagram_business_id
# Threads uses the same credentials - no separate setup needed!
```

### **YouTube:**
```env
YOUTUBE_CLIENT_ID=your_client_id
YOUTUBE_CLIENT_SECRET=your_client_secret
YOUTUBE_REFRESH_TOKEN=your_refresh_token
```

### **Twitter/X:**
```env
TWITTER_API_KEY=your_api_key
TWITTER_API_SECRET=your_api_secret
TWITTER_ACCESS_TOKEN=your_access_token
TWITTER_ACCESS_SECRET=your_access_secret
```

### **Telegram:**
```env
TELEGRAM_BOT_TOKEN=your_bot_token
TELEGRAM_CHANNEL_ID=@your_channel
```

### **VK (VKontakte):**
```env
VK_ACCESS_TOKEN=your_vk_token
VK_GROUP_ID=your_group_id
```

---

## 📘 Getting Credentials

### **Facebook/Instagram/Threads:**

1. **Go to:** https://developers.facebook.com/tools/explorer/
2. **Generate User Access Token** with permissions:
   - `pages_show_list`
   - `pages_manage_posts`
   - `pages_read_engagement`
   - `instagram_basic`
   - `instagram_content_publish`
3. **Get Page Info:**
   ```bash
   curl "https://graph.facebook.com/v18.0/me/accounts?access_token=YOUR_USER_TOKEN"
   ```
4. **Copy:**
   - `access_token` → `FACEBOOK_ACCESS_TOKEN` & `INSTAGRAM_ACCESS_TOKEN`
   - `id` → `FACEBOOK_PAGE_ID`
5. **Get Instagram ID:**
   ```bash
   curl "https://graph.facebook.com/v18.0/PAGE_ID?fields=instagram_business_account&access_token=PAGE_TOKEN"
   ```
6. **Copy:** `instagram_business_account.id` → `INSTAGRAM_ACCOUNT_ID`

**Note:** Threads uses `FACEBOOK_ACCESS_TOKEN` + `INSTAGRAM_ACCOUNT_ID` - no separate credentials needed!

### **Telegram:**

1. Message **@BotFather** → `/newbot` → follow instructions
2. Copy bot token → `TELEGRAM_BOT_TOKEN`
3. Create channel, add bot as admin
4. Channel ID: `@channelname` or use @userinfobot for private channels

### **YouTube:**

1. Go to: https://console.cloud.google.com/
2. Create project → Enable YouTube Data API v3
3. Create OAuth 2.0 credentials
4. Get Client ID and Secret
5. Use OAuth playground to get refresh token

---

## 🎬 How It Works

### **Content Generation:**
1. **AI generates** 5 unique phrases from 25 categories
2. **Each phrase includes:**
   - English text
   - Spanish translation
   - Pronunciation guide (phonetic)
   - Usage context

### **Visual Creation:**
1. **Creates** 1080x1920 vertical images
2. **Adds text** with stunning effects
3. **Habla Verse branding** at bottom
4. **"English • Spanish"** language indicator

### **Audio Generation:**
1. **English voice** (Microsoft Edge TTS)
2. **Spanish voice** (Microsoft Edge TTS)
3. **Perfect synchronization**

### **Video Assembly:**
1. **Combines** images + audio
2. **Creates** MP4 video (30-40 seconds)
3. **Saves** to `output/final_video.mp4`

### **Multi-Platform Upload:**
1. **Tries all 7 platforms**
2. **Skips** platforms without credentials
3. **Shows summary** of successes/failures
4. **Saves results** to `output/upload_results_*.json`

---

## 📊 Content Categories (25 Total)

1. Daily Greetings
2. Common Phrases
3. Food & Dining
4. Travel Essentials
5. Numbers & Time
6. Family & Relationships
7. Shopping
8. Directions
9. Weather
10. Emotions & Feelings
11. Work & Business
12. Health & Body
13. Colors & Descriptions
14. Animals
15. Hobbies & Activities
16. Slang & Informal
17. Romantic Phrases
18. Emergency Situations
19. Technology & Internet
20. Sports & Fitness
21. Music & Entertainment
22. Education & Learning
23. Money & Finance
24. House & Home
25. Fashion & Appearance

**Bot randomly selects one category each run!**

---

## 🤖 GitHub Actions (Automation)

### **Setup:**

1. **Push code to GitHub**
2. **Add secrets** in repo settings:
   - `POLLINATIONS_API_KEY`
   - `FACEBOOK_ACCESS_TOKEN`
   - `FACEBOOK_PAGE_ID`
   - `INSTAGRAM_ACCESS_TOKEN`
   - `INSTAGRAM_ACCOUNT_ID`
   - (Add others as needed)

3. **Workflow runs:**
   - **5 times daily** for global coverage
   - **Manual** trigger anytime

### **Posting Schedule (UTC):**

| Time (UTC) | Latin America | Europe | North America |
|------------|---------------|--------|---------------|
| 00:00 | 6-9 PM | 12-1 AM | 7 PM EST |
| 06:00 | 12-3 AM | 7-8 AM | 1 AM EST |
| 12:00 | 6-9 AM | 1-2 PM | 7 AM EST |
| 18:00 | 12-3 PM | 7-8 PM | 1 PM EST |
| 20:00 | 2-5 PM | 9-10 PM | 3 PM EST |

**Covers all major timezones for maximum reach!**

---

## ✅ Features

### **Multi-Platform:**
- ✅ Upload to 7 platforms simultaneously
- ✅ Optional credentials (bot continues without them)
- ✅ Detailed upload summaries
- ✅ Error handling

### **Visual:**
- ✅ 1080x1920 vertical format (Reels/Shorts/TikTok)
- ✅ Habla Verse branding
- ✅ "English • Spanish" language indicator
- ✅ Dynamic text containers
- ✅ Professional gradients and effects

### **Audio:**
- ✅ English spoken ONCE (not repeated)
- ✅ Native Spanish pronunciation
- ✅ Perfect synchronization

### **Content:**
- ✅ AI-generated phrases (no repeats!)
- ✅ Complete sentences (no blanks)
- ✅ Phonetic pronunciation guides
- ✅ 25 categories for variety
- ✅ Advanced duplicate prevention

### **Automation:**
- ✅ Runs 5 times daily automatically
- ✅ Uploads to all platforms
- ✅ Continues without credentials
- ✅ Error handling
- ✅ Clear status reporting

---

## 🔧 Troubleshooting

### **"Credentials not configured"**
- Add platform credentials to `.env`
- Bot will skip and continue

### **"Video not created"**
- Check `POLLINATIONS_API_KEY` in `.env`
- Install dependencies: `pip install -r requirements.txt`

### **"Upload fails"**
- Check credentials are correct
- Verify token permissions
- Check platform API limits

### **"Font not found"**
- GitHub Actions installs fonts automatically
- Locally: Install DejaVu fonts or add Arial to `fonts/` folder

---

## 📈 Running Forever

### **Duplicate Prevention:**

1. **Content History Tracking** (`content_history.json`):
   - Stores every phrase ever generated
   - Automatically committed back to GitHub
   - Grows with every video

2. **AI-Powered Uniqueness**:
   - Passes used phrases to AI as exclusion list
   - Temperature 1.0 for maximum creativity
   - Smart similarity checking

3. **25 Categories**:
   - Randomly selected each run
   - Ensures variety

**Result:** Every video is 100% unique! 🎯

---

## 🎯 Best Practices

### **1. Test Locally First:**
```bash
python main.py
```
Check video quality before automating

### **2. Add Credentials Gradually:**
- Start with Facebook only
- Add Instagram when ready
- Add others as needed

### **3. Monitor GitHub Actions:**
- Check workflow runs
- Review upload summaries
- Fix any errors

---

## 📞 Support

### **Common Issues:**

**Q: Bot creates video but uploads fail?**
**A:** Check credentials in `.env` - bot continues without them

**Q: How to change background?**
**A:** Replace `background.png` with your own image

**Q: Which platforms are supported?**
**A:** Facebook, Instagram, YouTube, Twitter, Telegram, VK, Threads

**Q: How many times per day?**
**A:** 5 times daily (configurable in `.github/workflows/daily_upload.yml`)

---

## 🎉 You're Ready!

### **Quick Checklist:**

- [ ] Install dependencies (`pip install -r requirements.txt`)
- [ ] Create `.env` from `.env.template`
- [ ] Add `POLLINATIONS_API_KEY` to `.env`
- [ ] Test locally (`python main.py`)
- [ ] Push to GitHub
- [ ] Add GitHub secrets
- [ ] Watch it run!

---

## 🌟 Features Summary

**Your bot:**
- ✅ Generates unique Spanish content
- ✅ Creates professional videos
- ✅ Adds branding automatically
- ✅ Uploads to 7 platforms
- ✅ Never repeats content
- ✅ Runs 5 times daily
- ✅ Handles errors gracefully

**Output:**
- ✅ 1080x1920 vertical video
- ✅ Facebook title & description
- ✅ YouTube title & description
- ✅ Instagram caption
- ✅ All hashtags lowercase

---

## 📜 License

MIT License - Feel free to use and modify!

---

## 🚀 Let's Go!

**Your automated Spanish learning empire starts now!**

```bash
python main.py
```

**¡Vamos! 🇪🇸✨**
