#!/usr/bin/env python3
"""
Weekly script generator — runs every Sunday, writes 2 weeks of scripts.
Each script is tailored for @marcomarkets: Meta ads for local service businesses.
"""

import os, json, requests
from datetime import datetime, timezone, timedelta

CLAUDE_API_KEY = os.environ.get('CLAUDE_API_KEY', '')
OUTPUT_FILE = os.path.join(os.path.dirname(__file__), '..', 'dashboard', 'scripts-data.json')

# No Carousel — only Talking Head and Screen Record
# Pattern: 5 Talking Head, 2 Screen Record per week
TYPES = ['Talking Head', 'Talking Head', 'Screen Record', 'Talking Head', 'Talking Head', 'Screen Record', 'Talking Head']

TOPIC_POOL = [
    # Ads strategy
    "Why your Meta ad isn't getting leads (the 3 most common mistakes)",
    "How to write a headline that gets service business owners to stop scrolling",
    "The one campaign objective most service businesses get wrong",
    "Why broad audiences are killing your local ad results",
    "How to use a real job photo instead of stock to 3x your click rate",
    "The difference between a boosted post and a real Meta ad campaign",
    "How to set up a lead form that actually converts on Meta",
    "Why your ad works for 3 days then dies — and how to fix it",
    "What a well-run Meta ad account looks like after 30 days (real numbers)",
    # Mindset / positioning
    "Referrals are keeping you stuck — here's why",
    "Why service businesses are better positioned for Meta ads than e-commerce",
    "The gap between service business owners and marketing agencies",
    "Why most service business owners think ads don't work (and why they're wrong)",
    "What happens when you stop relying on word of mouth",
    "Why your lead cost is high and what actually fixes it",
    "The difference between service businesses that scale and those that stay stuck",
    # Content / hooks
    "One word change that gets more people clicking your ad",
    "The hook formula that works for every service business ad",
    "Why 'professional and reliable' is the worst thing to put in your ad",
    "How to write an offer that actually makes people want to call",
    "Why your offer is the reason your ad isn't converting",
    # Client results
    "Window cleaner went from 0 to 11 booked jobs in a month with Meta ads",
    "How a plumber cut his cost per lead from $120 to $38",
    "Car detailer: 39 leads, 15 booked, $2k-$3k back — real numbers",
    "How a landscaper filled his schedule using Meta ads alone",
    # Platform / strategy
    "Meta vs Google — the honest answer for service businesses",
    "Why I only run Meta ads for service businesses (not Google, not TikTok)",
    "How the Meta algorithm decides who sees your ad",
    "Why retargeting is the cheapest leads you'll ever get",
    "How to structure your first Meta ad campaign the right way",
    "Why most service business owners quit ads too early",
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

def pick_topics(n, used=None):
    """Pick n varied topics, never repeating used ones."""
    import random
    used = used or []
    pool = [t for t in TOPIC_POOL if t not in used]
    random.shuffle(pool)
    return pool[:n]

def generate_script(topic, post_type, day_label):
    type_instruction = {
        'Talking Head': 'Direct to camera. Conversational. No teleprompter feel.',
        'Screen Record': 'Screen record of Meta Ads Manager or Instagram. Walk through it as you talk.',
    }.get(post_type, 'Direct to camera.')

    prompt = f"""You are writing Instagram and TikTok content for @marcomarkets — Marco, who runs Meta ads for local service businesses (plumbers, window cleaners, landscapers, HVAC, car detailers, electricians, cleaners). His audience is service business owners who want more leads and want to scale. He works with clients who have real budgets and serious growth goals — not just people testing with pocket change.

Tone: chill, real, easy to follow. Like a knowledgeable friend who's seen real results — not a hype guy, not a corporate marketer. Conversational and confident. Professional but never stiff. No slang like "tradies". Say "service business owners" or just "business owners" or name the trade directly (plumber, detailer, etc). Never mention specific daily budgets like "$25/day" — talk about ad spend in general terms, or use results/percentages/ratios instead.

Never talk negatively about other niches like e-commerce or coaches — Marco may work with them in the future.

Write a complete script for {day_label} ({post_type}).

Topic: {topic}

Format instruction: {type_instruction}

OVERLAY RULE: Only include an overlay object for Talking Head videos (line1 and line2 as short on-screen text). For Screen Record, set overlay to null.

The script must have:
- A strong hook (first 3-5 seconds — make them stop scrolling)
- Clear value in the middle (teach something real and specific)
- A closing line — but ONLY add a CTA ("DM me ADS" / "follow @marcomarkets") if this is one of the max-2 CTA videos for the week. Otherwise end with a punchy value statement, no pitch at all.

CTA RULE — applies to BOTH the script lines and captions together:
- Max 2 out of 7 videos per week should have any CTA anywhere (script or caption)
- No-CTA video: the Close line ends on a clean insight or statement — no "DM me", no "follow", no ask anywhere
- CTA video: the Close line says it, and at least one caption option can include it
- Script and captions must match — never pitch in the script if captions don't, and vice versa

Also write 3 caption options (josh.hills0 style):
- lowercase, conversational, no hashtags (or max 1-2)
- Option A: 1-2 lines, pure insight or value takeaway
- Option B: 2-3 lines expanding the idea
- Option C: one sentence — the core point only

Respond ONLY with this JSON:
{{
  "title": "short punchy title for the video, max 8 words",
  "overlay": {{"line1": "short on-screen text line 1", "line2": "line 2"}} ,
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
    {{"time": "Close", "tag": "5s", "cls": "", "text": "closing words — CTA only if this is a CTA video, otherwise a clean value statement, no pitch"}}
  ]
}}"""

    result = claude(prompt, max_tokens=1500)
    if result:
        result.setdefault('type', post_type)
        result.setdefault('film', type_instruction)
        result.setdefault('captions', [])
        result.setdefault('lines', [])
        result.setdefault('stories', [])
    return result

def fallback_script(topic, post_type, day_label):
    return {
        "title": topic[:50],
        "type": post_type,
        "film": "Direct to camera, confident delivery.",
        "captions": [
            {"label": "A", "text": "coming soon."},
            {"label": "B", "text": "follow @marcomarkets for daily meta ads content for service businesses"},
            {"label": "C", "text": "more this week."}
        ],
        "lines": [
            {"time": "Hook", "tag": "5s", "cls": "hook", "text": f"Today: {topic}"},
            {"time": "Main Point", "tag": "20s", "cls": "", "text": "Script coming — check back after Sunday's update."},
            {"time": "Close", "tag": "5s", "cls": "", "text": "More coming this week."}
        ],
        "stories": [],
        "overlay": None
    }

def generate_week(week_start, used_topics=None):
    day_names = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
    topics = pick_topics(7, used=used_topics)
    label = week_start.strftime('%b %d, %Y')
    print(f"Generating scripts for week of {label}...")
    scripts = []
    for i, (topic, post_type, day_name) in enumerate(zip(topics, TYPES, day_names)):
        print(f"  {day_name}: {topic[:55]}...")
        result = generate_script(topic, post_type, day_name)
        if not result:
            print(f"  → fallback used for {day_name}")
            result = fallback_script(topic, post_type, day_name)
        scripts.append(result)
    return {
        "week_of": week_start.strftime('%Y-%m-%d'),
        "week_of_display": label,
        "scripts": scripts,
    }

def main():
    now = datetime.now(timezone.utc)
    # Week 1 = next Monday
    days_to_monday = (7 - now.weekday()) % 7 or 7
    week1_start = (now + timedelta(days=days_to_monday)).replace(hour=0, minute=0, second=0, microsecond=0)
    week2_start = week1_start + timedelta(weeks=1)

    week1 = generate_week(week1_start)
    week1_topics = [s['title'] for s in week1['scripts']]
    week2 = generate_week(week2_start, used_topics=week1_topics)

    # Load existing weeks and keep any that aren't being replaced
    existing_weeks = []
    try:
        with open(OUTPUT_FILE) as f:
            old = json.load(f)
            existing_weeks = old.get('weeks', [])
    except Exception:
        pass

    new_week_dates = {week1['week_of'], week2['week_of']}
    kept = [w for w in existing_weeks if w['week_of'] not in new_week_dates]
    all_weeks = sorted(kept + [week1, week2], key=lambda w: w['week_of'])

    output = {
        "generated": now.strftime('%Y-%m-%dT%H:%M:%SZ'),
        "generated_display": now.strftime('%b %d, %Y at %H:%M UTC'),
        "weeks": all_weeks,
        # Keep legacy 'scripts' key pointing to week1 for backwards compat
        "scripts": week1['scripts'],
        "week_of": week1['week_of'],
        "week_of_display": week1['week_of_display'],
    }

    with open(OUTPUT_FILE, 'w') as f:
        json.dump(output, f, indent=2)

    print(f"Done. {len(all_weeks)} weeks stored.")

if __name__ == '__main__':
    main()
