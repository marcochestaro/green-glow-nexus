#!/usr/bin/env python3
"""
Weekly Miro carousel board creator.
Runs every Sunday alongside the script generator.
Creates 3 new carousel boards from a rotating topic pool — no Claude API needed.
Tracks created boards in dashboard/miro-boards.json to avoid repeats.
"""

import os, json, requests
from datetime import datetime, timezone

MIRO_TOKEN = os.environ.get('MIRO_ACCESS_TOKEN', '')
BOARDS_FILE = os.path.join(os.path.dirname(__file__), '..', 'dashboard', 'miro-boards.json')

API = 'https://api.miro.com/v2'
HEADERS = {
    'Authorization': f'Bearer {MIRO_TOKEN}',
    'Content-Type': 'application/json',
    'Accept': 'application/json',
}

# Full topic pool — will rotate through without repeating until exhausted
CAROUSEL_TOPICS = [
    {
        "title": "$25/Day Ad Budget Math — How It Actually Works",
        "slides": [
            ("$25/day doesn't sound like much.", "But here's the actual math that gets service businesses booked."),
            ("Day 1–5: Learning phase", "Meta is figuring out who clicks. Don't judge results yet. Let it run."),
            ("Day 6–14: Optimisation kicks in", "CPL drops. Leads start coming in. This is where it starts working."),
            ("Day 15–30: Compound effect", "The algorithm has data. Cost per lead is at its lowest. Consistent bookings."),
            ("The result after 30 days?", "Real clients. DM me ADS if you want this for your business."),
        ]
    },
    {
        "title": "The 4 Elements of a Winning Local Ad",
        "slides": [
            ("Every high-converting local ad has exactly 4 things.", "Most service businesses are missing at least 2."),
            ("1. A specific hook", "Not 'we're professional and reliable.' Something that makes them stop scrolling."),
            ("2. A clear outcome", "Not what you do — what they GET. 'Clean gutters in 2 hours, no mess left behind.'"),
            ("3. Proof", "A real photo. A real number. A real client result. One is enough."),
            ("4. One simple CTA", "'Get a free quote' beats 'learn more' every time. Make it easy to say yes."),
        ]
    },
    {
        "title": "Why Your Meta Ad Isn't Getting Leads",
        "slides": [
            ("Your ad is live. No leads. Here's exactly why.", "It's almost always one of these 3 things."),
            ("Mistake 1: Weak hook", "The first 3 seconds didn't make them stop. They kept scrolling. The rest didn't matter."),
            ("Mistake 2: No specific offer", "You listed your service. You didn't give them a reason to act RIGHT NOW."),
            ("Mistake 3: Wrong objective", "Boosting a post isn't the same as running a Lead Generation campaign. Different result entirely."),
            ("Fix one of these today.", "DM me ADS and I'll tell you which one is costing you the most."),
        ]
    },
    {
        "title": "Meta vs Google — The Honest Answer for Service Businesses",
        "slides": [
            ("Everyone asks: Meta or Google?", "Here's the honest breakdown for local service businesses."),
            ("Google Ads: High intent, high cost", "People are searching right now. But CPL can hit $80–$150+ for competitive trades."),
            ("Meta Ads: Lower cost, broader reach", "CPL of $20–$50 is realistic. You interrupt people — so your creative has to be good."),
            ("The real answer?", "Start with Meta at $25/day. Get leads. Prove the model. Scale to Google later."),
            ("For most tradies just starting?", "Meta wins. DM me ADS to talk through your specific situation."),
        ]
    },
    {
        "title": "What Happens in the First 30 Days of Meta Ads",
        "slides": [
            ("Most service businesses quit Meta ads inside 2 weeks.", "Here's exactly what's supposed to happen — and when."),
            ("Week 1: The learning phase", "Meta is testing audiences and placements. Costs look high. This is normal. Don't touch it."),
            ("Week 2: First real leads", "The algorithm has enough data to start finding your buyer. Leads come in but inconsistently."),
            ("Week 3–4: Consistency", "CPL drops. Bookings become predictable. The hard part is behind you."),
            ("The only way to fail is to stop.", "DM me ADS if you want to see real numbers from this process."),
        ]
    },
    {
        "title": "How to Write an Ad Headline That Actually Converts",
        "slides": [
            ("Most service business ad headlines are invisible.", "Here's the formula that makes them stop."),
            ("The formula: Pain + Timeframe + Outcome", "You don't need to be clever. You need to be specific."),
            ("Bad headline: 'Professional Window Cleaning Services'", "Zero reason to click. Sounds like everyone else."),
            ("Good headline: 'Get your windows spotless before the weekend — we come to you'", "Specific. Local. Time-anchored. Outcome clear."),
            ("Try rewriting yours with this formula.", "DM me ADS if you want me to look at your current headline."),
        ]
    },
    {
        "title": "The Referral Trap — Why Word of Mouth Is Keeping You Stuck",
        "slides": [
            ("Referrals feel safe. But they're actually limiting your growth.", "Here's why."),
            ("You can't control when referrals come in.", "Feast and famine. You're at the mercy of other people's conversations."),
            ("You can't scale what you can't predict.", "A referral business has a ceiling. An ad-driven business has a dial."),
            ("Referrals reward being liked. Ads reward being found.", "Different games. Different growth trajectories."),
            ("You don't have to choose — but you do have to add ads.", "DM me ADS to build the predictable side of your business."),
        ]
    },
    {
        "title": "Why Broad Audiences Beat Narrow Targeting for Local Service Ads",
        "slides": [
            ("Most service businesses over-target their Meta ads.", "And it's costing them money."),
            ("Narrow targeting = small pool + high CPM", "You're telling Meta to find a rare person. That's expensive."),
            ("Broad targeting = Meta does the work", "Let the algorithm find who's most likely to convert. It's better at this than you are."),
            ("The only thing to restrict: location", "Set your radius. Then let Meta optimise everything else."),
            ("Trust the algorithm for who. Control the geography.", "DM me ADS if you want help setting this up."),
        ]
    },
    {
        "title": "Retargeting — The Cheapest Leads You'll Ever Get",
        "slides": [
            ("Most service businesses run one campaign and wonder why leads are expensive.", "Retargeting is the answer."),
            ("What is retargeting?", "Showing ads only to people who've already seen your content or visited your page."),
            ("Why it's cheaper", "These people already know you exist. Conversion rate is 3–5x higher than cold traffic."),
            ("How to set it up", "Create a custom audience from Instagram engagers or website visitors. Budget $5–10/day on top of your cold campaign."),
            ("Cold campaign finds them. Retargeting closes them.", "DM me ADS to add this to your setup."),
        ]
    },
    {
        "title": "How a Window Cleaner Got 11 Jobs in 30 Days With Meta Ads",
        "slides": [
            ("Real numbers from a real client.", "Window cleaner. $25/day. 30 days. Here's what happened."),
            ("Week 1: Setup + learning phase", "3 leads. Cost per lead: $58. Felt slow. We kept it running."),
            ("Week 2: Algorithm optimises", "7 leads. CPL dropped to $31. 4 booked jobs confirmed."),
            ("Week 3–4: Consistency hits", "11 leads. CPL: $22. 7 booked jobs. $700 spent. Revenue from ads: $2,800+."),
            ("4x return on ad spend in 30 days.", "DM me ADS if you want results like this for your business."),
        ]
    },
    {
        "title": "The Boosted Post Trap — Why It's Not the Same as a Real Ad",
        "slides": [
            ("Boosting a post is not running a Meta ad.", "Here's the difference — and why it matters for your leads."),
            ("Boosted post: optimised for engagement", "Meta shows it to people likely to like or comment. Not to people likely to book."),
            ("Real Lead Ad: optimised for conversions", "Meta shows it to people who've shown buying intent. Completely different audience."),
            ("Boosted posts build vanity metrics.", "Real campaigns build pipelines. Same budget. Very different results."),
            ("Stop boosting. Start campaigning.", "DM me ADS to set up your first real lead generation campaign."),
        ]
    },
    {
        "title": "How to Set Up a Lead Form That Actually Converts",
        "slides": [
            ("Your Meta lead form is losing you bookings.", "Here's how to fix it in 10 minutes."),
            ("Keep it to 3 fields max", "Name, phone, suburb. Every extra field drops your conversion rate by 10–20%."),
            ("Write a custom thank-you message", "Don't use the default. Tell them exactly what happens next: 'I'll call you within 2 hours.'"),
            ("Add a qualifying question", "One question only. 'Are you looking to book within the next 2 weeks?' Filters time-wasters."),
            ("Follow up within 1 hour", "Speed to lead is everything. After 1 hour, your close rate drops by 80%."),
        ]
    },
]


