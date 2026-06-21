#!/usr/bin/env python3
"""
Agent research script — runs daily, pulls real data, synthesizes with Claude.
Sources: Reddit r/FacebookAds r/PPC r/socialmediamarketing, Google Trends
"""

import os, json, requests, sys
from datetime import datetime, timezone

CLAUDE_API_KEY = os.environ.get('CLAUDE_API_KEY', '')
OUTPUT_FILE = os.path.join(os.path.dirname(__file__), '..', 'dashboard', 'agents-data.json')

HEADERS = {'User-Agent': 'Mozilla/5.0 (AgentResearch/1.0; research bot)'}

# ── Data collection ──────────────────────────────────────────────────────────

def reddit_posts(subreddit, query='', sort='hot', limit=8, time='week'):
    base = f"https://www.reddit.com/r/{subreddit}"
    url = f"{base}/search.json?q={query}&sort={sort}&limit={limit}&t={time}" if query else f"{base}/{sort}.json?limit={limit}&t={time}"
    try:
        r = requests.get(url, headers=HEADERS, timeout=12)
        r.raise_for_status()
        posts = r.json()['data']['children']
        return [{'title': p['data']['title'], 'score': p['data']['score'], 'text': p['data'].get('selftext','')[:400]} for p in posts]
    except Exception as e:
        print(f"Reddit {subreddit} error: {e}")
        return []

def google_trends(keywords):
    try:
        from pytrends.request import TrendReq
        pt = TrendReq(hl='en-US', tz=0, timeout=(10,25))
        pt.build_payload(keywords[:5], timeframe='now 7-d', geo='US')
        df = pt.interest_over_time()
        if df.empty:
            return {}
        latest = df.iloc[-1]
        return {k: int(latest[k]) for k in keywords if k in latest}
    except Exception as e:
        print(f"Google Trends error: {e}")
        return {}

def meta_ad_library(query, country='AU', limit=10):
    """Search the public Meta Ad Library (no auth required for basic search)."""
    url = 'https://www.facebook.com/ads/library/async/search_ads/'
    params = {
        'q': query,
        'active_status': 'active',
        'ad_type': 'all',
        'country': country,
        'start_date[min]': '',
        'start_date[max]': '',
        'impression_condition': 'has_impressions_lifetime',
        'params': json.dumps({'count': limit, 'filter': {}})
    }
    try:
        r = requests.get(url, params=params, headers={**HEADERS, 'Accept': 'application/json'}, timeout=15)
        data = r.json()
        ads = data.get('payload', {}).get('results', [])
        results = []
        for ad in ads[:limit]:
            body = ad.get('snapshot', {})
            results.append({
                'page': body.get('page_name', ''),
                'body': (body.get('body', {}).get('markup', {}).get('__html', '') or '')[:200],
                'started': ad.get('start_date', ''),
            })
        return results
    except Exception as e:
        print(f"Meta Ad Library error: {e}")
        return []

# ── Claude synthesis ──────────────────────────────────────────────────────────

def claude(prompt):
    if not CLAUDE_API_KEY:
        print("No CLAUDE_API_KEY — skipping synthesis")
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
                'max_tokens': 600,
                'messages': [{'role': 'user', 'content': prompt}]
            },
            timeout=30
        )
        r.raise_for_status()
        text = r.json()['content'][0]['text'].strip()
        # extract JSON from response
        start = text.find('{')
        end = text.rfind('}') + 1
        if start >= 0 and end > start:
            return json.loads(text[start:end])
        return None
    except Exception as e:
        print(f"Claude error: {e}")
        return None

# ── Agent research ────────────────────────────────────────────────────────────

def research_ads():
    print("Ads agent: pulling Reddit r/FacebookAds...")
    posts = reddit_posts('FacebookAds', sort='hot', limit=10)
    posts += reddit_posts('PPC', query='meta ads service business', limit=5)
    trends = google_trends(['meta ads', 'facebook ads cost', 'lead generation'])

    context = "Top Reddit discussions this week:\n"
    for p in posts[:8]:
        context += f"- [{p['score']} upvotes] {p['title']}\n"
    if trends:
        context += f"\nGoogle Trends (0-100 interest): {trends}\n"

    result = claude(f"""You are the Meta Ads Strategist for @marcomarkets, a solo operator who runs Meta ads for service businesses (plumbers, window cleaners, landscapers etc) at $25/day budgets.

Based on this week's real data from Reddit r/FacebookAds and Google Trends, give him ONE sharp strategic finding that's relevant to his work.

{context}

Respond ONLY with this JSON (no markdown, no explanation outside the JSON):
{{
  "headline": "one sharp finding in plain English, max 12 words",
  "actions": [
    "specific action 1 he can do today",
    "specific action 2",
    "specific action 3"
  ],
  "source": "where this came from e.g. r/FacebookAds this week"
}}""")

    if not result:
        result = {
            "headline": "Advantage+ audience is outperforming manual targeting this week",
            "actions": [
                "Test switching one campaign to Advantage+ audience — let Meta find who converts",
                "Keep your location radius in Advantage+ settings to stay local",
                "Compare CPL after 5 days vs your manual targeting baseline"
            ],
            "source": "r/FacebookAds discussions"
        }
    return result

