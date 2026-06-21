// Fetches Instagram data via Apify and writes data.json to dashboard/
const https = require('https');
const fs = require('fs');
const path = require('path');

const TOKEN = process.env.APIFY_TOKEN;
if (!TOKEN) { console.error('Missing APIFY_TOKEN'); process.exit(1); }

const ME = 'marcomarkets';
const COMPETITORS = ['adsbydann','joshhills','adsharley','badmarketing','markbuilds','isaiahhgarciaa'];
const ALL_HANDLES = [ME, ...COMPETITORS];

function apifyRequest(method, urlPath, body) {
  return new Promise((resolve, reject) => {
    const url = new URL('https://api.apify.com' + urlPath);
    url.searchParams.set('token', TOKEN);
    const opts = {
      hostname: url.hostname,
      path: url.pathname + url.search,
      method,
      headers: { 'Content-Type': 'application/json' },
    };
    const req = https.request(opts, res => {
      let data = '';
      res.on('data', c => data += c);
      res.on('end', () => {
        try { resolve(JSON.parse(data)); }
        catch(e) { reject(e); }
      });
    });
    req.on('error', reject);
    if (body) req.write(JSON.stringify(body));
    req.end();
  });
}

function sleep(ms) { return new Promise(r => setTimeout(r, ms)); }

async function runScraper(handles) {
  console.log('Starting Apify run for:', handles.join(', '));
  const run = await apifyRequest('POST', '/v2/acts/apify~instagram-scraper/runs', {
    directUrls: handles.map(h => `https://www.instagram.com/${h}/`),
    resultsType: 'details',
    resultsLimit: 10,
  });
  const runId = run.data && run.data.id;
  if (!runId) throw new Error('Failed to start run: ' + JSON.stringify(run));
  console.log('Run started:', runId);

  // Poll until finished
  for (let i = 0; i < 30; i++) {
    await sleep(10000);
    const status = await apifyRequest('GET', `/v2/acts/apify~instagram-scraper/runs/${runId}`);
    const s = status.data && status.data.status;
    console.log('Status:', s);
    if (s === 'SUCCEEDED') break;
    if (s === 'FAILED' || s === 'ABORTED') throw new Error('Run failed: ' + s);
  }

  // Get results
  const dataset = run.data.defaultDatasetId;
  const items = await apifyRequest('GET', `/v2/datasets/${dataset}/items?limit=200`);
  return items.items || items;
}

async function main() {
  const items = await runScraper(ALL_HANDLES);

  console.log('Total items returned:', items.length);
  const errorItems = items.filter(i => i.error);
  const goodItems = items.filter(i => !i.error);
  if (errorItems.length > 0) console.log('Error items:', errorItems.length, '— first error:', errorItems[0].error, errorItems[0].errorDescription);
  if (goodItems.length > 0) {
    const first = goodItems[0];
    console.log('Good item keys:', Object.keys(first).slice(0, 25).join(', '));
    console.log('Good item username:', first.username, '| followersCount:', first.followersCount, '| ownerId:', first.ownerId);
  }
  const meData = goodItems.find(i => (i.username || i.ownerUsername || '').toLowerCase() === ME.toLowerCase()) || {};
  const topPosts = (meData.latestPosts || meData.posts || meData.topPosts || meData.recentPosts || [])
    .slice(0, 6)
    .map(p => ({
      id: p.id || '',
      url: p.url || p.link || `https://www.instagram.com/p/${p.shortCode}/`,
      type: p.type === 'Video' ? 'Video' : p.type === 'Sidecar' ? 'Sidecar' : 'Image',
      caption: (p.caption || '').slice(0, 80),
      timestamp: p.timestamp || p.takenAt || '',
      views: p.videoViewCount || p.videoPlayCount || 0,
      likes: p.likesCount || p.likes || 0,
      comments: p.commentsCount || p.comments || 0,
      engagement: (p.likesCount || 0) + (p.commentsCount || 0),
    }));

  const competitors = COMPETITORS.map(handle => {
    const c = goodItems.find(i => (i.username || '').toLowerCase() === handle.toLowerCase()) || {};
    return {
      handle,
      followers: c.followersCount || c.followedByCount || c.followers || null,
    };
  });

  const output = {
    pulledAt: new Date().toISOString(),
    me: {
      handle: ME,
      followers: meData.followersCount || meData.followedByCount || meData.followers || null,
      totalPosts: meData.postsCount || meData.mediaCount || meData.igTvVideoCount || topPosts.length,
      totalViews: topPosts.reduce((s, p) => s + p.views, 0),
      avgEngagement: topPosts.length
        ? Math.round(topPosts.reduce((s, p) => s + p.engagement, 0) / topPosts.length)
        : 0,
      topPosts,
    },
    competitors,
  };

  const outPath = path.join(__dirname, '..', 'dashboard', 'data.json');
  fs.writeFileSync(outPath, JSON.stringify(output, null, 2));
  console.log('Written to', outPath);
  console.log('Followers:', output.me.followers);
  console.log('Top posts:', topPosts.length);
}

main().catch(e => { console.error(e); process.exit(1); });
