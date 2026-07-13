#!/usr/bin/env python3
"""
Content idea refresher — runs Mon & Thu, generates 40 fresh video ideas for the dashboard.
Never repeats ideas that are in the current active batch.
"""

import os, json, requests
from datetime import datetime, timezone

CLAUDE_API_KEY = os.environ.get('CLAUDE_API_KEY', '')
OUTPUT_FILE = os.path.join(os.path.dirname(__file__), '..', 'dashboard', 'scripts-data.json')

def claude_ideas():
    if not CLAUDE_API_KEY:
        print("No CLAUDE_API_KEY — skipping idea generation")
        return None

    prompt = """You are generating video content ideas for @marcomarkets — Marco, who runs Meta ads for local service businesses (plumbers, window cleaners, landscapers, HVAC, car detailers, electricians, cleaners, painters, etc).

His audience: service business owners who want more leads via Meta ads. They're practical people — they want tactics, proof, and real talk.

His content style: confident, chill, no hype. Pure value. No pitching on most videos. He's the knowledgeable friend, not the marketer trying to sell you.

Rules:
- No specific dollar amounts like "$25/day"
- No "tradies" — say "service business owners" or name the trade
- Never mention Marco's pricing
- Mix of formats: most are Talking Head, 2 per week are Screen Record
- Ideas should span: ads strategy, mindset/positioning, client results, platform/how-to, hooks/creative, offer, targeting, metrics

Generate exactly 40 unique, sharp video ideas. Make them varied — not all the same angle. Each idea should be a short, punchy title (max 10 words) that would make a service business owner stop and watch.

Respond ONLY with valid JSON:
{"ideas": ["idea 1", "idea 2", ..., "idea 40"]}"""

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
                'max_tokens': 2000,
                'messages': [{'role': 'user', 'content': prompt}]
            },
            timeout=60
        )
        r.raise_for_status()
        text = r.json()['content'][0]['text'].strip()
        start = text.find('{')
        end = text.rfind('}') + 1
        if start >= 0 and end > start:
            data = json.loads(text[start:end])
            return data.get('ideas', [])
    except Exception as e:
        print(f"Claude error: {e}")
    return None

def main():
    now = datetime.now(timezone.utc)

    ideas = claude_ideas()
    if not ideas or len(ideas) < 10:
        print("Could not generate ideas — leaving existing ones unchanged.")
        return

    try:
        with open(OUTPUT_FILE) as f:
            data = json.load(f)
    except Exception:
        data = {}

    data['ideas'] = ideas[:40]
    data['ideas_updated'] = now.strftime('%Y-%m-%dT%H:%M:%SZ')
    data['ideas_updated_display'] = now.strftime('%b %d, %Y at %H:%M UTC')

    with open(OUTPUT_FILE, 'w') as f:
        json.dump(data, f, indent=2)

    print(f"Done. {len(ideas[:40])} ideas written.")

if __name__ == '__main__':
    main()
