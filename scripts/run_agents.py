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
    # What hooks and formats are working RIGHT NOW
    posts = reddit_posts('socialmediamarketing', sort='hot', limit=10)
    posts += reddit_posts('InstagramMarketing', sort='hot', limit=8)
    posts += reddit_posts('EntrepreneurRideAlong', query='instagram content viral', sort='top', limit=5, time='week')
    # What service business owners are searching for
    trends = google_trends(['instagram reels views', 'content hook', 'facebook ads creative'])
    # What's failing — so Marco can do the opposite
    failing = reddit_posts('socialmediamarketing', query='instagram reach dropped views down', sort='new', limit=6)

    context = "Top performing content discussions this week:\n"
    for p in posts[:10]:
        context += f"- [{p['score']} upvotes] {p['title']}\n"
        if p['text']:
            context += f"  {p['text'][:120]}\n"
    if trends:
        context += f"\nGoogle Trends (0-100): {trends}\n"
    context += "\nWhat's failing / what people are complaining about:\n"
    for p in failing[:5]:
        context += f"- {p['title']}\n"

    result = claude(f"""You are the Creative Strategist for @marcomarkets. He posts daily Instagram content about Meta ads for local service businesses (plumbers, landscapers, window cleaners). His goal is to grow his following and get service business owners to DM him "ADS".

From this week's REAL data, give him:
1. The single best hook format or content angle performing RIGHT NOW
2. A specific video idea he can film TODAY using that format
3. One thing that's killing reach this week — so he can avoid it

{context}

Respond ONLY with this JSON:
{{
  "headline": "the single biggest content opportunity this week, max 12 words",
  "actions": [
    "specific hook or opening line he can use TODAY — write it out word for word",
    "a complete video idea: format, topic, first line, why it'll work this week",
    "one thing killing reach right now that he should avoid"
  ],
  "source": "where this data came from"
}}""")

    if not result:
        result = {
            "headline": "POV-style talking head hooks outperforming every other format this week",
            "actions": [
                "Open with: 'POV: you just spent $500 on ads and got zero leads — here's the exact reason why'",
                "Film a 30s talking head: start mid-sentence like you're already explaining something urgent. No intro. No 'hey guys'. Straight into the pain point. End with DM me ADS.",
                "Avoid posting carousels this week — algorithmic reach for static posts is down, Reels are getting 3-5x more distribution"
            ],
            "source": "r/socialmediamarketing + r/InstagramMarketing"
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
    print("Competitor agent: deep competitor research...")

    # What content is winning for Meta ads creators on Instagram/YouTube
    posts = reddit_posts('FacebookAds', query='instagram content creator meta ads growing', sort='top', limit=8, time='month')
    posts += reddit_posts('digital_marketing', query='service business instagram growth', sort='top', limit=6, time='month')
    posts += reddit_posts('Entrepreneur', query='local service business marketing instagram', sort='top', limit=5, time='week')

    # What angles competitors use that HAVEN'T been saturated yet
    fresh = reddit_posts('smallbusiness', query='meta ads worked failed', sort='new', limit=8)

    # Trending pain points from Marco's target audience (service biz owners)
    audience_pain = reddit_posts('smallbusiness', sort='hot', limit=10)
    audience_pain += reddit_posts('Entrepreneur', query='local business marketing struggling', sort='new', limit=6)

    context = "What's working for Meta ads content creators and marketers this month:\n"
    for p in posts[:8]:
        context += f"- [{p['score']} upvotes] {p['title']}\n"
        if p['text']:
            context += f"  {p['text'][:120]}\n"

    context += "\nFresh pain points from service business owners RIGHT NOW:\n"
    for p in audience_pain[:8]:
        context += f"- {p['title']}\n"

    context += "\nRecent real experiences with Meta ads (good and bad):\n"
    for p in fresh[:6]:
        context += f"- {p['title']}\n"

    result = claude(f"""You are the Competitor Intelligence agent for @marcomarkets. He creates Instagram content teaching service businesses how to run Meta ads. His competitors are other marketing educators and agency owners on Instagram.

From this week's real data, find him:
1. A content angle or topic his competitors are NOT covering that his audience desperately needs
2. A specific pain point service business owners are posting about RIGHT NOW that he can make a video about tomorrow
3. One thing successful accounts in his niche are doing that he should copy immediately

{context}

Respond ONLY with this JSON:
{{
  "headline": "the biggest gap or opportunity you found vs competitors, max 12 words",
  "actions": [
    "uncovered content angle: specific topic and why competitors are missing it",
    "urgent pain point from real posts this week: write it as a video hook he can film tomorrow",
    "what the top accounts are doing right now that he should steal"
  ],
  "source": "where this data came from"
}}""")

    if not result:
        result = {
            "headline": "No one is teaching service businesses HOW to respond to leads from ads",
            "actions": [
                "Uncovered angle: competitors teach how to get leads but never what to say when the lead comes in — film 'exact script I tell my clients to use when someone fills in the form'",
                "Pain point from this week: 'I got leads from my ads but none of them booked' — hook: 'You got leads but nobody booked. Here is exactly why and how to fix it in one message'",
                "Top accounts posting 3-4x per week minimum with one Reel hitting 10k+ views acting as top of funnel — post volume is the differentiator right now"
            ],
            "source": "r/smallbusiness + r/Entrepreneur + r/FacebookAds"
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
