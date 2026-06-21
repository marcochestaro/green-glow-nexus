require('dotenv').config({ path: require('path').join(__dirname, '../.env') });
const axios = require('axios');
const fs = require('fs');
const path = require('path');

const TOKEN = process.env.APIFY_TOKEN;
const BASE = 'https://api.apify.com/v2';

const MY_HANDLE = 'marcomarkets';
const COMPETITORS = ['adsbydann', 'joshhills', 'adsharley', 'badmarketing', 'markbuilds', 'isaiahhgarciaa'];

async function runScraper(usernames, resultsLimit = 50) {
  const run = await axios.post(
    `${BASE}/acts/apify~instagram-scraper/runs?token=${TOKEN}&waitForFinish=300`,
    {
      usernames,
      resultsType: 'posts',
      resultsLimit,
      addParentData: false,
    }
  );

  const datasetId = run.data.data.defaultDatasetId;
  const items = await axios.get(
    `${BASE}/datasets/${datasetId}/items?token=${TOKEN}&limit=2000`
  );
  return items.data;
}

async function getProfile(username) {
  const run = await axios.post(
    `${BASE}/acts/apify~instagram-scraper/runs?token=${TOKEN}&waitForFinish=120`,
    {
      usernames: [username],
      resultsType: 'details',
      resultsLimit: 1,
    }
  );
  const datasetId = run.data.data.defaultDatasetId;
  const items = await axios.get(
    `${BASE}/datasets/${datasetId}/items?token=${TOKEN}&limit=1`
  );
  return items.data[0] || null;
}

function rankPosts(posts, username) {
  return posts
    .filter(p => p.ownerUsername?.toLowerCase() === username.toLowerCase())
    .map(p => ({
      id: p.id,
      url: p.url,
      type: p.type,
      caption: (p.caption || '').slice(0, 120),
      timestamp: p.timestamp,
      views: p.videoViewCount || p.videoPlayCount || 0,
      likes: p.likesCount || 0,
      comments: p.commentsCount || 0,
      engagement: (p.likesCount || 0) + (p.commentsCount || 0),
    }))
    .sort((a, b) => b.views - a.views || b.engagement - a.engagement);
}

async function main() {
  console.log('Pulling your posts (@marcomarkets) — this takes ~2 min...');
  let myPosts = [];
  try {
    const raw = await runScraper([MY_HANDLE], 200);
    myPosts = rankPosts(raw, MY_HANDLE);
    console.log(`  Got ${myPosts.length} of your posts.`);
  } catch (e) {
    console.error('  Failed to pull your posts:', e.message);
  }

  console.log('Pulling profile/follower count...');
  let followers = null;
  try {
    const profile = await getProfile(MY_HANDLE);
    followers = profile?.followersCount ?? null;
    console.log(`  Followers: ${followers?.toLocaleString() ?? 'unavailable'}`);
  } catch (e) {
    console.error('  Failed to pull profile:', e.message);
  }

  console.log('Pulling competitor posts...');
  let competitorPosts = [];
  try {
    const raw = await runScraper(COMPETITORS, 30);
    competitorPosts = COMPETITORS.flatMap(handle => rankPosts(raw, handle).slice(0, 10));
    console.log(`  Got ${competitorPosts.length} competitor posts.`);
  } catch (e) {
    console.error('  Failed to pull competitor posts:', e.message);
  }

  const totalViews = myPosts.reduce((s, p) => s + p.views, 0);
  const totalEngagement = myPosts.reduce((s, p) => s + p.engagement, 0);
  const avgEngagement = myPosts.length ? (totalEngagement / myPosts.length).toFixed(1) : 0;

  const output = {
    pulledAt: new Date().toISOString(),
    me: {
      handle: MY_HANDLE,
      followers,
      totalPosts: myPosts.length,
      totalViews,
      avgEngagement,
      topPosts: myPosts.slice(0, 20),
      allPosts: myPosts,
    },
    competitors: competitorPosts,
  };

  const outPath = path.join(__dirname, '../dashboard/data.json');
  fs.writeFileSync(outPath, JSON.stringify(output, null, 2));
  console.log(`\nSaved to dashboard/data.json`);

  console.log('\n=== YOUR TOP 5 POSTS ===');
  myPosts.slice(0, 5).forEach((p, i) => {
    console.log(`\n#${i + 1}`);
    console.log(`  Views:      ${p.views.toLocaleString()}`);
    console.log(`  Likes:      ${p.likes.toLocaleString()}`);
    console.log(`  Comments:   ${p.comments}`);
    console.log(`  Type:       ${p.type}`);
    console.log(`  Date:       ${p.timestamp?.slice(0, 10)}`);
    console.log(`  Caption:    ${p.caption || '(none)'}`);
    console.log(`  URL:        ${p.url}`);
  });

  console.log(`\n=== SUMMARY ===`);
  console.log(`Followers:    ${followers?.toLocaleString() ?? 'unavailable'}`);
  console.log(`Total posts:  ${myPosts.length}`);
  console.log(`Total views:  ${totalViews.toLocaleString()}`);
  console.log(`Avg eng/post: ${avgEngagement}`);
}

main().catch(console.error);