def load_used_topics():
    if os.path.exists(BOARDS_FILE):
        try:
            with open(BOARDS_FILE) as f:
                data = json.load(f)
                return data.get('used_titles', []), data.get('boards', [])
        except Exception:
            pass
    return [], []


def save_boards(boards, used_titles):
    os.makedirs(os.path.dirname(BOARDS_FILE), exist_ok=True)
    data = {
        "updated": datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ'),
        "updated_display": datetime.now(timezone.utc).strftime('%b %d, %Y at %H:%M UTC'),
        "boards": boards,
        "used_titles": used_titles,
    }
    with open(BOARDS_FILE, 'w') as f:
        json.dump(data, f, indent=2)


def create_board(title):
    r = requests.post(f'{API}/boards', headers=HEADERS, json={
        "name": title,
        "description": "Weekly carousel — @marcomarkets",
        "policy": {"permissionsPolicy": {"collaborationToolsStartAccess": "all_editors", "copyAccess": "anyone", "sharingAccess": "team_members_with_editing_rights"}},
    }, timeout=20)
    r.raise_for_status()
    return r.json()


def add_slide_doc(board_id, slides):
    content = ""
    for i, (heading, body) in enumerate(slides, 1):
        content += f"## Slide {i}\n**{heading}**\n\n{body}\n\n---\n\n"
    r = requests.post(f'{API}/boards/{board_id}/documents', headers=HEADERS, json={
        "data": {"content": content, "type": "text"},
        "style": {"textAlign": "left"},
        "position": {"x": 0, "y": 0},
        "geometry": {"width": 800},
    }, timeout=20)
    r.raise_for_status()
    return r.json()


def main():
    if not MIRO_TOKEN:
        print("No MIRO_ACCESS_TOKEN — skipping Miro board creation")
        return

    used_titles, existing_boards = load_used_topics()

    # Pick topics not yet used; if pool exhausted, reset
    available = [t for t in CAROUSEL_TOPICS if t['title'] not in used_titles]
    if len(available) < 3:
        print("Topic pool exhausted — resetting rotation")
        used_titles = []
        available = CAROUSEL_TOPICS[:]

    this_week = available[:3]
    new_boards = list(existing_boards)
    newly_used = list(used_titles)

    for topic in this_week:
        print(f"Creating board: {topic['title']}")
        try:
            board = create_board(topic['title'])
            board_id = board['id']
            view_link = board.get('viewLink', f"https://miro.com/app/board/{board_id}/")
            add_slide_doc(board_id, topic['slides'])
            new_boards.append({
                "title": topic['title'],
                "board_id": board_id,
                "url": view_link,
                "created": datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ'),
            })
            newly_used.append(topic['title'])
            print(f"  → {view_link}")
        except Exception as e:
            print(f"  Error creating board: {e}")

    save_boards(new_boards, newly_used)
    print(f"Done. {len(this_week)} boards created.")


if __name__ == '__main__':
    main()
