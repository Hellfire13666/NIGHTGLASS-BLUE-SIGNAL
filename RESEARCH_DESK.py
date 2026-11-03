"""Local Facebook URL research registry; never fetches or visits links."""
from pathlib import Path
from urllib.parse import urlsplit, urlunsplit, parse_qs, urlencode
from datetime import datetime, timezone
import json, csv, hashlib, re

ALLOWED_HOSTS={'facebook.com','www.facebook.com','m.facebook.com','web.facebook.com','mbasic.facebook.com','fb.watch','www.fb.watch'}
SAFE_QUERY={'story_fbid','id','fbid','comment_id'}
MAX_URL=2048

def normalize(url):
    url=url.strip()
    if len(url)>MAX_URL or not url or any(ord(c)<32 for c in url):
        raise ValueError('Invalid URL length or control characters')
    parsed=urlsplit(url)
    if parsed.scheme.lower()!='https' or parsed.hostname is None or parsed.hostname.lower() not in ALLOWED_HOSTS:
        raise ValueError('Only HTTPS Facebook or fb.watch links are supported')
    if parsed.username or parsed.password or parsed.port is not None:
        raise ValueError('Credentials and custom ports not supported')
    path=parsed.path
    if not path or path=='/':raise ValueError('Use a Page, post, video or other specific public-content URL')
    if any(x in path.lower() for x in ['/login','/checkpoint','/settings','/messages','/groups/']):
        raise ValueError('Private or authenticated Facebook routes are not accepted')
    if len(path)>1000:raise ValueError('URL path too long')
    params=parse_qs(parsed.query,keep_blank_values=False)
    keep={k: v[0][:128] for k,v in params.items() if k in SAFE_QUERY and v and re.fullmatch(r'[a-zA-Z0-9_.-]{1,128}',v[0])}
    clean=urlunsplit(('https',parsed.hostname.lower(),path,urlencode(keep),'')).rstrip('/')
    return clean

def classify(url):
    p=urlsplit(url); path=p.path.lower()
    if p.hostname in ('fb.watch','www.fb.watch'):return 'short video link (not fetched)'
    if '/posts/' in path or '/permalink/' in path or '/story.php' in path:return 'possible post link'
    if '/videos/' in path or '/reel/' in path or '/watch/' in path:return 'possible video/reel link'
    if '/photos/' in path or '/photo.php' in path:return 'possible photo link'
    return 'Page/profile or other link (unverified)'

def add_entry(root,url,note=''):
    clean=normalize(url)
    if len(note)>400:raise ValueError('Note too long')
    root=Path(root)
    if root.is_symlink():raise ValueError('Cannot use a symlink registry directory')
    root.mkdir(parents=True,exist_ok=True,mode=0o700)
    registry=root/'sources.json'
    if registry.is_symlink():raise ValueError('Cannot use symlink registry')
    entries=[]
    if registry.exists():
        raw=json.loads(registry.read_text(encoding='utf-8'))
        if not isinstance(raw,list):raise ValueError('Invalid registry')
        entries=raw
    fingerprint=hashlib.sha256(clean.encode()).hexdigest()[:16]
    for entry in entries:
        if entry.get('id')==fingerprint:
            return entry,False
    entry={'id':fingerprint,'url':clean,'kind':classify(clean),'added_utc':datetime.now(timezone.utc).isoformat(timespec='seconds'), 'origin':'USER-SUPPLIED LINK', 'verification':'NOT FETCHED / UNVERIFIED', 'note':note}
    entries.append(entry)
    temp=root/'sources.json.tmp'
    if temp.is_symlink():raise ValueError('Unsafe temporary registry')
    with temp.open('w',encoding='utf-8') as f:json.dump(entries,f,indent=2,ensure_ascii=False)
    temp.chmod(0o600)
    temp.replace(registry)
    return entry,True

def list_entries(root):
    p=Path(root)/'sources.json'
    if not p.is_file() or p.is_symlink():return []
    data=json.loads(p.read_text(encoding='utf-8'))
    return data if isinstance(data,list) else []

def interactive(root):
    while True:
        print('\n◆ SOURCE RESEARCH DESK // LOCAL INDEX · NOT LIVE FACEBOOK')
        print('[1] Add a public-content URL  [2] List sources  [3] Export CSV  [0] Return')
        try:choice=input('RESEARCH ❯ ').strip()
        except (KeyboardInterrupt,EOFError):print();return 0
        if choice=='0':return 0
        if choice=='1':
            try:
                url=input('Public Facebook HTTPS URL: ').strip()
                note=input('Optional neutral research note (max 400 chars): ').strip()
                item,created=add_entry(root,url,note)
                print('SAVED' if created else 'ALREADY INDEXED',item['id'],item['kind'])
                print('STATUS:',item['verification'])
            except (ValueError,OSError,json.JSONDecodeError) as e:print('Not saved:',e)
        elif choice=='2':
            for i,item in enumerate(list_entries(root),1):
                print(f"[{i:03}] {item['id']} · {item['kind']} · {item['verification']}")
                print('    URL:',item['url'])
            if not list_entries(root):print('No sources indexed yet.')
        elif choice=='3':
            try:
                rows=list_entries(root)
                if not rows:print('No sources to export.');continue
                output=Path(root)/'sources.csv'
                with output.open('w',newline='',encoding='utf-8') as f:
                    w=csv.DictWriter(f,fieldnames=['id','url','kind','added_utc','origin','verification','note'])
                    w.writeheader();w.writerows(rows)
                output.chmod(0o600)
                print('Private CSV created: ResearchDesk/sources.csv')
            except (OSError,ValueError) as e:print('Export failed:',e)
        else:print('Choose 1, 2, 3 or 0.')
