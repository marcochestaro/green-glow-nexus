#!/usr/bin/env python3
"""
Weekly Miro carousel board creator — topic-aware visual layouts.
Same visual style (light gray bg, circles, labels, connectors, callout boxes)
but layout adapts to the topic type so each board looks different.
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

WHITE = '#ffffff'
DARK  = '#1e293b'
GRAY  = '#64748b'

# Per-layout color palettes
FUNNEL_COLORS  = ['#3b82f6', '#06b6d4', '#14b8a6', '#16a34a', '#15803d']
PROBLEM_COLORS = ['#ef4444', '#f97316', '#8b5cf6', '#06b6d4', '#eab308']
STEP_COLOR     = '#3b82f6'
COMP_LEFT      = '#ef4444'
COMP_RIGHT     = '#16a34a'
CASE_COLORS    = ['#94a3b8', '#60a5fa', '#3b82f6', '#1d4ed8', '#1e3a8a']


# 41 unique topics — pool exhausts before repeating.
# layout: funnel | problems | steps | comparison | case_study
CAROUSEL_TOPICS = [
    # ── Budget & math ───────────────────────────────────────────────────────────
    {
        "title": "The ROI Math Behind a Profitable Meta Campaign",
        "layout": "funnel",
        "slides": [
            ("AD SPEND", "Every dollar you put in is tracked and accountable."),
            ("COST PER LEAD", "A well-optimised campaign brings CPL down week over week."),
            ("CLOSE RATE", "If you close 30% of leads, 20 leads = 6 booked jobs."),
            ("REVENUE", "Average job value x booked jobs = your revenue from ads."),
            ("3x+ ROAS", "One booked job covers a full week of ad spend — often more."),
        ],
        "callout": "one booked job covers the full week of ad spend — often 5-10x over depending on the trade",
    },
    {
        "title": "Why Your Ad Spend Feels Wasted (And How to Fix It)",
        "layout": "problems",
        "slides": [
            ("TOO EARLY", "You judged it before Meta exited the learning phase. It needed more time."),
            ("CHANGED IT", "Every edit resets the learning phase. Patience is the actual strategy."),
            ("WRONG OBJECTIVE", "Traffic campaigns get clicks. Lead campaigns get leads. Not the same thing."),
        ],
        "callout": "set it up right once — then leave it alone for 14 days",
    },
    # ── Ad creative & copy ──────────────────────────────────────────────────────
    {
        "title": "The 4 Elements of a Winning Local Ad",
        "layout": "steps",
        "slides": [
            ("STRONG HOOK", "Not 'professional and reliable.' Something that stops the scroll in 3 seconds."),
            ("CLEAR OUTCOME", "Not what you do — what they GET. Specific and tangible."),
            ("REAL PROOF", "A real photo. A real number. A real result. One is enough."),
            ("SIMPLE CTA", "'Get a free quote' beats 'learn more' every time. Make it easy to say yes."),
        ],
        "callout": "most service businesses are missing at least 2 of these 4",
    },
    {
        "title": "How to Write an Ad Headline That Actually Converts",
        "layout": "comparison",
        "slides": [
            ("INVISIBLE HEADLINE", "Professional Window Cleaning Services — zero reason to click. Sounds like everyone else."),
            ("CONVERTING HEADLINE", "Get your windows spotless before the weekend — we come to you — specific, local, outcome-driven."),
        ],
        "formula": "Pain + Timeframe + Outcome",
        "callout": "you don't need to be clever — you need to be specific",
    },
    {
        "title": "5 Hook Formulas That Work for Every Service Business Ad",
        "layout": "steps",
        "slides": [
            ("THE NUMBER", "'3 mistakes killing your ad results' — specificity creates curiosity."),
            ("THE CALL-OUT", "'If you're a plumber in Brisbane running ads, watch this' — instant relevance."),
            ("THE RESULT", "'How this landscaper got 14 leads in a week' — proof before explanation."),
            ("AGAINST THE GRAIN", "'Stop targeting homeowners — here's what actually works'"),
            ("THE PAIN", "'You ran ads. Nobody called. Here's the exact reason why.'"),
        ],
        "callout": "the first 3 seconds decide everything — steal these",
    },
    {
        "title": "What 'Professional and Reliable' Is Actually Costing You",
        "layout": "comparison",
        "slides": [
            ("WHAT YOU'RE SAYING", "'Professional and reliable' — in every ad, ignored by everyone, costs you clicks."),
            ("WHAT WORKS", "'Responded in 2 hours, job done same day, no callbacks' — specific proof beats adjectives every time."),
        ],
        "formula": "Replace claims with proof. Replace adjectives with outcomes.",
        "callout": "specific always beats generic",
    },
    {
        "title": "How to Use a Real Job Photo to 3x Your Click Rate",
        "layout": "steps",
        "slides": [
            ("BEFORE/AFTER", "The most reliable visual format in any trade. Instant proof."),
            ("MID-JOB SHOT", "Shows the work is real. Authenticity outperforms polish every time."),
            ("YOU IN THE FRAME", "A face in the photo builds trust. Stock images don't."),
            ("THE RESULT", "Clean, sharp, finished work. Let the job speak for itself."),
        ],
        "callout": "real beats polished every time in local service ads",
    },
    # ── Mistakes & fixes ────────────────────────────────────────────────────────
    {
        "title": "Why Your Meta Ad Isn't Getting Leads",
        "layout": "problems",
        "slides": [
            ("WEAK HOOK", "First 3 seconds didn't stop the scroll. The rest didn't matter."),
            ("NO OFFER", "You listed your service. You didn't give them a reason to act right now."),
            ("WRONG SETUP", "Boosting a post isn't the same as a Lead Generation campaign."),
        ],
        "callout": "fix one of these today — they're almost always the cause",
    },
    {
        "title": "The Boosted Post Trap — Why It's Not the Same as a Real Ad",
        "layout": "comparison",
        "slides": [
            ("BOOSTED POST", "Optimised for engagement — Meta shows it to people who like and comment, not people who book."),
            ("REAL LEAD AD", "Optimised for conversions — Meta finds people with buying intent. Completely different audience."),
        ],
        "formula": "Same budget. Very different results.",
        "callout": "stop boosting — start running lead generation campaigns",
    },
    {
        "title": "Why Your Ad Works for 3 Days Then Dies",
        "layout": "problems",
        "slides": [
            ("AUDIENCE TAPPED", "You've shown it to everyone in your radius who'll click. The pool is exhausted."),
            ("MICRO-NICHE", "Narrow targeting runs out fast. Broad audiences have more runway."),
            ("ONE CREATIVE", "Rotate 2-3 images or videos. Fresh creative restarts performance."),
        ],
        "callout": "broaden the audience and add a second creative",
    },
    {
        "title": "5 Things to Check in Ads Manager Every Week",
        "layout": "steps",
        "slides": [
            ("COST PER LEAD", "Should trend down after day 14. Going up means creative is fatiguing."),
            ("FREQUENCY", "Hits 3+? Your audience has seen it 3 times. Refresh the creative."),
            ("CLICK-THROUGH RATE", "Under 1%? The hook is the problem. 2%+ means creative is working."),
            ("LEAD QUALITY", "Are leads booking? If not, targeting or offer needs adjusting."),
            ("SPEND vs LEADS", "Simple division. Know your CPL every single week."),
        ],
        "callout": "most businesses set up their ad and never look at it again",
    },
    # ── Platform & strategy ─────────────────────────────────────────────────────
    {
        "title": "Meta vs Google — The Honest Answer for Service Businesses",
        "layout": "comparison",
        "slides": [
            ("GOOGLE ADS", "High intent, high cost — CPL can hit $80-$150+ for competitive trades. People are actively searching."),
            ("META ADS", "Lower cost, broader reach — CPL of $20-$50 is realistic. You interrupt them so creative matters."),
        ],
        "formula": "Start with Meta. Prove the model. Scale to Google later.",
        "callout": "for most service businesses starting out — Meta wins",
    },
    {
        "title": "How the Meta Algorithm Decides Who Sees Your Ad",
        "layout": "funnel",
        "slides": [
            ("OBJECTIVE", "Lead gen objective tells Meta to find people who fill out forms."),
            ("CREATIVE SIGNAL", "High CTR = relevance. Meta rewards relevant ads with cheaper reach."),
            ("AUDIENCE SIGNALS", "Location, interests, past converters — all shape who gets targeted."),
            ("OPTIMISATION", "Meta learns with every conversion event. Gets smarter over time."),
            ("CHEAPER LEADS", "Better creative = lower CPL. The algorithm rewards performance."),
        ],
        "callout": "the better your creative, the cheaper your leads",
    },
    {
        "title": "Why I Only Run Meta Ads for Service Businesses",
        "layout": "problems",
        "slides": [
            ("LOCAL TARGETING", "Hit a 20km radius around any suburb. Precision that's hard to match elsewhere."),
            ("CONTROLLABLE CPL", "Real data fast on a lean budget. You see what's working before scaling."),
            ("VISUAL PROOF", "Before/after photos and job footage perform perfectly on Instagram and Facebook."),
            ("BUYERS ARE THERE", "Every homeowner and property manager is already on Meta. Your audience is waiting."),
        ],
        "callout": "focused on service businesses — the ROI math just works",
    },
    # ── Targeting & audiences ───────────────────────────────────────────────────
    {
        "title": "Why Broad Audiences Beat Narrow Targeting for Local Service Ads",
        "layout": "comparison",
        "slides": [
            ("NARROW TARGETING", "Small pool + high CPM — you're telling Meta to find a rare person. Expensive."),
            ("BROAD TARGETING", "Meta does the work — the algorithm finds who's most likely to convert. Cheaper, faster."),
        ],
        "formula": "The only thing to restrict: your location radius.",
        "callout": "trust the algorithm for who — control the geography",
    },
    {
        "title": "Retargeting — The Cheapest Leads You'll Ever Get",
        "layout": "steps",
        "slides": [
            ("COLD CAMPAIGN", "Finds new people. Higher CPL. Builds awareness across your area."),
            ("THEY SEE YOU", "Visit your page, watch your video, engage with a post. Now Meta knows them."),
            ("RETARGETING HITS", "Show ads only to warm people who already know you exist."),
            ("THEY CONVERT", "3-5x higher conversion rate than cold traffic. Same product, cheaper lead."),
        ],
        "callout": "cold campaign finds them — retargeting closes them",
    },
    {
        "title": "Lookalike Audiences — When to Use Them and When Not To",
        "layout": "steps",
        "slides": [
            ("WHAT IT DOES", "Meta finds people similar to your existing customers or leads."),
            ("THE PROBLEM", "You need 100+ source events minimum — fewer and it's inaccurate."),
            ("WHEN TO USE IT", "After 3-6 months. Upload your booked client list. Build from there."),
            ("FOR NOW", "Broad + location beats lookalike every time until your data is solid."),
        ],
        "callout": "powerful — but only when you have enough data to feed it",
    },
    # ── Lead forms & conversion ─────────────────────────────────────────────────
    {
        "title": "How to Set Up a Lead Form That Actually Converts",
        "layout": "steps",
        "slides": [
            ("3 FIELDS MAX", "Name, phone, suburb. Every extra field drops conversion rate by 10-20%."),
            ("CUSTOM THANK YOU", "Tell them exactly what happens next. 'I'll call you within 2 hours.'"),
            ("ONE QUALIFIER", "One question only. Filters time-wasters without killing conversion."),
            ("FOLLOW UP FAST", "Speed to lead is everything. After 1 hour, close rate drops 80%."),
        ],
        "callout": "your form is losing you bookings — fix it in 10 minutes",
    },
    {
        "title": "Why Speed to Lead Is Worth More Than Your Ad Creative",
        "layout": "funnel",
        "slides": [
            ("LEAD COMES IN", "They filled out your form. They're interested right now."),
            ("5 MINUTES", "Contact within 5 minutes — 9x more likely to convert."),
            ("30 MINUTES", "Conversion rate drops sharply. They're already comparing options."),
            ("1 HOUR", "Close rate down 80%. They've moved on or called someone else."),
            ("24 HOURS", "Effectively gone. They've forgotten they even filled in the form."),
        ],
        "callout": "your follow-up speed is your competitive advantage",
    },
    {
        "title": "What to Say When a Lead Calls From Your Meta Ad",
        "layout": "steps",
        "slides": [
            ("DON'T OPEN WITH PRICE", "Price before value kills the sale. Get context first."),
            ("ASK WHAT'S GOING ON", "Let them explain the problem. You're solving it — not just quoting it."),
            ("CONFIRM THEIR TIMELINE", "'When do you need this done by?' Urgency tells you how hot the lead is."),
            ("GIVE A NEXT STEP", "'I can come out Thursday at 10am — does that work?' Close the loop."),
        ],
        "callout": "most service businesses fumble this moment — don't",
    },
    # ── Mindset & positioning ───────────────────────────────────────────────────
    {
        "title": "The Referral Trap — Why Word of Mouth Is Keeping You Stuck",
        "layout": "comparison",
        "slides": [
            ("REFERRALS", "You can't control when they come in. Feast and famine. At the mercy of other people's conversations."),
            ("ADS", "A predictable lead dial you control. You decide volume. You decide when to scale."),
        ],
        "formula": "Referrals reward being liked. Ads reward being found.",
        "callout": "you can't scale what you can't predict",
    },
    {
        "title": "Why Service Businesses Are Built for Meta Ads",
        "layout": "problems",
        "slides": [
            ("LOCATION IS SPECIFIC", "Your ad only needs to reach people in your suburb. Tiny pool. Cheap reach."),
            ("WORK IS VISUAL", "Before/after photos and job footage — Instagram was built for this."),
            ("HIGH JOB VALUE", "One new client from ads could be worth hundreds to thousands over their lifetime."),
            ("LOW COMPETITION", "Most service businesses aren't running Meta ads yet. You dominate by showing up."),
        ],
        "callout": "the ROI math works better for you than for any product brand",
    },
    {
        "title": "The Gap Between Service Businesses and Marketing Agencies",
        "layout": "comparison",
        "slides": [
            ("GENERIC AGENCY", "Runs the same ads they'd run for a dentist or a gym — doesn't know your job values, close rates, or what a booked job is worth."),
            ("WHAT YOU ACTUALLY NEED", "Simple lead gen campaign. A clear offer. A follow-up system. Someone who knows your trade numbers."),
        ],
        "formula": "You don't need a big agency. You need the right system.",
        "callout": "the gap is real — and it's costing service businesses leads",
    },
    # ── Client results ──────────────────────────────────────────────────────────
    {
        "title": "How a Window Cleaner Got 11 Jobs in 30 Days With Meta Ads",
        "layout": "case_study",
        "slides": [
            ("WEEK 1", "3 leads at $58 CPL — felt slow, kept it running"),
            ("WEEK 2", "7 leads at $31 CPL — 4 booked jobs confirmed"),
            ("WEEK 3", "11 leads at $22 CPL — 7 booked, algorithm dialled in"),
            ("MONTH 1", "4x return on ad spend — $700 in, $2,800+ revenue out"),
        ],
        "callout": "week 1 is always the hardest — the businesses that quit never see week 3",
    },
    {
        "title": "How a Plumber Cut His Cost Per Lead From $120 to $38",
        "layout": "case_study",
        "slides": [
            ("THE PROBLEM", "Running a Traffic campaign — Meta was sending clicks, not leads. CPL: $120"),
            ("FIX 1", "Switched to Lead Generation objective — CPL dropped to $71"),
            ("FIX 2", "Simplified lead form to 3 fields — CPL dropped to $38"),
            ("THE RESULT", "Same budget, same audience — better setup changed everything"),
        ],
        "callout": "the setup matters more than the budget",
    },
    {
        "title": "Car Detailer. First Meta Campaign. Real Numbers.",
        "layout": "case_study",
        "slides": [
            ("WEEK 1", "5 leads at $35 CPL — 2 booked, early signal is good"),
            ("WEEK 2", "9 leads at $28 CPL — 4 booked, CPL dropping"),
            ("WEEKS 3-4", "14 leads at $22 CPL — 7 booked, algorithm dialled in"),
            ("MONTH 1", "3.5x ROAS — first campaign, never run ads before"),
        ],
        "callout": "first campaign, never run ads before — the results are there when it's set up right",
    },
    {
        "title": "Landscaper: $0 to Fully Booked in 6 Weeks",
        "layout": "case_study",
        "slides": [
            ("WEEKS 1-2", "Testing 2 creatives — before/after won by 40% over job site photo"),
            ("WEEK 3", "First booked jobs from ads — covered the full month of ad spend"),
            ("WEEK 4", "Waiting list started forming — raised prices"),
            ("WEEK 6", "Fully booked, referring overflow, running entirely on ads"),
        ],
        "callout": "same skills, same area — just visible now",
    },
    # ── Content & Instagram growth ──────────────────────────────────────────────
    {
        "title": "What Happens in the First 30 Days of Meta Ads",
        "layout": "funnel",
        "slides": [
            ("DAY 1-7", "Learning phase — Meta tests audiences and placements. Costs look high. Normal. Don't touch."),
            ("DAY 8-14", "First real leads — algorithm has data, finds your buyer. Inconsistent but real."),
            ("DAY 15-21", "Consistency starts — CPL drops. Bookings become more predictable."),
            ("DAY 22-30", "Dialled in — CPL stable, leads steady. The hard part is behind you."),
        ],
        "callout": "the only way to fail is to stop",
    },
    {
        "title": "Why Posting Every Day on Instagram Actually Works for Getting Clients",
        "layout": "steps",
        "slides": [
            ("TRUST TOUCHPOINTS", "A potential client might see 10 posts before they DM you. That's 10 reasons to trust you."),
            ("ALGORITHM REWARDS VOLUME", "Post daily for 30 days and your baseline reach increases. Consistency compounds."),
            ("WARM TRAFFIC", "When someone sees your content and then your ad, conversion cost drops significantly."),
            ("SHOW THE WORK", "Post the jobs. Real photos. Real results. That's the whole strategy."),
        ],
        "callout": "post daily — keep it simple — show the work",
    },
    {
        "title": "The 3-Second Rule — Why Most Reels Fail Immediately",
        "layout": "comparison",
        "slides": [
            ("WHAT KILLS IT", "'Hey guys, welcome back, today I want to talk about...' — already scrolled past before you finish the sentence."),
            ("WHAT WORKS", "Start mid-sentence. Drop them into the middle of something. Act like they've been watching for 10 seconds."),
        ],
        "formula": "Open with the most interesting thing you have to say.",
        "callout": "if you don't hook them in 3 seconds, they're gone",
    },
    {
        "title": "5 Instagram Post Ideas for Any Service Business This Week",
        "layout": "steps",
        "slides": [
            ("BEFORE/AFTER", "The most reliable format in any trade. One photo. Instant proof."),
            ("COMMON MISTAKE", "'The #1 mistake homeowners make before calling a plumber' — instant authority."),
            ("YOUR PROCESS", "Show what actually happens when they hire you. Demystify the job."),
            ("A PRICE MYTH", "'What does a full detail actually cost?' Transparent = trustworthy."),
            ("CLIENT RESULT", "'This took 45 minutes and saved $800 in repairs.' Specific = believable."),
        ],
        "callout": "pick one, shoot it today — consistency beats perfection",
    },
    # ── Offer & positioning ─────────────────────────────────────────────────────
    {
        "title": "How to Write an Offer That Makes People Want to Call",
        "layout": "comparison",
        "slides": [
            ("WEAK OFFER", "'Free quote on all jobs' — everyone offers this. No urgency, no reason to choose you."),
            ("STRONG OFFER", "'Book this week and we'll have it done same-day — or it's free' — specific, urgent, risk reversed."),
        ],
        "formula": "Specific outcome + timeframe + risk reversal.",
        "callout": "you don't need a discount — you need a reason to act now",
    },
    {
        "title": "The Difference Between a Good Ad and a Great Ad",
        "layout": "comparison",
        "slides": [
            ("GOOD AD", "Describes the service and speaks to everyone. 'Professional window cleaning. Fast. Reliable. Call us today.'"),
            ("GREAT AD", "Describes the transformation and speaks to one person. 'Spotless windows in 90 minutes — book online.'"),
        ],
        "formula": "Good ads get clicks. Great ads get bookings.",
        "callout": "speak to one person — make them feel like you wrote it for them",
    },
    {
        "title": "Why 'Get a Free Quote' Is the Weakest CTA You Can Use",
        "layout": "comparison",
        "slides": [
            ("WEAK CTA", "'Get a free quote' — table stakes, everyone offers it, zero reason to choose you over the next result."),
            ("STRONG CTA", "'Book your spot' or 'Get your price in 60 seconds' — implies scarcity, speed, and a clear next step."),
        ],
        "formula": "Make your CTA feel like the first step of something good.",
        "callout": "your CTA is the last thing standing between them and a lead",
    },
    # ── Scaling & systems ───────────────────────────────────────────────────────
    {
        "title": "When to Scale Your Meta Ad Budget (And When Not To)",
        "layout": "funnel",
        "slides": [
            ("PROFITABLE CPL", "Only scale if you're already profitable. More budget on a broken campaign loses money faster."),
            ("14 DAYS CONSISTENT", "Same CPL week over week, leads converting to jobs — now consider scaling."),
            ("20% INCREASES ONLY", "Don't double the budget overnight. 20% bumps preserve the algorithm's optimisation."),
            ("WATCH FOR 7 DAYS", "After each increase, monitor CPL for a week before the next bump."),
            ("THEN SCALE AGAIN", "Repeat. Slow and steady scales without breaking the campaign."),
        ],
        "callout": "scale when it's working — fix it when it's not",
    },
    {
        "title": "How to Run Meta Ads in a Slow Season Without Wasting Money",
        "layout": "steps",
        "slides": [
            ("DON'T TURN IT OFF", "Turning off resets the learning phase. Drop budget to a low minimum to keep the algorithm warm."),
            ("SHIFT OBJECTIVE", "Run engagement or awareness ads during slow season. Build the audience for when demand returns."),
            ("RETARGET WARM PEOPLE", "Run low-budget retargeting to stay top of mind with people who've engaged."),
            ("STAY VISIBLE", "Businesses that run through slow season own market share when demand picks up."),
        ],
        "callout": "slow season is when your competitors go quiet — don't",
    },
    {
        "title": "How to Test 2 Ads Without Wasting Your Budget",
        "layout": "steps",
        "slides": [
            ("SAME AD SET", "Same audience, same budget — two different creatives. Let Meta split traffic between them."),
            ("TEST CREATIVE FIRST", "Don't test audience, budget, and creative at once. One variable at a time."),
            ("WAIT FOR 50+ IMPRESSIONS", "Not after 2 days. Give Meta time to find the right people for each creative."),
            ("KILL THE LOSER", "Scale the winner. Simple. Repeatable. No guessing."),
        ],
        "callout": "most businesses run one ad and hope — testing is the smarter move",
    },
    # ── Mindset & business ──────────────────────────────────────────────────────
    {
        "title": "The Real Reason Most Service Business Owners Don't Run Ads",
        "layout": "problems",
        "slides": [
            ("FEAR OF FAILURE", "They've heard stories — a mate spent money and got nothing. So they write off the whole channel."),
            ("WRONG SETUP", "The mate who got nothing ran a boosted post with a stock photo. That's not a Meta ad."),
            ("DOING NOTHING", "Referrals dry up. No predictable lead source. One slow month from stress."),
        ],
        "callout": "ads are a skill — you learn it once and use it forever",
    },
    {
        "title": "What 'Consistent Leads' Actually Means for a Service Business",
        "layout": "steps",
        "slides": [
            ("PREDICTABLE REVENUE", "You know roughly what next month looks like. You can plan staff, equipment, capacity."),
            ("LESS DESPERATION", "You stop taking every job. You can be selective. Raise prices."),
            ("GROWTH BY CHOICE", "Scale when you want to. Hire when it makes sense. Not because you're scrambling."),
            ("REAL BUSINESS", "A well-run campaign delivers this — leads in, calendar full, stress out."),
        ],
        "callout": "most service businesses have never actually had consistent leads",
    },
    {
        "title": "Why Most Service Businesses Plateau at $10k/Month",
        "layout": "funnel",
        "slides": [
            ("THE CEILING", "Referrals max out. Word-of-mouth can't scale beyond a point."),
            ("ADD ADS", "New lead volume forces decisions — hire, specialise, raise prices, systemise."),
            ("BUILD SYSTEMS", "Follow-up, clear offer, capacity to handle the work. Not just the ads."),
            ("BREAK THROUGH", "The businesses that break $10k have a predictable lead source and a system to handle it."),
        ],
        "callout": "it's a systems problem — not a skills problem",
    },
    # ── Niche specifics ─────────────────────────────────────────────────────────
    {
        "title": "Meta Ads for Plumbers — What Works and What Doesn't",
        "layout": "problems",
        "slides": [
            ("GENERIC ADS FAIL", "'We fix all plumbing issues! Call now!' — too broad, instantly ignored."),
            ("URGENCY WORKS", "'Burst pipe? We respond within 60 minutes in [suburb]' — specific, urgent, local."),
            ("SEASONAL ANGLES", "'Hot water system going cold before winter?' — timely hooks convert every time."),
        ],
        "callout": "plumbing is competitive on Meta — the angle is everything",
    },
    {
        "title": "Meta Ads for Landscapers — The Angle That Always Works",
        "layout": "steps",
        "slides": [
            ("SHOOT THE JOB", "Take 3 photos before you pack up — wide shot, close-up, transformation shot."),
            ("SELL THE RESULT", "Don't talk about overgrown lawns. Talk about being 'ready to host again by the weekend.'"),
            ("TIME IT SEASONALLY", "Spring clean-ups, pre-summer prep, end-of-year tidy — match your ad to the calendar."),
            ("POST THE BEFORE/AFTER", "One photo per week. Consistent visual proof. That's the whole content strategy."),
        ],
        "callout": "landscaping is visual — that's your biggest advantage on Instagram",
    },
    {
        "title": "Meta Ads for Window Cleaners — Why This Niche Prints Money",
        "layout": "problems",
        "slides": [
            ("HIGH FREQUENCY", "Average job repeats every 3-6 months. LTV is real and predictable."),
            ("EASY VISUAL PROOF", "Before/after windows are instantly satisfying. High CTR by default."),
            ("LOW COMPETITION", "Most window cleaners aren't running Meta ads. You dominate by just showing up."),
        ],
        "callout": "window cleaning is one of the best niches for Meta ads — the math works",
    },
]


# ── API helpers ────────────────────────────────────────────────────────────────

def api_post(path, payload):
    r = requests.post(f'{API}{path}', headers=HEADERS, json=payload, timeout=30)
    if not r.ok:
        print(f"  API error {r.status_code} on {path}: {r.text[:300]}")
        r.raise_for_status()
    return r.json()


def add_circle(board_id, content, x, y, size, fill):
    """Circle shape with content centered inside."""
    return api_post(f'/boards/{board_id}/shapes', {
        'data': {'shape': 'circle', 'content': content},
        'style': {
            'fillColor': fill,
            'fontColor': WHITE,
            'borderColor': fill,
            'borderWidth': '2',
            'textAlign': 'center',
            'textAlignVertical': 'middle',
            'fontSize': '14',
            'fontWeight': 'bold',
            'fillOpacity': '1',
        },
        'position': {'x': x, 'y': y, 'origin': 'center'},
        'geometry': {'width': size, 'height': size},
    })


def add_rect(board_id, content, x, y, w, h, fill, text_color=WHITE, border_color=None, font_size='14', align='center'):
    return api_post(f'/boards/{board_id}/shapes', {
        'data': {'shape': 'rectangle', 'content': content},
        'style': {
            'fillColor': fill,
            'fontColor': text_color,
            'borderColor': border_color or fill,
            'borderWidth': '3',
            'textAlign': align,
            'textAlignVertical': 'middle',
            'fontSize': font_size,
            'fillOpacity': '1',
        },
        'position': {'x': x, 'y': y, 'origin': 'center'},
        'geometry': {'width': w, 'height': h},
    })


def add_text(board_id, content, x, y, w, font_size, color, bold=False):
    text = f'<strong>{content}</strong>' if bold else content
    return api_post(f'/boards/{board_id}/texts', {
        'data': {'content': text},
        'style': {'color': color, 'fontSize': str(font_size), 'textAlign': 'center'},
        'position': {'x': x, 'y': y, 'origin': 'center'},
        'geometry': {'width': w},
    })


def add_arrow(board_id, from_id, to_id, color=GRAY):
    try:
        api_post(f'/boards/{board_id}/connectors', {
            'startItem': {'id': from_id, 'snapTo': 'right'},
            'endItem':   {'id': to_id,   'snapTo': 'left'},
            'style': {
                'strokeColor': color,
                'strokeWidth': '2',
                'endStrokeCap': 'filled_triangle',
                'startStrokeCap': 'none',
                'strokeStyle': 'normal',
            },
        })
    except Exception as e:
        print(f"  Arrow skipped: {e}")


def board_header(board_id, title, total_w, y_offset=-120):
    add_text(board_id, title, x=total_w / 2, y=y_offset, w=total_w, font_size=28, color=DARK, bold=True)
    add_text(board_id, '@marcomarkets', x=total_w / 2, y=y_offset + 50, w=total_w, font_size=16, color=GRAY)


def board_callout(board_id, text, cx, y, w=900):
    add_rect(board_id, text, x=cx, y=y, w=w, h=80,
             fill=WHITE, text_color=DARK, border_color='#cbd5e1', font_size='15')


# ── Layout builders ────────────────────────────────────────────────────────────

def build_funnel(board_id, topic):
    """Decreasing circles connected horizontally — good for flows and funnels."""
    slides = topic['slides']
    n = len(slides)
    sizes = [300 - i * 28 for i in range(n)]  # e.g. 300, 272, 244, 216, 188
    gap = 50
    # Center x of each circle accounting for variable sizes
    xs = []
    cx = sizes[0] / 2
    for i, size in enumerate(sizes):
        if i == 0:
            cx = size / 2
        else:
            cx += sizes[i - 1] / 2 + gap + size / 2
        xs.append(cx)

    total_w = xs[-1] + sizes[-1] / 2
    board_header(board_id, topic['title'], total_w)

    y_circle = 300
    circle_ids = []
    for i, (label, sublabel) in enumerate(slides):
        color = FUNNEL_COLORS[i % len(FUNNEL_COLORS)]
        short = label[:22]
        shape = add_circle(board_id, short, x=xs[i], y=y_circle, size=sizes[i], fill=color)
        circle_ids.append(shape['id'])
        # Label below circle
        add_text(board_id, label, x=xs[i], y=y_circle + sizes[i] / 2 + 25,
                 w=max(sizes[i] + 40, 200), font_size=13, color=DARK, bold=True)
        add_text(board_id, sublabel, x=xs[i], y=y_circle + sizes[i] / 2 + 55,
                 w=max(sizes[i] + 60, 220), font_size=12, color=GRAY)

    for i in range(len(circle_ids) - 1):
        add_arrow(board_id, circle_ids[i], circle_ids[i + 1], color='#94a3b8')

    if topic.get('callout'):
        board_callout(board_id, topic['callout'], cx=total_w / 2, y=y_circle + sizes[0] / 2 + 140)

    print(f"  → funnel: {n} circles built")


def build_problems(board_id, topic):
    """Equal circles side by side, each a different color — good for problems/mistakes."""
    slides = topic['slides']
    n = len(slides)
    size = 240
    gap = 70
    spacing = size + gap
    total_w = n * size + (n - 1) * gap + 100

    board_header(board_id, topic['title'], total_w)

    y_circle = 280
    for i, (label, detail) in enumerate(slides):
        color = PROBLEM_COLORS[i % len(PROBLEM_COLORS)]
        x = 50 + size / 2 + i * spacing
        short = label[:20]
        add_circle(board_id, short, x=x, y=y_circle, size=size, fill=color)
        # Label below (colored to match circle)
        add_text(board_id, label, x=x, y=y_circle + size / 2 + 28,
                 w=size + 40, font_size=14, color=color, bold=True)
        # Explanation box below label
        add_rect(board_id, detail, x=x, y=y_circle + size / 2 + 120,
                 w=size + 30, h=110,
                 fill=WHITE, text_color=DARK, border_color=color, font_size='13', align='left')

    if topic.get('callout'):
        board_callout(board_id, topic['callout'], cx=total_w / 2, y=y_circle + size / 2 + 275)

    print(f"  → problems: {n} circles built")


def build_steps(board_id, topic):
    """Numbered circles same color, connected by arrows — good for how-tos and checklists."""
    slides = topic['slides']
    n = len(slides)
    size = 210
    gap = 60
    spacing = size + gap
    total_w = n * size + (n - 1) * gap + 100

    board_header(board_id, topic['title'], total_w)

    y_circle = 280
    circle_ids = []
    for i, (label, detail) in enumerate(slides):
        x = 50 + size / 2 + i * spacing
        num = f'0{i+1}' if i + 1 < 10 else str(i + 1)
        shape = add_circle(board_id, num, x=x, y=y_circle, size=size, fill=STEP_COLOR)
        circle_ids.append(shape['id'])
        add_text(board_id, label, x=x, y=y_circle + size / 2 + 28,
                 w=size + 30, font_size=13, color=DARK, bold=True)
        add_text(board_id, detail, x=x, y=y_circle + size / 2 + 60,
                 w=size + 40, font_size=12, color=GRAY)

    for i in range(len(circle_ids) - 1):
        add_arrow(board_id, circle_ids[i], circle_ids[i + 1], color='#94a3b8')

    if topic.get('callout'):
        board_callout(board_id, topic['callout'], cx=total_w / 2, y=y_circle + size / 2 + 130)

    print(f"  → steps: {n} circles built")


def build_comparison(board_id, topic):
    """Two large circles side by side — left=bad/before (red), right=good/after (green)."""
    slides = topic['slides']
    left_label, left_detail = slides[0]
    right_label, right_detail = slides[1]

    size = 280
    gap = 160  # space for VS label in center
    total_w = size * 2 + gap + 200

    board_header(board_id, topic['title'], total_w)

    y_circle = 270
    lx = 100 + size / 2
    rx = total_w - 100 - size / 2

    add_circle(board_id, left_label[:18], x=lx, y=y_circle, size=size, fill=COMP_LEFT)
    add_circle(board_id, right_label[:18], x=rx, y=y_circle, size=size, fill=COMP_RIGHT)

    # VS label in center
    add_text(board_id, 'VS', x=total_w / 2, y=y_circle,
             w=80, font_size=32, color='#94a3b8', bold=True)

    # Detail boxes below each circle
    add_rect(board_id, left_detail, x=lx, y=y_circle + size / 2 + 120,
             w=size + 80, h=130, fill=WHITE, text_color=DARK, border_color=COMP_LEFT,
             font_size='13', align='left')
    add_rect(board_id, right_detail, x=rx, y=y_circle + size / 2 + 120,
             w=size + 80, h=130, fill=WHITE, text_color=DARK, border_color=COMP_RIGHT,
             font_size='13', align='left')

    if topic.get('formula'):
        add_text(board_id, topic['formula'], x=total_w / 2, y=y_circle + size / 2 + 70,
                 w=500, font_size=15, color=DARK, bold=True)

    if topic.get('callout'):
        board_callout(board_id, topic['callout'], cx=total_w / 2, y=y_circle + size / 2 + 290)

    print(f"  → comparison: 2 circles built")


def build_case_study(board_id, topic):
    """Rising bar chart — good for weekly results and metric progressions."""
    slides = topic['slides']
    n = len(slides)
    bar_w = 200
    gap = 50
    spacing = bar_w + gap
    # Bar heights increase left to right
    min_h, max_h = 120, 380
    step = (max_h - min_h) / max(n - 1, 1)
    heights = [int(min_h + i * step) for i in range(n)]

    total_w = n * bar_w + (n - 1) * gap + 120
    ground_y = 520  # y of the bottom of the tallest bar

    board_header(board_id, topic['title'], total_w)

    for i, (label, detail) in enumerate(slides):
        color = CASE_COLORS[i % len(CASE_COLORS)]
        h = heights[i]
        x = 60 + bar_w / 2 + i * spacing
        bar_top_y = ground_y - h

        # The bar (rectangle)
        add_rect(board_id, '', x=x, y=bar_top_y + h / 2, w=bar_w, h=h,
                 fill=color, font_size='13')

        # Label inside bar (at top of bar if tall enough)
        if h > 80:
            add_text(board_id, label, x=x, y=bar_top_y + 30,
                     w=bar_w - 10, font_size=14, color=WHITE, bold=True)

        # Detail text below bar
        add_text(board_id, detail, x=x, y=ground_y + 30,
                 w=bar_w + 20, font_size=12, color=GRAY)

    if topic.get('callout'):
        board_callout(board_id, topic['callout'], cx=total_w / 2, y=ground_y + 110)

    print(f"  → case_study: {n} bars built")


LAYOUT_BUILDERS = {
    'funnel':      build_funnel,
    'problems':    build_problems,
    'steps':       build_steps,
    'comparison':  build_comparison,
    'case_study':  build_case_study,
}


def build_visual_board(board_id, topic):
    layout = topic.get('layout', 'steps')
    builder = LAYOUT_BUILDERS.get(layout, build_steps)
    builder(board_id, topic)


# ── Board management ───────────────────────────────────────────────────────────

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


def get_team_id():
    r = requests.get(f'{API}/orgs', headers=HEADERS, timeout=20)
    if r.ok:
        orgs = r.json().get('data', [])
        if orgs:
            org_id = orgs[0]['id']
            tr = requests.get(f'{API}/orgs/{org_id}/teams', headers=HEADERS, timeout=20)
            if tr.ok:
                teams = tr.json().get('data', [])
                if teams:
                    return teams[0]['id']
    return None


def create_board(title):
    payload = {'name': title, 'description': 'Weekly board — @marcomarkets'}
    team_id = get_team_id()
    if team_id:
        payload['teamId'] = team_id
    r = requests.post(f'{API}/boards', headers=HEADERS, json=payload, timeout=20)
    r.raise_for_status()
    return r.json()


def main():
    if not MIRO_TOKEN:
        print("No MIRO_ACCESS_TOKEN — skipping Miro board creation")
        return

    used_titles, existing_boards = load_used_topics()

    available = [t for t in CAROUSEL_TOPICS if t['title'] not in used_titles]
    if not available:
        print("All topics have been used. Add new topics to CAROUSEL_TOPICS to continue.")
        return
    if len(available) < 3:
        print(f"Only {len(available)} topic(s) left — using what's available.")

    this_week = available[:3]
    new_boards = list(existing_boards)
    newly_used = list(used_titles)

    for topic in this_week:
        print(f"Creating board: {topic['title']} [{topic.get('layout', 'steps')}]")
        try:
            board = create_board(topic['title'])
            board_id = board['id']
            view_link = board.get('viewLink', f"https://miro.com/app/board/{board_id}/")
            build_visual_board(board_id, topic)
            new_boards.append({
                'title': topic['title'],
                'board_id': board_id,
                'url': view_link,
                'layout': topic.get('layout', 'steps'),
                'created': datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ'),
            })
            newly_used.append(topic['title'])
            print(f"  → {view_link}")
        except Exception as e:
            print(f"  Error creating board: {e}")

    save_boards(new_boards, newly_used)
    print(f"Done. {len(this_week)} boards created.")


if __name__ == '__main__':
    main()
