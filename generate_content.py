"""
Spanish Learning Content Generator
Generates English-to-Spanish learning phrases with categories
"""

import os
import json
import requests
from dotenv import load_dotenv
from urllib.parse import quote

load_dotenv()

POLLINATIONS_API_KEY = os.getenv("POLLINATIONS_API_KEY")

# Learning categories for variety
CATEGORIES = [
    "Daily Greetings",
    "Common Phrases",
    "Food & Dining",
    "Travel Essentials",
    "Numbers & Time",
    "Family & Relationships",
    "Shopping",
    "Directions",
    "Weather",
    "Emotions & Feelings",
    "Work & Business",
    "Health & Body",
    "Colors & Descriptions",
    "Animals",
    "Hobbies & Activities",
    "Slang & Informal",
    "Romantic Phrases",
    "Emergency Situations",
    "Technology & Internet",
    "Sports & Fitness",
    "Music & Entertainment",
    "Education & Learning",
    "Money & Finance",
    "House & Home",
    "Fashion & Appearance"
]

# Viral hook styles for engagement
VIRAL_STYLES = [
    "surprising fact",
    "common mistake correction",
    "quick tip",
    "must-know phrase",
    "local secret",
    "travel hack",
    "flirty phrase",
    "funny expression",
    "cultural insight",
    "word origin story"
]

def generate_learning_content(category: str, num_phrases: int = 5, used_phrases: list = None) -> list:
    """
    Generate English-Spanish learning phrases using Pollinations AI

    Returns list of dicts with:
    - english: English phrase
    - spanish: Spanish translation
    - pronunciation: Phonetic pronunciation guide
    - context: Usage context/example
    """

    if not POLLINATIONS_API_KEY:
        raise ValueError("POLLINATIONS_API_KEY not set!")

    # Add viral hook instruction
    import random
    viral_style = random.choice(VIRAL_STYLES)

    system_prompt = (
        "You are a viral Spanish language teacher creating engaging educational content for social media. "
        "Generate practical, commonly-used phrases that people actually want to share and learn. "
        "IMPORTANT: Create COMPLETE sentences with NO blanks, NO underscores, NO placeholders. "
        "Every phrase must be a full, natural sentence that can be spoken aloud. "
        "Avoid phrases like 'I'm allergic to ____' - instead use specific examples like 'I'm allergic to cats'. "
        "Return ONLY valid JSON array format with no additional text. "
        f"Style: Make each phrase feel like a {viral_style} - something people would want to share!"
        "CRITICAL: Keep phrases SHORT and SIMPLE (max 10-12 words). "
        "Use everyday vocabulary that beginners can understand. "
        "Avoid complex grammar, subjunctive mood, or rare words. "
        "Focus on phrases that are immediately useful in real conversations."
    )

    # Build exclusion list from used phrases
    exclusion_note = ""
    if used_phrases and len(used_phrases) > 0:
        # Show last 20 used phrases as examples to avoid
        recent = used_phrases[-20:] if len(used_phrases) > 20 else used_phrases
        exclusion_note = f"\n\nAVOID these phrases (already used): {recent}"

    user_prompt = (
        f"Create {num_phrases} ESSENTIAL {category} phrases for English speakers learning Spanish. "
        f"Each phrase should be UNIQUE and ENGAGING - perfect for viral social media content. "
        f"For each phrase, provide: "
        f"1. English phrase (natural, conversational, COMPLETE sentence with NO blanks or underscores, MAX 10-12 WORDS) "
        f"2. Spanish translation (correct, native-level, COMPLETE sentence, SIMPLE vocabulary) "
        f"3. Pronunciation guide (simple phonetic spelling for English speakers) "
        f"4. Context (when/how to use it, 1 short sentence with a fun or surprising angle) "
        f"\n\nIMPORTANT RULES: "
        f"- NO blanks (____) or placeholders "
        f"- Use specific examples (e.g., 'I'm allergic to cats' not 'I'm allergic to ____') "
        f"- Every phrase must be speakable by text-to-speech "
        f"- Make phrases SHORT, SIMPLE, and practical (max 10-12 words each) "
        f"- Use everyday vocabulary - avoid exotic or rare words "
        f"- Avoid complex grammar (no subjunctive, no compound tenses) "
        f"- Add variety: mix formal, informal, slang, and fun expressions "
        f"- Create phrases people will want to SHARE and REMEMBER "
        f"- Think TikTok/Reels: quick, catchy, useful "
        f"{exclusion_note}"
        f"\n\nReturn as JSON array: "
        f'[{{"english": "...", "spanish": "...", "pronunciation": "...", "context": "..."}}]'
    )
    
    # Use Pollinations AI chat completions endpoint
    url = "https://gen.pollinations.ai/v1/chat/completions"
    
    headers = {
        "Authorization": f"Bearer {POLLINATIONS_API_KEY}",
        "Content-Type": "application/json"
    }
    
    payload = {
        "model": "openai",
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ],
        "temperature": 1.0  # Maximum creativity for unique content every time
    }
    
    print(f"[content] Generating {num_phrases} phrases for: {category}")
    
    max_retries = 3
    for attempt in range(max_retries):
        try:
            response = requests.post(url, headers=headers, json=payload, timeout=60)
            response.raise_for_status()
            
            data = response.json()
            content = data["choices"][0]["message"]["content"].strip()
            
            # Extract JSON from response (handle markdown code blocks)
            if "```json" in content:
                content = content.split("```json")[1].split("```")[0].strip()
            elif "```" in content:
                content = content.split("```")[1].split("```")[0].strip()
            
            # Parse JSON
            phrases = json.loads(content)
            
            # Validate structure
            if isinstance(phrases, list) and len(phrases) > 0:
                for phrase in phrases:
                    if not all(k in phrase for k in ["english", "spanish", "pronunciation", "context"]):
                        raise ValueError("Invalid phrase structure")
                
                print(f"[content] ✅ Generated {len(phrases)} phrases successfully!")
                return phrases
            else:
                raise ValueError("Invalid response format")
                
        except Exception as e:
            print(f"[content] ⚠️ Attempt {attempt + 1}/{max_retries} failed: {e}")
            if attempt == max_retries - 1:
                raise
    
    raise Exception("Failed to generate content after all retries")


def save_content_to_file(phrases: list, category: str, output_file: str = "content.json"):
    """Save generated content to JSON file"""
    
    content = {
        "category": category,
        "phrases": phrases,
        "total": len(phrases)
    }
    
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(content, f, ensure_ascii=False, indent=2)
    
    print(f"[content] Saved to {output_file}")
    return content


if __name__ == "__main__":
    # Test generation
    import random
    
    category = random.choice(CATEGORIES)
    phrases = generate_learning_content(category, num_phrases=5)
    save_content_to_file(phrases, category)
    
    print("\n" + "="*60)
    print(f"Sample phrases from '{category}':")
    print("="*60)
    for i, phrase in enumerate(phrases, 1):
        print(f"\n{i}. {phrase['english']}")
        print(f"   Spanish: {phrase['spanish']}")
        print(f"   Pronunciation: {phrase['pronunciation']}")
        print(f"   Context: {phrase['context']}")
