"""
HablaVerse - Advanced Search Engine Optimization (SEO) & Algorithmic Discovery Engine
Optimized specifically for:
- Google Search Indexing & Video Carousels
- YouTube Algorithm & Shorts Feed (Category 27: Education)
- Instagram Reels & Explore Page (Search-indexed captions + save triggers)
- Facebook Video Graph Search & Watch Feed
"""

import random


def generate_seo_metadata(category: str, phrases: list) -> dict:
    """
    Generate highly optimized, platform-specific metadata designed to maximize:
    1. Search Engine Discoverability (Google Search, YouTube Search, Instagram Search)
    2. Click-Through Rate (CTR) via intent-driven hooks
    3. Algorithm Engagement (Saves, Shares, Watch time, Comments)
    """
    phrases = phrases or []
    first_eng = phrases[0].get("english", "").strip() if phrases else category

    # =========================================================================
    # 1. YOUTUBE METADATA (Category 27: Education)
    # =========================================================================
    # Rotate title templates to avoid duplicate-title penalties while targeting high-volume searches
    yt_title_templates = [
        f"5 Essential Spanish Phrases for {category}! 🇪🇸 (Spanish for Beginners) #Shorts",
        f"How to Say \"{first_eng}\" in Spanish? 🇪🇸 ({category} Phrases) #Shorts",
        f"Must-Know Spanish {category} Vocabulary! 🇪🇸 (Speak Spanish Fast) #Shorts",
        f"Learn Spanish: Top {category} Phrases in 60 Seconds! 🇪🇸 #Shorts",
        f"Daily Spanish: {category} Phrases for Beginners 🇪🇸 #Shorts"
    ]
    # Pick template deterministically or semi-randomly based on category length
    title_idx = len(category) % len(yt_title_templates)
    yt_title = yt_title_templates[title_idx][:100]

    # Timestamp breakdown for Google Video indexing
    # Google Search requires 00:00 format to index video chapters
    timestamps = [
        "0:00 Intro: Spanish " + category,
        "0:05 Phrase 1",
        "0:15 Phrase 2",
        "0:25 Phrase 3",
        "0:35 Phrase 4",
        "0:45 Phrase 5"
    ]

    yt_desc_lines = [
        f"🎯 Master essential Spanish phrases for {category}!",
        f"In this Spanish lesson for beginners, learn how to speak Spanish naturally with accurate pronunciation, translation, and real-world context.",
        "",
        "📌 Key Phrases & Timestamps:",
    ]

    for i, p in enumerate(phrases[:5]):
        eng = p.get("english", "")
        spa = p.get("spanish", "")
        pron = p.get("pronunciation", "")
        ctx = p.get("context", "")
        t_label = timestamps[i + 1] if i + 1 < len(timestamps) else f"0:{20 + i*10}"
        line = f"• {t_label}: {eng} → {spa}"
        if pron:
            line += f" [{pron}]"
        if ctx:
            line += f" ({ctx})"
        yt_desc_lines.append(line)

    yt_desc_lines.extend([
        "",
        "💡 Pronunciation & Study Tip:",
        "Repeat each phrase out loud 3 times to build muscle memory and master the native Spanish accent!",
        "",
        "🌍 About HablaVerse:",
        "HablaVerse brings you daily Spanish lessons, essential Spanish vocabulary, travel phrases, and pronunciation guides to help you become fluent in Spanish one phrase at a time.",
        "",
        "🔔 Subscribe to HablaVerse for daily Spanish lessons, Shorts, and fluency tips!",
        "👍 Like this video and comment below which phrase was your favorite!",
        "",
        "#Shorts #LearnSpanish #SpanishForBeginners #SpanishVocabulary #SpeakSpanish #SpanishPhrases #DailySpanish #SpanishLessons #LanguageLearning #HablaVerse #SpanishPronunciation #Education"
    ])
    yt_description = "\n".join(yt_desc_lines)[:5000]

    yt_tags = [
        "Learn Spanish",
        "Spanish for beginners",
        "Spanish phrases",
        "Spanish vocabulary",
        "Speak Spanish",
        "Daily Spanish",
        "Spanish lessons",
        "Spanish pronunciation",
        "Conversational Spanish",
        "Basic Spanish",
        "Spanish speaking practice",
        f"Spanish {category.lower()}",
        f"{category.lower()} in Spanish",
        "Spanish words",
        "Language learning",
        "HablaVerse",
        "Spanish Shorts",
        "How to learn Spanish",
        "Spanish language",
        "Fast Spanish"
    ]

    # =========================================================================
    # 2. INSTAGRAM METADATA (Reels & Search)
    # =========================================================================
    # Instagram's algorithm indexes the first 125 characters before the fold for search queries
    ig_desc_lines = [
        f"🇪🇸 5 Essential Spanish Phrases for {category}! (Save this for later 📌)",
        "",
        f"Want to sound natural speaking Spanish? Master these must-know {category.lower()} phrases today:",
        ""
    ]

    emojis = ["1️⃣", "2️⃣", "3️⃣", "4️⃣", "5️⃣"]
    for i, p in enumerate(phrases[:5]):
        emoji = emojis[i] if i < len(emojis) else f"{i+1}."
        ig_desc_lines.append(f"{emoji} {p.get('english', '')}")
        ig_desc_lines.append(f"   📍 {p.get('spanish', '')}")
        if p.get("pronunciation"):
            ig_desc_lines.append(f"   🔊 [{p.get('pronunciation', '')}]")
        if p.get("context"):
            ig_desc_lines.append(f"   💡 Context: {p.get('context', '')}")
        ig_desc_lines.append("")

    ig_desc_lines.extend([
        "💾 SAVE this reel so you can practice pronunciation anytime!",
        "💬 Comment below: Which phrase are you going to use today?",
        "👥 Tag a friend who is learning Spanish!",
        "🔔 Follow @hablaverse for daily bite-sized Spanish lessons!",
        "",
        "#learnspanish #spanishforbeginners #spanishvocabulary #spanishphrases #dailyspanish #speakspanish #spanishlessons #studyspanish #learnlanguages #spanishtips #bilingual #hablaverse #spanishwords #spanishpractice #reels #spanishreels #learnoninstagram"
    ])
    ig_caption = "\n".join(ig_desc_lines)[:2200]

    # =========================================================================
    # 3. FACEBOOK METADATA (Clean, Highly Shareable, Search-friendly)
    # =========================================================================
    fb_title = f"Learn Spanish: 5 Must-Know {category} Phrases for Beginners 🇪🇸"
    fb_desc_lines = [
        f"🎯 Learn Spanish with HablaVerse!",
        f"📚 Category: {category}",
        "",
        f"Master Spanish one phrase at a time! Here are 5 essential {category.lower()} phrases with pronunciation:",
        ""
    ]
    for i, p in enumerate(phrases[:5]):
        emoji = emojis[i] if i < len(emojis) else f"{i+1}."
        fb_desc_lines.append(f"{emoji} {p.get('english', '')}")
        fb_desc_lines.append(f"   📍 {p.get('spanish', '')}")
        if p.get("pronunciation"):
            fb_desc_lines.append(f"   🔊 [{p.get('pronunciation', '')}]")
        fb_desc_lines.append("")

    fb_desc_lines.extend([
        "💡 Tip: Repeat each phrase out loud 3 times to lock it into memory!",
        "👍 Like this video if you learned something new!",
        "💬 Comment your favorite phrase below!",
        "🔔 Follow HablaVerse for daily Spanish lessons!",
        "",
        "#learnspanish #spanishlessons #spanishforbeginners #languagelearning #spanishvocabulary #hablaverse #dailyspanish #speakspanish #spanishwords #bilingual"
    ])
    fb_description = "\n".join(fb_desc_lines)

    # =========================================================================
    # 4. TWITTER / X METADATA (Short, High-Engagement)
    # =========================================================================
    first_phrase = phrases[0] if phrases else {}
    tw_caption = (
        f"🇪🇸 Learn Spanish: {category}\n\n"
        f"• {first_phrase.get('english', '')} ➜ {first_phrase.get('spanish', '')}\n\n"
        f"Master daily Spanish one phrase at a time! 👇\n\n"
        f"#LearnSpanish #Spanish #HablaVerse"
    )

    # =========================================================================
    # 5. TELEGRAM METADATA (HTML formatting)
    # =========================================================================
    tg_lines = [
        f"🇪🇸 <b>Learn Spanish: {category}</b>\n"
    ]
    for p in phrases[:5]:
        tg_lines.append(f"• <b>{p.get('english', '')}</b> ➜ <i>{p.get('spanish', '')}</i> [{p.get('pronunciation', '')}]")
    tg_lines.append("\n💡 <i>Repeat each phrase out loud 3 times!</i>\n\n#Spanish #LearnSpanish")
    tg_caption = "\n".join(tg_lines)

    # =========================================================================
    # 6. THREADS / TIKTOK / VK
    # =========================================================================
    threads_text = (
        f"🇪🇸 5 Essential Spanish Phrases for {category}!\n\n"
        f"• {first_phrase.get('english', '')} ➜ {first_phrase.get('spanish', '')}\n\n"
        f"Save this for your daily Spanish practice 📌\n#LearnSpanish #Spanish"
    )

    tiktok_desc = (
        f"🇪🇸 5 Must-Know Spanish {category} Phrases! #LearnSpanish #Spanish #SpanishForBeginners #HablaVerse #Education"
    )

    return {
        "youtube": {
            "title": yt_title,
            "description": yt_description,
            "tags": yt_tags,
            "category_id": "27"  # Education
        },
        "instagram": {
            "caption": ig_caption
        },
        "facebook": {
            "title": fb_title,
            "description": fb_description
        },
        "twitter": {
            "caption": tw_caption
        },
        "telegram": {
            "caption": tg_caption
        },
        "vk": {
            "title": fb_title,
            "description": fb_description
        },
        "threads": {
            "text": threads_text
        },
        "tiktok": {
            "description": tiktok_desc
        }
    }
