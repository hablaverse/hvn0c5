"""
Content Tracker - Prevents duplicate content generation
Tracks used phrases and categories to ensure fresh content every time
"""

import json
import os
from datetime import datetime
from pathlib import Path

TRACKER_FILE = Path("content_history.json")


def load_history():
    """Load content generation history"""
    if TRACKER_FILE.exists():
        try:
            with open(TRACKER_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except:
            return {"runs": [], "used_phrases": []}
    return {"runs": [], "used_phrases": []}


def save_history(history):
    """Save content generation history"""
    with open(TRACKER_FILE, 'w', encoding='utf-8') as f:
        json.dump(history, f, ensure_ascii=False, indent=2)


def is_phrase_duplicate(new_phrase, used_phrases, similarity_threshold=0.6):
    """
    Check if a phrase is too similar to previously used phrases
    Simple word-based similarity check
    
    Lower threshold (0.6) means stricter duplicate detection
    """
    new_words = set(new_phrase.lower().split())
    
    # Skip very short phrases
    if len(new_words) < 3:
        for used in used_phrases:
            if new_phrase.lower() in used.lower() or used.lower() in new_phrase.lower():
                return True
        return False

    for used in used_phrases:
        used_words = set(used.lower().split())

        # Calculate Jaccard similarity
        if len(new_words) == 0 or len(used_words) == 0:
            continue

        intersection = len(new_words.intersection(used_words))
        union = len(new_words.union(used_words))
        similarity = intersection / union if union > 0 else 0

        if similarity >= similarity_threshold:
            return True

    return False


def filter_duplicate_phrases(phrases, history, similarity_threshold=0.6):
    """
    Filter out phrases that are too similar to previously used ones
    Returns list of unique phrases
    
    Lower threshold (0.6) means stricter duplicate detection
    """
    used_phrases = history.get("used_phrases", [])
    unique_phrases = []

    for phrase in phrases:
        english_text = phrase.get("english", "")

        if not is_phrase_duplicate(english_text, used_phrases, similarity_threshold):
            unique_phrases.append(phrase)
        else:
            print(f"[tracker] ⚠️ Skipping duplicate: {english_text[:50]}...")

    return unique_phrases


def log_content_generation(category, phrases):
    """
    Log this content generation run
    Returns True if content is unique enough
    """
    history = load_history()
    
    # Create run record
    run_record = {
        "timestamp": datetime.now().isoformat(),
        "category": category,
        "num_phrases": len(phrases),
        "phrases": [p.get("english", "") for p in phrases]
    }
    
    # Add to history
    history["runs"].append(run_record)
    
    # Add phrases to used list
    for phrase in phrases:
        english_text = phrase.get("english", "")
        if english_text and english_text not in history["used_phrases"]:
            history["used_phrases"].append(english_text)

    # Keep only last 200 runs and 2000 phrases to avoid file bloat (increased for better variety)
    history["runs"] = history["runs"][-200:]
    history["used_phrases"] = history["used_phrases"][-2000:]

    save_history(history)
    
    print(f"[tracker] ✅ Logged {len(phrases)} new phrases")
    print(f"[tracker] 📊 Total unique phrases in history: {len(history['used_phrases'])}")
    
    return True


def get_recent_categories(limit=5):
    """Get recently used categories to avoid repetition"""
    history = load_history()
    runs = history.get("runs", [])
    
    if not runs:
        return []
    
    recent_runs = runs[-limit:]
    return [run["category"] for run in recent_runs]


def suggest_fresh_category(all_categories, avoid_recent=3):
    """
    Suggest a category that hasn't been used recently
    """
    import random
    
    recent_categories = get_recent_categories(limit=avoid_recent)
    
    # Filter out recently used categories
    fresh_categories = [cat for cat in all_categories if cat not in recent_categories]
    
    if not fresh_categories:
        # If all categories were used recently, just pick randomly
        return random.choice(all_categories)
    
    return random.choice(fresh_categories)


def print_generation_stats():
    """Print statistics about content generation"""
    history = load_history()
    runs = history.get("runs", [])
    
    if not runs:
        print("[tracker] No previous runs found")
        return
    
    print("\n" + "="*60)
    print("📊 CONTENT GENERATION HISTORY")
    print("="*60)
    print(f"Total runs: {len(runs)}")
    print(f"Unique phrases generated: {len(history['used_phrases'])}")
    
    if runs:
        print(f"\nLast 5 runs:")
        for run in runs[-5:]:
            timestamp = run['timestamp'].split('T')[0]  # Just the date
            print(f"  • {timestamp}: {run['category']} ({run['num_phrases']} phrases)")
    
    print("="*60 + "\n")


if __name__ == "__main__":
    # Test the tracker
    print_generation_stats()
