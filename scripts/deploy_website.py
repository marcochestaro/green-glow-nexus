# Uploads the site as a Pages _worker.bundle with each file as a raw data module, so nothing is decoded at startup.
# The usual asset upload needs a short-lived upload token in the Authorization header, which this session's proxy overwrites.
import json, mimetypes, os, sys, subprocess, tempfile, uuid
# Usage: python3 scripts/deploy_website.py  (needs a Cloudflare API token with Pages: Edit, injected by the session proxy)
here = os.path.dirname(os.path.abspath(__file__))
root = sys.argv[1] if len(sys.argv) > 1 else os.path.join(here, '..', 'website')
acct, proj = '01f2d28a0d1bb92a492fce8a283e047f', 'scalable'
mimetypes.add_type('image/webp', '.webp')
parts, imports, table = [], [], []
for i, (dp, f) in enumerate((dp, f) for dp, _, fs in os.walk(root) for f in sorted(fs)):
    p = os.path.join(dp, f); rel = '/' + os.path.relpath(p, root)
    mod = f'f{i}.bin'
    parts.append((mod, 'application/octet-stream', open(p, 'rb').read()))
    imports.append(f'import m{i} from "./{mod}";')
    table.append(f'{json.dumps(rel)}:[{json.dumps(mimetypes.guess_type(p)[0] or "application/octet-stream")},m{i}]')
js = '\n'.join(imports) + '\nconst F={' + ','.join(table) + '''};
export default{async fetch(req){
  const u=new URL(req.url);
  if(u.hostname.startsWith('www.')){u.hostname=u.hostname.slice(4);return Response.redirect(u.toString(),301);}
  let p=decodeURIComponent(u.pathname);if(p.endsWith('/'))p+='index.html';
  const f=F[p]||F[p+'.html']||F[p+'/index.html'];
  if(!f)return new Response('Not found',{status:404,headers:{'content-type':'text/plain'}});
  const html=f[0]==='text/html';
  return new Response(f[1],{headers:{'content-type':f[0]+(html?'; charset=utf-8':''),'cache-control':html?'public, max-age=0, must-revalidate':'public, max-age=86400'}});
}};
'''
parts.insert(0, ('_worker.js', 'application/javascript+module', js.encode()))
b = '----scalable' + uuid.uuid4().hex
body = b''
body += f'--{b}\r\nContent-Disposition: form-data; name="metadata"\r\n\r\n{json.dumps({"main_module": "_worker.js"})}\r\n'.encode()
for name, ct, data in parts:
    body += f'--{b}\r\nContent-Disposition: form-data; name="{name}"; filename="{name}"\r\nContent-Type: {ct}\r\n\r\n'.encode() + data + b'\r\n'
body += f'--{b}--\r\n'.encode()
w = tempfile.NamedTemporaryFile('wb', suffix='.bundle', delete=False); w.write(body); w.close()
print('bundle bytes', len(body))
out = subprocess.run(['curl', '-s', '-X', 'POST', f'https://api.cloudflare.com/client/v4/accounts/{acct}/pages/projects/{proj}/deployments',
    '--form-string', 'manifest={}', '--form-string', 'branch=main', '-F', f'_worker.bundle=@{w.name};filename=_worker.bundle'],
    capture_output=True, text=True).stdout
d = json.loads(out)
print(d['success'], d.get('errors'), d['result'] and d['result']['url'])
