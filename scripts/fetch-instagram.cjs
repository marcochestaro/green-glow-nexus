// Fetches Instagram profile data directly via Instagram's internal API
const https = require('https');
const http = require('http');
const fs = require('fs');
const path = require('path');

const ME = 'marcomarkets';
const COMPETITORS = ['adsbydann','joshhills','adsharley','badmarketing','markbuilds','isaiahhgarciaa'];
const ALL_HANDLES = [ME, ...COMPETITORS];

function get(url, redirects = 0) {
  return new Promise((resolve, reject) => {
    if (redirects > 5) return reject(new Error('Too many redirects'));
    const lib = url.startsWith('https') ? https : http;
    const req = lib.request(url, {
      method: 'GET',
      headers: {
        'x-ig-app-id': '936619743392459',
        'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Mobile/15E148 Safari/604.1',
        'Accept': '*/*',
        'Accept-Language': 'en-US,en;q=0.9',
        'Referer': 'https://www.instagram.com/',
      },
    }, res => {
      if (res.statusCode >= 300 && res.statusCode < 400 && res.headers.location) {
        res.resume();
        return resolve(get(res.headers.location, redirects + 1));
      }
      let data = '';
      res.on('data', c => data += c);
      res.on('end', () => resolve({ status: res.statusCode, body: data }));
    });
    req.on('error', reject);
    req.end();
  });
}

function fetchProfile(username) {
  return get(`https://i.instagram.com/api/v1/users/web_profile_info/?username=${username}`)
    .then(({ status, body }) => {
      console.log(`${username}: HTTP ${status}, body length ${body.length}, preview: ${body.slice(0, 80)}`);
      const json = JSON.parse(body);
      const user = json.data && json.data.user;
      if (!user) return null;
      return {
        username: user.username,
        followers: user.edge_followed_by && user.edge_followed_by.count,
        totalPosts: user.edge_owner_to_timeline_media && user.edge_owner_to_timeline_media.count,
        posts: (user.edge_owner_to_timeline_media && user.edge_owner_to_timeline_media.edges || []).map(e => {
          const n = e.node;
          return {
            id: n.id || '',
            shortCode: n.shortcode || '',
            url: `https://www.instagram.com/p/${n.shortcode}/`,
            type: n.__typename === 'GraphVideo' ? 'Video' : n.__typename === 'GraphSidecar' ? 'Sidecar' : 'Image',
            caption: ((n.edge_media_to_caption && n.edge_media_to_caption.edges[0] && n.edge_media_to_caption.edges[0].node.text) || '').slice(0, 80),
            timestamp: n.taken_at_timestamp ? new Date(n.taken_at_timestamp * 1000).toISOString() : '',
            views: n.video_view_count || 0,
            likes: (n.edge_liked_by && n.edge_liked_by.count) || 0,
            comments: (n.edge_media_to_comment && n.edge_media_to_comment.count) || 0,
            engagement: ((n.edge_liked_by && n.edge_liked_by.count) || 0) + ((n.edge_media_to_comment && n.edge_media_to_comment.count) || 0),
          };
        }),
      };
    })
    .catch(e => { console.log(`${username}: error - ${e.message}`); return null; });
}

function sleep(ms) { return new Promise(r => setTimeout(r, ms)); }

async function main() {
  const outPath = path.join(__dirname, '..', 'dashboard', 'data.json');
  let existing = {};
  try { existing = JSON.parse(fs.readFileSync(outPath, 'utf8')); } catch(e) {}

  console.log('Fetching profiles:', ALL_HANDLES.join(', '));

  const results = {};
  for (const handle of ALL_HANDLES) {
    results[handle] = await fetchProfile(handle);
    console.log(`${handle}: followers=${results[handle] ? results[handle].followers : 'FAILED'}`);
    await sleep(2000);
  }

  const meProfile = results[ME];
  const topPosts = meProfile ? meProfile.posts.slice(0, 6) : (existing.me && existing.me.topPosts || []);

  const competitors = COMPETITORS.map(handle => {
    const p = results[handle];
    const prev = existing.competitors && existing.competitors.find(c => c.handle === handle);
    return {
      handle,
      followers: (p && p.followers != null) ? p.followers : (prev ? prev.followers : null),
    };
  });

  const output = {
    pulledAt: new Date().toISOString(),
    me: {
      handle: ME,
      followers: (meProfile && meProfile.followers != null) ? meProfile.followers : (existing.me ? existing.me.followers : null),
      totalPosts: (meProfile && meProfile.totalPosts != null) ? meProfile.totalPosts : (existing.me ? existing.me.totalPosts : 0),
      totalViews: topPosts.reduce((s, p) => s + (p.views || 0), 0),
      avgEngagement: topPosts.length
        ? Math.round(topPosts.reduce((s, p) => s + (p.engagement || 0), 0) / topPosts.length)
        : (existing.me ? existing.me.avgEngagement : 0),
      topPosts,
    },
    competitors,
  };

  fs.mkdirSync(path.dirname(outPath), { recursive: true });
  fs.writeFileSync(outPath, JSON.stringify(output, null, 2));
  console.log('Done. My followers:', output.me.followers, '| posts:', output.me.totalPosts);
  console.log('Competitors:', competitors.map(c => `${c.handle}:${c.followers}`).join(', '));
}

main().catch(e => { console.error(e); process.exit(1); });
