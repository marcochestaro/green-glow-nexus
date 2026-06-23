#!/usr/bin/env python3
"""
Weekly script generator — runs every Sunday, writes 7 posts for the coming week.
Each script is tailored for @marcomarkets: Meta ads for local service businesses.
"""

import os, json, requests
from datetime import datetime, timezone, timedelta

CLAUDE_API_KEY = os.environ.get('CLAUDE_API_KEY', '')
OUTPUT_FILE = os.path.join(os.path.dirname(__file__), '..', 'dashboard', 'scripts-data.json')

TYPES = ['Talking Head', 'Screen Record', 'Talking Head', 'Carousel', 'Talking Head', 'Talking Head', 'Talking Head']

TOPIC_POOL = [
    # Ads strategy
    "The $25/day ad budget breakdown — what it actually produces for a service business",
    "Why your Meta ad isn't getting leads (the 3 most common mistakes)",
    "How to write a headline that gets service business owners to stop scrolling",
    "The one campaign objective most service businesses get wrong",
    "Why broad audiences are killing your local ad results",
    "How to use a real job photo instead of stock to 3x your click rate",
    "The difference between a boosted post and a real Meta ad campaign",
    "How to set up a lead form that actually converts on Meta",
    "Why your ad works for 3 days then dies — and how to fix it",
    "What a $25/day ad account looks like after 30 days (real numbers)",
    # Mindset / positioning
    "Referrals are keeping you stuck — here's why",
    "Why service businesses are better positioned for Meta ads than e-commerce",
    "The information gap between tradies and marketing agencies is bigger than you think",
    "Why most service business owners think ads don't work (and why they're wrong)",
    "What happens when you stop relying on word of mouth",
    # Content / hooks
    "One word change that gets more people clicking your ad",
    "The hook formula that works for every service business ad",
    "Why 'professional and reliable' is the worst thing to put in your ad",
    "How to write an offer that actually makes people want to call",
    # Client results
    "Car detailer, $25/day, 30 days — real numbers",
    "Window cleaner went from 0 to 11 booked jobs in a month with Meta ads",
    "How a plumber cut his cost per lead from $120 to $38",
    # Platform / strategy
    "Meta vs Google — the honest answer for service businesses",
    "Why I only run Meta ads for service businesses (not Google, not TikTok)",
    "How the Meta algorithm decides who sees your ad",
    "Why retargeting is the cheapest leads you'll ever get",
]

def claude(prompt, max_tokens=2000):
    if not CLAUDE_API_KEY:
        print("No CLAUDE_API_KEY")
        return None
    try:
        r = requests.post(
            'https://api.anthropic.com/v1/messages',
            headers={
                'x-api-key': CLAUDE_API_KEY,
                'anthropic-version': '2023-06-01',
                'content-type': 'application/json',
            },
            json={
                'model': 'claude-haiku-4-5-20251001',
                'max_tokens': max_tokens,
                'messages': [{'role': 'user', 'content': prompt}]
            },
            timeout=60
        )
        r.raise_for_status()
        text = r.json()['content'][0]['text'].strip()
        start = text.find('{')
        end = text.rfind('}') + 1
        if start >= 0 and end > start:
            return json.loads(text[start:end])
        return None
    except Exception as e:
        print(f"Claude error: {e}")
        return None

def pick_topics(n=7):
    """Pick n varied topics for the week — spread across strategy, mindset, results."""
    import random
    pool = TOPIC_POOL[:]
    random.shuffle(pool)
    return pool[:n]