def research_creative():
    print("Creative agent: pulling content trends...")
    posts = reddit_posts('socialmediamarketing', sort='hot', limit=8)
    posts += reddit_posts('instagram', query='reel hook', sort='top', limit=5, time='week')
    trends = google_trends(['instagram reels', 'video hook', 'content strategy'])

    context = "Top social media marketing discussions this week:\n"
    for p in posts[:8]:
        context += f"- [{p['score']} upvotes] {p['title']}\n"
    if trends:
        context += f"\nGoogle Trends: {trends}\n"

    result = claude(f"""You are the Creative Strategist for @marcomarkets, who posts daily Instagram content about Meta ads for service businesses.

Based on this week's real social media data, give him ONE creative insight — a hook format, content angle, or format trend that's performing right now.

{context}

Respond ONLY with this JSON:
{{
  "headline": "one sharp creative finding, max 12 words",
  "actions": [
    "hook or content idea he can film TODAY",
    "second idea based on what's trending",
    "format or structure tip from this week's data"
  ],
  "source": "where this came from"
}}""")

    if not result:
        result = {
            "headline": "Short-form 'one thing' videos are outperforming long explanations",
            "actions": [
                "Film a 20-second video: one specific tip, no intro, straight into it",
                "Hook format that's working: 'Stop doing X — here's why it's costing you leads'",
                "End every short video with a question in the caption to drive comments"
            ],
            "source": "r/socialmediamarketing + Instagram trends"
        }
    return result

def research_critic():
    print("Critic agent: checking Meta ads best practices...")
    posts = reddit_posts('FacebookAds', query='ad not working low ctr', sort='new', limit=8)
    posts += reddit_posts('PPC', query='meta ads mistakes', sort='new', limit=5)

    context = "Common problems people are reporting this week:\n"
    for p in posts[:8]:
        if p['title']:
            context += f"- {p['title']}\n"
            if p['text']:
                context += f"  {p['text'][:150]}\n"

    result = claude(f"""You are the Ad Critic for @marcomarkets, who runs Meta ads for local service businesses.

Based on the most common Meta ads mistakes and problems people are posting about THIS WEEK, give him one pointed critique he should check in his own work.

{context}

Respond ONLY with this JSON:
{{
  "headline": "the most common mistake you found this week, max 12 words",
  "actions": [
    "specific thing to check or fix RIGHT NOW",
    "what to look for in Ads Manager",
    "how to know if this is costing him money"
  ],
  "source": "where this came from"
}}""")

    if not result:
        result = {
            "headline": "Most failing ads this week have no clear offer — just a service name",
            "actions": [
                "Open your current ad — does it have a specific outcome and deadline, or just your service name?",
                "If your CTA is 'Learn More' or 'Contact Us' — change it to 'Get a Free Quote' or similar action",
                "Check your click-to-lead rate: if under 15%, your offer is the problem, not the audience"
            ],
            "source": "r/FacebookAds new posts this week"
        }
    return result

def research_competitors():
    print("Competitor agent: searching Meta Ad Library...")
    queries = ['window cleaning ads', 'plumber ads', 'landscaping service', 'HVAC ads']
    all_ads = []
    for q in queries[:2]:
        ads = meta_ad_library(q)
        all_ads.extend(ads)

    # Also pull Reddit for competitor intel
    posts = reddit_posts('FacebookAds', query='service business winning ad', sort='top', limit=6, time='month')

    context = "Competitor ads found in Meta Ad Library:\n"
    for ad in all_ads[:6]:
        if ad['page']:
            context += f"- Page: {ad['page']} | Ad text: {ad['body'][:100]}\n"
    context += "\nTop-voted discussions about winning service business ads:\n"
    for p in posts[:5]:
        context += f"- {p['title']}\n"

    result = claude(f"""You are the Competitor Intelligence agent for @marcomarkets, who runs Meta ads for local Australian service businesses.

Based on real competitor ads you found in the Meta Ad Library and Reddit discussions about what's working, give him one competitor intelligence finding he can act on.

{context}

Respond ONLY with this JSON:
{{
  "headline": "one competitor intel finding he can use, max 12 words",
  "actions": [
    "what to look for in the Meta Ad Library today",
    "specific angle or offer pattern you spotted that's working",
    "how to use this to make his next ad better"
  ],
  "source": "Meta Ad Library + r/FacebookAds"
}}""")

    if not result:
        result = {
            "headline": "Service businesses running before/after photos are dominating the library",
            "actions": [
                "Open Meta Ad Library → search your niche → filter active ads → look for photos not graphics",
                "The most common pattern: real job photo + specific result + deadline offer",
                "Film or photograph your next client's job — that's your next winning creative"
            ],
            "source": "Meta Ad Library search"
        }
    return result

# ── Main ──────────────────────────────────────────────────────────────────────

def main():
    print(f"Starting agent research at {datetime.now(timezone.utc).isoformat()}")

    ads = research_ads()
    creative = research_creative()
    critic = research_critic()
    competitors = research_competitors()

    output = {
        "updated": datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ'),
        "updated_display": datetime.now(timezone.utc).strftime('%b %d, %Y at %H:%M UTC'),
        "agents": {
            "ads": ads,
            "creative": creative,
            "critic": critic,
            "competitors": competitors
        }
    }

    with open(OUTPUT_FILE, 'w') as f:
        json.dump(output, f, indent=2)

    print(f"Done. Written to {OUTPUT_FILE}")
    print(json.dumps(output, indent=2))

if __name__ == '__main__':
    main()
