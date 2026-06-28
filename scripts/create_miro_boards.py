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

# 42 unique topics — 14 weeks of 3 boards each before anything could theoretically repeat.
# When the pool is fully exhausted the script flags it but does NOT reset — new topics must be added.
CAROUSEL_TOPICS = [
    # ── Budget & math ───────────────────────────────────────────────────────────
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
        "title": "What $500/Month in Meta Ads Actually Buys You",
        "slides": [
            ("$500/month sounds like a lot. Here's what it actually produces.", "For a local service business running it right."),
            ("$500 ÷ 30 days = $16.67/day", "That's enough to run one solid lead generation campaign in a local radius."),
            ("At $25 CPL (realistic after week 2)", "You get roughly 20 leads per month from $500 in spend."),
            ("If you close 30% of those leads", "That's 6 new jobs. At $300 average job value = $1,800 revenue from $500 spend."),
            ("3.6x return. Every month. Predictably.", "DM me ADS to make this work for your trade."),
        ]
    },
    {
        "title": "Why Your Ad Spend Feels Wasted (And How to Fix It)",
        "slides": [
            ("You spent $200 on ads. Got nothing. Here's what actually went wrong.", "It's rarely what you think."),
            ("Problem 1: You judged it too early", "Meta needs 50 conversion events to exit the learning phase. That takes time and budget."),
            ("Problem 2: You changed it mid-run", "Every edit resets the learning phase. Patience is the strategy."),
            ("Problem 3: Wrong campaign objective", "Traffic campaigns get clicks. Lead campaigns get leads. They're not the same."),
            ("The fix: set it up right once, then leave it alone for 14 days.", "DM me ADS to get the setup right."),
        ]
    },
    # ── Ad creative & copy ──────────────────────────────────────────────────────
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
        "title": "How to Write an Ad Headline That Actually Converts",
        "slides": [
            ("Most service business ad headlines are invisible.", "Here's the formula that makes them stop."),
            ("The formula: Pain + Timeframe + Outcome", "You don't need to be clever. You need to be specific."),
            ("Bad: 'Professional Window Cleaning Services'", "Zero reason to click. Sounds like every other tradie."),
            ("Good: 'Get your windows spotless before the weekend — we come to you'", "Specific. Local. Time-anchored. Outcome clear."),
            ("Rewrite yours with this formula.", "DM me ADS if you want me to look at your current headline."),
        ]
    },
    {
        "title": "5 Hook Formulas That Work for Every Service Business Ad",
        "slides": [
            ("The first 3 seconds decide everything.", "Here are 5 hooks that work — steal them."),
            ("Hook 1: The number hook", "'3 mistakes that are killing your ad results' — specificity creates curiosity."),
            ("Hook 2: The call-out hook", "'If you're a plumber in Brisbane running ads, watch this' — instant relevance."),
            ("Hook 3: The result hook", "'How this landscaper got 14 leads in a week for $320' — proof before explanation."),
            ("Hook 4: The against the grain hook", "'Stop targeting homeowners — here's what actually works'"),
            ("Hook 5: The pain hook", "'You ran ads. Nobody called. Here's the exact reason why.'"),
        ]
    },
    {
        "title": "What 'Professional and Reliable' Is Actually Costing You",
        "slides": [
            ("'Professional and reliable' is in every tradie ad.", "That's exactly why it doesn't work."),
            ("When everyone says the same thing, no one stands out.", "Your audience becomes blind to it."),
            ("Replace claims with proof.", "Not 'reliable' — 'responded within 2 hours, job done same day.'"),
            ("Replace adjectives with outcomes.", "Not 'professional' — 'left the site cleaner than we found it, no callbacks.'"),
            ("Specific always beats generic.", "DM me ADS to rewrite your ad copy with this approach."),
        ]
    },
    {
        "title": "How to Use a Real Job Photo to 3x Your Click Rate",
        "slides": [
            ("Stock photos kill click rates.", "Here's why real job photos outperform them every time."),
            ("Real photos prove you actually do the work.", "Stock photos feel like marketing. Real photos feel like evidence."),
            ("The best performing ad photos:", "Before/after. Mid-job. The finished result with you in it."),
            ("What to shoot on your next job", "One wide shot. One close-up. One with you or your team visible."),
            ("Real beats polished every time in local service ads.", "DM me ADS to talk through your creative."),
        ]
    },
    # ── Mistakes & fixes ────────────────────────────────────────────────────────
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
        "title": "Why Your Ad Works for 3 Days Then Dies",
        "slides": [
            ("Your ad runs great for 3 days then goes cold.", "Here's exactly why — and how to fix it."),
            ("Cause 1: Ad fatigue in a small audience", "You've shown it to everyone in your radius who'll click it. The pool is tapped."),
            ("Cause 2: You're in a micro-niche audience", "Narrow targeting exhausts fast. Broad audiences have more runway."),
            ("Cause 3: You only have one creative", "Rotate 2–3 different images or videos. Fresh creative restarts performance."),
            ("Fix: broaden audience + add a second creative.", "DM me ADS to diagnose which one it is."),
        ]
    },
    {
        "title": "5 Things to Check in Ads Manager Every Week",
        "slides": [
            ("Most service businesses set up their ad and never look at it.", "Here's what to actually check — and how often."),
            ("1. Cost per lead (CPL)", "Should be trending down week over week after day 14. If it's going up, your creative is fatiguing."),
            ("2. Frequency", "If frequency hits 3+, your audience has seen it 3 times. Time to refresh the creative."),
            ("3. Click-through rate (CTR)", "Under 1%? Your hook is the problem. 2%+ means your creative is working."),
            ("4. Lead quality (not just volume)", "Are the leads booking? If not, your targeting or offer needs adjusting."),
            ("5. Amount spent vs leads", "Simple division. Know your CPL every single week."),
        ]
    },
    # ── Platform & strategy ─────────────────────────────────────────────────────
    {
        "title": "Meta vs Google — The Honest Answer for Service Businesses",
        "slides": [
            ("Everyone asks: Meta or Google?", "Here's the honest breakdown for local service businesses."),
            ("Google Ads: High intent, high cost", "People are searching right now. But CPL can hit $80–$150+ for competitive trades."),
            ("Meta Ads: Lower cost, broader reach", "CPL of $20–$50 is realistic. You interrupt people — so your creative has to be good."),
            ("The real answer?", "Start with Meta at $25/day. Get leads. Prove the model. Scale to Google later."),
            ("For most tradies just starting out?", "Meta wins. DM me ADS to talk through your situation."),
        ]
    },
    {
        "title": "How the Meta Algorithm Decides Who Sees Your Ad",
        "slides": [
            ("Meta doesn't show your ad to everyone.", "It shows it to who it thinks will take action. Here's how it decides."),
            ("It starts with your campaign objective", "Lead gen objective = Meta finds people likely to fill out a form. Traffic = likely to click. Choose carefully."),
            ("Then it looks at your creative", "High CTR signals relevance. Meta rewards relevant ads with cheaper reach."),
            ("Then it looks at your audience signals", "Your location radius, any interests you set, and past converters all shape who it targets."),
            ("The better your creative, the cheaper your leads.", "DM me ADS to improve your creative performance."),
        ]
    },
    {
        "title": "Why I Only Run Meta Ads for Service Businesses",
        "slides": [
            ("I don't run Google Ads. I don't run TikTok Ads.", "Here's exactly why I'm 100% focused on Meta for service businesses."),
            ("Meta has the most accurate local targeting", "You can hit a 20km radius around any suburb. Google can't match the geo-precision."),
            ("The CPL is the most controllable", "At $25/day you get real data fast. Google often needs $50–100/day before it optimises."),
            ("Service businesses have visual proof", "Before/after photos. Job site footage. That works perfectly on Instagram and Facebook feeds."),
            ("The audience is there.", "Every homeowner, landlord, and property manager is on Meta. Your buyers are already there."),
        ]
    },
    # ── Targeting & audiences ───────────────────────────────────────────────────
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
        "title": "Lookalike Audiences — When to Use Them and When Not To",
        "slides": [
            ("Lookalike audiences sound powerful.", "But most service businesses use them at the wrong time. Here's the truth."),
            ("What a lookalike does", "Meta finds people similar to your existing customers or leads. Powerful — but only with enough data."),
            ("The problem: you need 100+ source events minimum", "If you have fewer leads or customers than that, your lookalike will be inaccurate."),
            ("When to use it", "After 3–6 months of lead gen campaigns. Upload your booked client list. Build from there."),
            ("For now? Broad + location beats lookalike every time.", "DM me ADS to talk through your audience strategy."),
        ]
    },
    # ── Lead forms & conversion ─────────────────────────────────────────────────
    {
        "title": "How to Set Up a Lead Form That Actually Converts",
        "slides": [
            ("Your Meta lead form is losing you bookings.", "Here's how to fix it in 10 minutes."),
            ("Keep it to 3 fields max", "Name, phone, suburb. Every extra field drops your conversion rate by 10–20%."),
            ("Write a custom thank-you message", "Don't use the default. Tell them exactly what happens next: 'I'll call you within 2 hours.'"),
            ("Add one qualifying question", "One question only. 'Are you looking to book within the next 2 weeks?' Filters time-wasters."),
            ("Follow up within 1 hour", "Speed to lead is everything. After 1 hour, your close rate drops by 80%."),
        ]
    },
    {
        "title": "Why Speed to Lead Is Worth More Than Your Ad Creative",
        "slides": [
            ("You can have the best ad in the world.", "But if you call your leads 24 hours later, you're losing half your bookings."),
            ("Study: leads contacted within 5 minutes", "Are 9x more likely to convert than leads contacted after 30 minutes."),
            ("After 1 hour, close rate drops 80%.", "The lead has moved on. Called someone else. Forgotten they even filled in the form."),
            ("The fix: set up an instant SMS or email auto-reply", "Let them know you'll call within 2 hours. Then actually call within 2 hours."),
            ("Your follow-up speed is your competitive advantage.", "DM me ADS — I'll show you the exact follow-up system I give clients."),
        ]
    },
    {
        "title": "What to Say When a Lead Calls From Your Meta Ad",
        "slides": [
            ("You got a lead. They called.", "Most service businesses fumble this moment. Here's exactly what to say."),
            ("Don't open with your price", "Price before value kills the sale. Get context first."),
            ("Ask: 'What's going on for you?'", "Let them explain the problem. You're solving it — not just quoting it."),
            ("Then confirm: 'When do you need this done by?'", "Urgency tells you how hot the lead is. Act accordingly."),
            ("Then give a specific next step.", "'I can come out Thursday at 10am to take a look — does that work?' Close the loop."),
        ]
    },
    # ── Mindset & positioning ───────────────────────────────────────────────────
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
        "title": "Why Service Businesses Are Built for Meta Ads",
        "slides": [
            ("E-commerce brands fight for attention on Meta.", "Service businesses have an unfair advantage. Here's why."),
            ("You serve a specific location", "Your ad only needs to reach people in your city or suburb. Tiny pool. Cheap reach."),
            ("You have a visual product", "Before/after photos. Job site footage. Real proof of work. Instagram was built for this."),
            ("Your sale is high-value and recurring", "One new customer from ads could be worth $500–$5,000+ over their lifetime."),
            ("The ROI math works better for you than for any product brand.", "DM me ADS to start the math for your specific trade."),
        ]
    },
    {
        "title": "The Gap Between Tradies and Marketing Agencies",
        "slides": [
            ("Most marketing agencies charge $1,500–$3,000/month.", "For a service business doing $10k/month, that's 15–30% of revenue. Brutal."),
            ("And most agencies don't understand trade businesses.", "They run the same generic ads they'd run for a dentist or a gym."),
            ("The gap is real.", "Tradies need someone who speaks their language and knows their numbers."),
            ("What you actually need:", "A simple lead gen campaign. A follow-up system. A clear offer. That's it."),
            ("You don't need an agency. You need a system.", "DM me ADS — I'll show you what that looks like for your trade."),
        ]
    },
    # ── Client results ──────────────────────────────────────────────────────────
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
        "title": "How a Plumber Cut His Cost Per Lead From $120 to $38",
        "slides": [
            ("A plumber came to me with a broken Meta ad setup.", "He was getting leads but at $120 each. That's not a business — that's a bleed."),
            ("The diagnosis: wrong campaign objective", "He was running a Traffic campaign. Meta was sending clicks, not leads."),
            ("Fix 1: Switch to Lead Generation objective", "Immediately Meta started targeting people who fill out forms. CPL dropped to $71."),
            ("Fix 2: Simplify the lead form to 3 fields", "Name, phone, postcode. Removed 4 extra questions. CPL dropped to $38."),
            ("Same budget. Same audience. Better setup.", "DM me ADS to audit your current setup."),
        ]
    },
    {
        "title": "Car Detailer. $25/Day. 30 Days. Real Numbers.",
        "slides": [
            ("Mobile car detailer. First time running Meta ads.", "Here's exactly what happened when we turned it on."),
            ("Week 1", "5 leads at $35 CPL. 2 booked. Revenue: $380. Spend: $175. Early signal is good."),
            ("Week 2", "9 leads at $28 CPL. 4 booked. Revenue: $760. Spend: $175. CPL dropping."),
            ("Week 3–4", "14 leads at $22 CPL. 7 booked. Revenue: $1,330. Spend: $350. Dialled in."),
            ("Month 1 total: $700 spent. $2,470 revenue. 3.5x ROAS.", "DM me ADS if you want this for your detail business."),
        ]
    },
    {
        "title": "Landscaper: $0 to Fully Booked in 6 Weeks",
        "slides": [
            ("Landscaper. Never run ads before. Relied entirely on referrals.", "Here's what happened when we switched that."),
            ("Week 1–2: Building the baseline", "Testing 2 creatives — a job site photo and a before/after. The before/after won by 40%."),
            ("Week 3: First booked jobs from ads", "CPL at $41. 3 jobs booked. Covers the full month of ad spend."),
            ("Week 4–6: Fully booked", "Waiting list started forming. Raised his prices. Started referring overflow work to others."),
            ("Same skills. Same area. Just visible now.", "DM me ADS to turn on visibility for your trade."),
        ]
    },
    # ── Content & Instagram growth ──────────────────────────────────────────────
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
        "title": "Why Posting Every Day on Instagram Actually Works for Getting Clients",
        "slides": [
            ("Most tradies think Instagram is for influencers.", "Here's why daily posting is actually your best free lead source."),
            ("Every post is a trust touchpoint", "A potential client might see 10 of your posts before they ever DM you. That's 10 reasons to trust you."),
            ("Instagram rewards consistency with reach", "Post daily for 30 days and your account's baseline reach increases. The algorithm rewards volume."),
            ("Your content is your ad", "When someone sees your post and then your ad, the conversion cost drops. Warm traffic converts cheaper."),
            ("Post daily. Keep it simple. Show the work.", "DM me ADS — I'll tell you what to post this week."),
        ]
    },
    {
        "title": "The 3-Second Rule — Why Most Reels Fail Immediately",
        "slides": [
            ("If you don't hook them in 3 seconds, they're gone.", "Here's why most Reels fail before they even begin."),
            ("The algorithm watches completion rate", "If people scroll past in 2 seconds, Meta stops pushing your Reel. Dead before it started."),
            ("The most common mistake: slow intro", "'Hey guys, welcome back, today I want to talk about...' — already scrolled past."),
            ("What works: start mid-sentence", "Act like they've already been watching for 10 seconds. Drop them into the middle of something."),
            ("Open with the most interesting thing you have to say.", "Not a warm-up. Not an intro. The thing."),
        ]
    },
    {
        "title": "5 Instagram Post Ideas for Any Service Business This Week",
        "slides": [
            ("No idea what to post?", "Here are 5 content types that always perform for service businesses."),
            ("1. Before/after", "The most reliable post format in any trade. One photo. Instant proof."),
            ("2. Common mistake in your industry", "'The #1 mistake homeowners make before calling a plumber' — positions you as the expert."),
            ("3. Your process in 60 seconds", "Show them what actually happens when they hire you. Demystify the job."),
            ("4. A price myth", "'What does a full car detail actually cost? Here's the breakdown.' Transparent = trustworthy."),
            ("5. A client result with a number", "'This took 45 minutes and saved the client $800 in repairs.' Specific = believable."),
        ]
    },
    # ── Offer & positioning ─────────────────────────────────────────────────────
    {
        "title": "How to Write an Offer That Makes People Want to Call",
        "slides": [
            ("Most service business offers are invisible.", "Here's how to write one that actually makes people act."),
            ("The anatomy of a strong offer:", "Specific outcome + timeframe + risk reversal."),
            ("Weak offer: 'Free quote on all jobs'", "Everyone offers this. It means nothing. It creates no urgency."),
            ("Strong offer: 'Book this week and we'll have your gutters cleared same-day — or it's free'", "Specific. Urgent. Risk reversed. That's memorable."),
            ("You don't need a discount. You need a reason to act now.", "DM me ADS to write the offer for your trade."),
        ]
    },
    {
        "title": "The Difference Between a Good Ad and a Great Ad",
        "slides": [
            ("Good ads get clicks.", "Great ads get bookings. Here's the difference."),
            ("Good ad: describes the service", "Professional window cleaning. Fast. Reliable. Call us today."),
            ("Great ad: describes the transformation", "'Your windows will be spotless in 90 minutes. No streaks. We clean up after ourselves. Book online.'"),
            ("Good ad: speaks to everyone", "Broad language. No specific person addressed."),
            ("Great ad: speaks to one person", "'If you're a homeowner in [suburb] who wants...' — they feel like you wrote it for them."),
        ]
    },
    {
        "title": "Why 'Get a Free Quote' Is the Weakest CTA You Can Use",
        "slides": [
            ("Every tradie ad ends with 'get a free quote'.", "Here's why it's killing your conversion rate."),
            ("Free quotes are table stakes", "Everyone offers them. It gives the lead zero reason to choose you over the next guy."),
            ("Better CTAs tell them what happens next", "'Book your spot' — implies limited availability. 'Get your price in 60 seconds' — implies speed."),
            ("The best CTAs include a benefit", "'Get a free same-day quote' or 'See if we service your suburb' both beat generic."),
            ("Make your CTA feel like the first step of something good.", "DM me ADS if you want me to rewrite yours."),
        ]
    },
    # ── Scaling & systems ───────────────────────────────────────────────────────
    {
        "title": "When to Scale Your Meta Ad Budget (And When Not To)",
        "slides": [
            ("Most businesses scale too fast or not at all.", "Here's the exact signal to look for before increasing budget."),
            ("The rule: only scale on a profitable CPL", "If you're not profitable at $25/day, spending $100/day just loses you money faster."),
            ("The signal to scale: consistent results over 14 days", "Same CPL week over week. Leads converting to jobs. Then consider scaling."),
            ("How to scale: 20% budget increases only", "Don't double your budget overnight. Meta re-enters learning phase. 20% bumps preserve optimisation."),
            ("Scale when it's working. Fix it when it's not.", "DM me ADS to know which stage you're at."),
        ]
    },
    {
        "title": "How to Run Meta Ads in a Slow Season Without Wasting Money",
        "slides": [
            ("Slow season doesn't mean stop ads.", "It means run them smarter. Here's how."),
            ("Drop budget but don't turn it off", "Turning off resets the learning phase. Drop to $10–15/day minimum to keep the algorithm warm."),
            ("Shift objective to brand awareness", "Build your audience during slow season. Retarget them when demand returns."),
            ("Run engagement ads on your best performing posts", "Cheap. Builds social proof. Keeps your page active without burning lead gen budget."),
            ("The businesses that run through slow season", "Own market share when demand picks up. DM me ADS to set up a slow-season strategy."),
        ]
    },
    {
        "title": "How to Test 2 Ads Without Wasting Your Budget",
        "slides": [
            ("Most service businesses run one ad and hope it works.", "Testing 2 is the smarter move — here's how to do it without doubling your spend."),
            ("Run them in the same ad set", "Same audience. Same budget. Two different creatives. Let Meta split traffic between them."),
            ("What to test first: the creative (image or video)", "Don't test audience, budget, and creative at once. One variable at a time."),
            ("When to call a winner: after 50+ impressions each", "Not after 2 days. Give Meta time to find the right people for each creative."),
            ("Kill the loser. Scale the winner.", "Simple. Repeatable. DM me ADS to set this up."),
        ]
    },
    # ── Mindset & business ──────────────────────────────────────────────────────
    {
        "title": "The Real Reason Most Tradies Don't Run Ads",
        "slides": [
            ("It's not budget. It's not time.", "Here's the real reason most tradies never run ads — and why it's costing them."),
            ("Fear of it not working", "They've heard stories. A mate spent $500 and got nothing. So they write off the whole channel."),
            ("Wrong setup = wrong result", "The mate who got nothing ran a boosted post with no offer and a stock photo. That's not a Meta ad."),
            ("The real risk is doing nothing", "Referrals dry up. You have no predictable lead source. You're always one slow month away from stress."),
            ("Ads are a skill. Like tiling. Like quoting.", "You learn it once and use it forever. DM me ADS to start."),
        ]
    },
    {
        "title": "What 'Consistent Leads' Actually Means for a Service Business",
        "slides": [
            ("Everyone says they want consistent leads.", "But most service businesses have never actually had them. Here's what it looks like."),
            ("Consistent leads = predictable revenue", "You know roughly what next month looks like. You can plan staff, equipment, capacity."),
            ("Consistent leads = less desperation", "You stop taking every job that calls. You can be selective. Raise prices."),
            ("Consistent leads = growth by choice", "You scale when you want to. Hire when it makes sense. Not because you're scrambling."),
            ("A $25/day ad campaign done right delivers this.", "DM me ADS — I'll show you what it takes for your specific trade."),
        ]
    },
    {
        "title": "Why Most Service Businesses Plateau at $10k/Month",
        "slides": [
            ("There's a ceiling most tradies hit and can't break through.", "Here's why it happens and what breaks you through it."),
            ("The ceiling is usually a lead source problem", "You're at max capacity for word-of-mouth. Referrals can't scale beyond a point."),
            ("Adding ads breaks the ceiling", "New lead volume forces decisions: hire, specialise, raise prices, systemise."),
            ("But ads alone aren't the answer", "You need a follow-up system, a clear offer, and capacity to handle more work."),
            ("The $10k ceiling is a systems problem, not a skill problem.", "DM me ADS to map out what breaking through looks like for your business."),
        ]
    },
    # ── Niche specifics ─────────────────────────────────────────────────────────
    {
        "title": "Meta Ads for Plumbers — What Works and What Doesn't",
        "slides": [
            ("Plumbing is one of the most competitive local service niches on Meta.", "Here's what actually works."),
            ("What doesn't work: generic plumbing ads", "'We fix all plumbing issues! Call now!' — ignored. Too broad."),
            ("What works: urgency-based creative", "'Burst pipe? We respond within 60 minutes in [suburb]' — specific, urgent, local."),
            ("What works: seasonal angles", "'Hot water system going cold before summer? Get it sorted now.' Timely hooks convert."),
            ("What works: before/after with job story", "'$150 repair that saved this homeowner $3,000 in water damage' — proof + outcome."),
        ]
    },
    {
        "title": "Meta Ads for Landscapers — The Angle That Always Works",
        "slides": [
            ("Landscaping is visual.", "That's your biggest advantage on Instagram. Here's how to use it."),
            ("Your best ad is your last finished job", "Take 3 photos before you pack up. Wide shot, close-up, transformation shot."),
            ("The angle that converts: aspiration not desperation", "Don't talk about overgrown lawns. Talk about the result — 'ready to host again by the weekend.'"),
            ("Seasonal timing is everything", "Spring clean-ups, pre-summer prep, end-of-year tidy. Match your ad to the calendar."),
            ("One before/after per week on Instagram", "Consistent visible proof. That's the content strategy. DM me ADS to pair it with paid."),
        ]
    },
    {
        "title": "Meta Ads for Window Cleaners — Why This Niche Prints Money",
        "slides": [
            ("Window cleaning is one of the best niches for Meta ads.", "Here's exactly why — and how to maximise it."),
            ("Low ticket, high frequency", "Average job: $150–$300. Most clients rebook every 3–6 months. LTV is real."),
            ("Visual proof is easy", "Before/after windows are instantly satisfying. High CTR creative almost by default."),
            ("Tight local radius works perfectly", "You serve a suburb or 20km radius. Meta's geo-targeting was built for this."),
            ("Low competition from other window cleaners on Meta", "Most aren't running ads. You dominate by just showing up consistently."),
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
    payload = {
        "name": title,
        "description": "Weekly carousel — @marcomarkets",
    }
    team_id = get_team_id()
    if team_id:
        payload["teamId"] = team_id
    r = requests.post(f'{API}/boards', headers=HEADERS, json=payload, timeout=20)
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

    # Pick topics not yet used — never repeats, never resets
    available = [t for t in CAROUSEL_TOPICS if t['title'] not in used_titles]
    if not available:
        print("All carousel topics have been used. Add new topics to CAROUSEL_TOPICS to continue.")
        return
    if len(available) < 3:
        print(f"Only {len(available)} topic(s) left in pool — using what's available.")

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
            if hasattr(e, 'response') and e.response is not None:
                print(f"  Response body: {e.response.text}")

    save_boards(new_boards, newly_used)
    print(f"Done. {len(this_week)} boards created.")


if __name__ == '__main__':
    main()