def generate_script(topic, post_type, day_label):
    type_instruction = {
        'Talking Head': 'Direct to camera. Conversational. No teleprompter feel.',
        'Screen Record': 'Screen record of Meta Ads Manager or Instagram. Walk through it as you talk.',
        'Carousel': '5 slides. Each slide is one bold point. Minimal design, dark background.',
    }.get(post_type, 'Direct to camera.')

    prompt = f"""You are writing Instagram and TikTok content for @marcomarkets — Marco, who runs Meta ads for local service businesses (plumbers, window cleaners, landscapers, HVAC, car detailers) at $25/day budgets. His audience is service business owners who want more leads.

Tone: chill, real, easy to follow. Like a knowledgeable friend talking — not a hype guy, not a corporate marketer. Conversational and confident. Professional but never stiff. No slang like "tradies". Say "service business owners" or just "business owners" or name the trade directly (plumber, detailer, etc).

Write a complete script for {day_label} ({post_type}).

Topic: {topic}

Format instruction: {type_instruction}

The script must have:
- A strong hook (first 3-5 seconds — make them stop scrolling)
- Clear value in the middle (teach something real and specific)
- A closing line — but ONLY add a CTA ("DM me ADS" / "follow @marcomarkets") if this is one of the max-2 CTA videos for the week. Otherwise end with a punchy value statement, no pitch at all.

CTA RULE — applies to BOTH the script lines and captions together:
- Max 2 out of 7 videos per week should have any CTA anywhere (script or caption)
- No-CTA video: the Close line ends on a clean insight or statement — no "DM me", no "follow", no ask anywhere
- CTA video: the Close line says it, and at least one caption option can include it
- Script and captions must match — never pitch in the script if captions don't, and vice versa

Also write 3 caption options. Follow this rule strictly:

MOST VIDEOS — keep captions short (josh.hills0 style):
- lowercase, conversational, no hashtags (or max 1-2)
- Option A: 1-2 lines, pure insight
- Option B: 2-3 lines expanding the idea
- Option C: one sentence — the core point only

EXCEPTION — only write a long caption if the video hook says something like "here's how I do X" or "this is how I get clients" and the video deliberately teases "see the caption." In that case, Option B can be the full step-by-step breakdown (5-10 lines). Still lowercase. No hashtag walls.

Respond ONLY with this JSON:
{{
  "title": "short punchy title for the video, max 8 words",
  "overlay": {{"line1": "bold short hook text for on-screen overlay (like josh.hills0 style — 4-7 words, no punctuation)", "line2": "(the curiosity or pain point in parentheses — one short line)"}},
  "recCap": 0,
  "recVer": "full",  
  "type": "{post_type}",
  "film": "one sentence filming tip for Marco — where to film it, what to show, how to deliver it",
  "captions": [
    {{"label": "A", "text": "caption A text"}},
    {{"label": "B", "text": "caption B text"}},
    {{"label": "C", "text": "caption C text"}}
  ],
  "lines": [
    {{"time": "Hook", "tag": "5s", "cls": "hook", "text": "exact words to say for the hook"}},
    {{"time": "Point 1", "tag": "8s", "cls": "", "text": "exact words"}},
    {{"time": "Point 2", "tag": "8s", "cls": "", "text": "exact words"}},
    {{"time": "Point 3", "tag": "8s", "cls": "", "text": "exact words"}},
    {{"time": "Close", "tag": "5s", "cls": "cta", "text": "closing words — CTA only if this is a CTA video, otherwise a clean value statement, no pitch"}}
  ]
}}"""

    result = claude(prompt, max_tokens=1500)
    if result:
        # Ensure required fields exist
        result.setdefault('type', post_type)
        result.setdefault('film', f'{type_instruction}')
        result.setdefault('captions', [])
        result.setdefault('lines', [])
    return result

def fallback_script(topic, post_type, day_label):
    return {
        "title": topic[:50],
        "type": post_type,
        "film": "Direct to camera, confident delivery.",
        "captions": [
            {"label": "A", "text": "coming soon."},
            {"label": "B", "text": "follow @marcomarkets for daily meta ads tips for service businesses"},
            {"label": "C", "text": "more this week."}
        ],
        "lines": [
            {"time": "Hook", "tag": "5s", "cls": "hook", "text": f"Today we're talking about: {topic}"},
            {"time": "Main Point", "tag": "20s", "cls": "", "text": "Script coming — check back after Sunday's automated update."},
            {"time": "Close", "tag": "5s", "cls": "cta", "text": "DM me ADS if you want help with your Meta ads."}
        ]
    }

def main():
    now = datetime.now(timezone.utc)
    # Find next Monday
    days_to_monday = (7 - now.weekday()) % 7 or 7
    week_start = now + timedelta(days=days_to_monday)
    week_start = week_start.replace(hour=0, minute=0, second=0, microsecond=0)

    day_names = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
    topics = pick_topics(7)

    print(f"Generating scripts for week of {week_start.strftime('%b %d, %Y')}...")

    scripts = []
    for i, (topic, post_type, day_name) in enumerate(zip(topics, TYPES, day_names)):
        print(f"  {day_name}: {topic[:50]}...")
        result = generate_script(topic, post_type, day_name)
        if not result:
            print(f"  → fallback used for {day_name}")
            result = fallback_script(topic, post_type, day_name)
        scripts.append(result)

    output = {
        "generated": now.strftime('%Y-%m-%dT%H:%M:%SZ'),
        "generated_display": now.strftime('%b %d, %Y at %H:%M UTC'),
        "week_of": week_start.strftime('%Y-%m-%d'),
        "week_of_display": week_start.strftime('%b %d, %Y'),
        "scripts": scripts
    }

    with open(OUTPUT_FILE, 'w') as f:
        json.dump(output, f, indent=2)

    print(f"Done. Written to {OUTPUT_FILE}")
    print(f"Week of: {output['week_of_display']}")

if __name__ == '__main__':
    main()
