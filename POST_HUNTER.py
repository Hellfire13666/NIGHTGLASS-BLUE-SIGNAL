#!/usr/bin/env python3
"""NIGHTGLASS Post Hunter: authorized Page Graph API, offline imports, local-only reports."""
import csv
import io
import json
import os
import re
import sys
import urllib.parse
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

MAX_LIMIT=500
FIELDS='id,message,created_time,permalink_url'
PAGE_RE=re.compile(r'^[0-9]{1,30}$')
VERSION_RE=re.compile(r'^v[0-9]{1,2}\.[0-9]{1,2}$')

def normalize(row):
    """Normalize ordinary export aliases to the Graph-style report schema.

    Prefer fields already supplied by the Meta API; only use aliases when
    the canonical field is empty. No URLs are requested by this function.
    """
    if not isinstance(row, dict):
        return None
    aliases = {
        'id': ('id', 'post_id'),
        'created_time': ('created_time', 'date', 'timestamp', 'published_at', 'published_time'),
        'message': ('message', 'text', 'body', 'content'),
        'permalink_url': ('permalink_url', 'url', 'link', 'permalink'),
    }
    normalized = {}
    for field, keys in aliases.items():
        value = ''
        for key in keys:
            candidate = row.get(key)
            if candidate is not None and candidate != '':
                # Keep zero numeric IDs/timestamps; avoid serializing complex objects.
                if isinstance(candidate, (str, int, float)) and not isinstance(candidate, bool):
                    value = str(candidate)
                    if value.strip():
                        break
        normalized[field] = value
    return normalized

def api_page(page_id,token,after=None,version='v24.0',fetch=None):
    if not PAGE_RE.fullmatch(page_id): raise ValueError('Use the numeric ID of a Page you are authorized to access.')
    if not VERSION_RE.fullmatch(version): raise ValueError('Invalid Graph API version')
    params={'fields':FIELDS,'limit':'100'}
    if after: params['after']=after
    url='https://graph.facebook.com/'+version+'/'+page_id+'/posts?'+urllib.parse.urlencode(params)
    if fetch is None:
        def fetch(u):
            with urllib.request.urlopen(urllib.request.Request(u,headers={'User-Agent':'NIGHTGLASS-PostHunter/1.0', 'Authorization':'Bearer '+token}), timeout=20) as r:
                return json.load(r)
    try: result=fetch(url)
    except Exception as exc:
        # API failures may embed query strings or tokens: never print the exception.
        raise RuntimeError('Page API request failed. Check Page permissions, network, and API status.') from None
    if not isinstance(result,dict): raise RuntimeError('Unexpected Page API response.')
    if 'error' in result: raise RuntimeError('Meta API rejected the request; check permissions or API limits.')
    return result

def collect(page_id,token,limit=100,version='v24.0',fetch=None):
    if not isinstance(limit,int) or not (1<=limit<=MAX_LIMIT): raise ValueError('Limit must be 1–500')
    if not token: raise ValueError('NIGHTGLASS_PAGE_TOKEN is not set')
    found=[]; seen=set(); cursor=None; cursors=set(); status='source ended'
    for _ in range(100):
        try: result=api_page(page_id,token,cursor,version,fetch)
        except RuntimeError:
            if not found: raise
            status='PARTIAL: Page API stopped before completion';break
        items=result.get('data')
        if not isinstance(items,list): status='PARTIAL: unexpected Page API data';break
        for item in items:
            post=normalize(item)
            if post is None or not post['id'] or post['id'] in seen:continue
            seen.add(post['id']);found.append(post)
            if len(found)>=limit:status='requested limit reached';break
        if len(found)>=limit:break
        if not items:status='source ended';break
        after=((result.get('paging') or {}).get('cursors') or {}).get('after')
        if not isinstance(after,str) or not after or after in cursors:
            status='source ended (no new cursor)';break
        cursors.add(after);cursor=after
    else:status='PARTIAL: pagination safety limit reached'
    return found,status

def read_import(path):
    p=Path(os.path.expandvars(path)).expanduser()
    if p.is_symlink() or not p.is_file() or p.stat().st_size>20_000_000:raise ValueError('Import must be a regular local file under 20 MB')
    if p.suffix.lower()=='.csv':
        with p.open(encoding='utf-8-sig',newline='') as f: rows=list(csv.DictReader(f))
    elif p.suffix.lower() in ('.json','.jsonl'):
        with p.open(encoding='utf-8-sig') as f:
            if p.suffix.lower()=='.jsonl': rows=[json.loads(line) for line in f if line.strip()]
            else:
                data=json.load(f);rows=data.get('data',data.get('posts',[])) if isinstance(data,dict) else data
    else:raise ValueError('Only CSV, JSON, JSONL imports are supported')
    if not isinstance(rows,list):raise ValueError('Expected list of post objects')
    return [x for r in rows if (x:=normalize(r)) is not None]

def display(posts,source,status):
    print('\nNIGHTGLASS // POST HUNTER 100+ | '+source)
    for i,p in enumerate(posts,1):
        print(f'[{i:03}] {p["created_time"] or "DATE NOT PROVIDED"} | ID {p["id"] or "NOT PROVIDED"}')
        print(' TEXT:',p['message'] or '[NO TEXT FIELD RETURNED]')
        print(' LINK:',p['permalink_url'] or '[NO PERMALINK RETURNED]')
    print(f'[TOTAL] posts={len(posts)} | {status} | source={source}')

def save(posts,source,status):
    dest=Path.home()/'Documents'/'NIGHTGLASS-VAULT'/'post-hunter-runs'
    dest.mkdir(parents=True,exist_ok=True,mode=0o700)
    os.chmod(dest,0o700)
    run='posts-'+datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S%fZ')
    paths={kind:dest/(run+'.'+kind) for kind in ('txt','json','csv')}
    text=io.StringIO()
    text.write(f'NIGHTGLASS POST HUNTER | {source} | {status} | count={len(posts)}\n')
    for i,p in enumerate(posts,1):
        text.write(f'[{i:03}] {p["created_time"]} | {p["id"]}\n TEXT: {p["message"]}\n LINK: {p["permalink_url"]}\n')
    buf=io.StringIO();writer=csv.DictWriter(buf,fieldnames=['id','created_time','message','permalink_url']);writer.writeheader();writer.writerows(posts)
    contents={'txt':text.getvalue(),'json':json.dumps({'source':source,'status':status,'posts':posts},ensure_ascii=False,indent=2),'csv':buf.getvalue()}
    for kind,p in paths.items():
        fd=os.open(p,os.O_WRONLY|os.O_CREAT|os.O_EXCL,0o600)
        with os.fdopen(fd,'w',encoding='utf-8') as f:f.write(contents[kind])
    for p in paths.values(): print('[SAVED]',p.name)
    print('[VAULT] Private post-hunter-runs | local only')
    return paths

def interactive(original):
    while True:
        print('\nBLUE SIGNAL // POST HUNTER 100+')
        print('[7] LINK FUSION | META FULL / META ALL LINKS / custom public URL')
        print('[1] Authorized Meta Page API | live posts (permission required)')
        print('[2] Import permitted CSV / JSON / JSONL | offline')
        print('[3] Original Public Post Fusion')
        print('[4] Smart Link Fusion | paste or import public URLs')
        print('[5] Public Post Discovery | one public HTML page')
        print('[6] Public Evidence Inspector | one public URL')
        print('[0] Return to NIGHTGLASS')
        try: choice=input('POST HUNTER > ').strip()
        except (EOFError,KeyboardInterrupt):return 0
        if choice=='0':return 0
        if choice=='3':return original()
        if choice=='7':
            from NIGHTGLASS_LINK_FUSION_FAVORITES import interactive as link_favorites
            link_favorites()
            continue
        if choice in ('4','5','6'):
            try:
                if choice=='4':
                    from NIGHTGLASS_SMART_LINK_FUSION import main as link_main
                    print('[MODE] OFFLINE LINK IMPORT | Type DONE when finished')
                    # Some terminal environments redirect standard input; use own prompt
                    # and pass a private temporary text file only when needed.
                    from pathlib import Path as _Path
                    import tempfile as _tempfile
                    import sys as _sys
                    rows=[]
                    while True:
                        line=input('LINK > ').strip()
                        if line.upper()=='DONE':break
                        if line:rows.append(line)
                    from NIGHTGLASS_SMART_LINK_FUSION import extract as _extract
                    from NIGHTGLASS_SMART_LINK_FUSION import save as _save_links
                    links,rejected=_extract('\n'.join(rows),50)
                    print('[MODE] USER-SUPPLIED LINKS | NOT VERIFIED LIVE POSTS')
                    for idx,item in enumerate(links,1):
                        print(f"[{idx:03d}] {item['type']}: {item['url']}")
                    print(f'[FOUND] {len(links)} | [REJECTED] {rejected} | [TARGET] 50')
                    if links and input('Save private link report? [y/N]: ').lower().strip()=='y':
                        print('[SAVED]',_save_links(links).name)
                elif choice=='5':
                    from NIGHTGLASS_PUBLIC_DISCOVERY import main as discovery_main
                    url=input('PUBLIC FACEBOOK PAGE URL (Enter cancels) > ').strip()
                    if url:
                        flags=['--url',url,'--target','50']
                        if input('Save privately? [y/N]: ').lower().strip()=='y':flags.append('--save')
                        discovery_main(flags)
                else:
                    from EVIDENCE_INSPECTOR import main as evidence_main
                    url=input('PUBLIC FACEBOOK LINK (Enter cancels) > ').strip()
                    if url:
                        flags=['--url',url]
                        if input('Save privately? [y/N]: ').lower().strip()=='y':flags.append('--save')
                        evidence_main(flags)
            except (ValueError,OSError,EOFError,KeyboardInterrupt) as exc:
                print('[STOP] Tool exited safely:',type(exc).__name__)
            continue
        try:
            if choice=='1':
                token=os.environ.get('NIGHTGLASS_PAGE_TOKEN','')
                if not token:
                    print('[STOP] Set NIGHTGLASS_PAGE_TOKEN privately for a Page you manage or can access. No request made.');continue
                page_id=input('Authorized numeric Page ID (Enter cancels): ').strip()
                if not page_id:continue
                amount=input('Max posts [100; max 500]: ').strip()
                limit=int(amount) if amount else 100
                if input('Request authorized Page posts? Type YES: ').strip()!='YES':continue
                posts,status=collect(page_id,token,limit)
                source='AUTHORIZED PAGE API'
            elif choice=='2':
                print('[TIP] Paste the whole path BEFORE pressing Enter. Example: ~/Downloads/NIGHTGLASS-POST-HUNTER-DEMO-100.json')
                path=input('FILE PATH > ').strip().strip('\"').strip("'")
                if not path:
                    print('[CANCEL] Empty path. Choose [2] again or use the one-paste --import option.');continue
                posts=read_import(path);status='imported records, not live Facebook';source='LOCAL IMPORT'
            else:print('Choose 0–6.');continue
            display(posts,source,status)
            if input('Save to private vault? [y/N]: ').strip().lower()=='y':save(posts,source,status)
        except (ValueError,OSError,json.JSONDecodeError,UnicodeError,RuntimeError) as exc:
            print('[STOP]',str(exc))

def main(argv=None):
    import argparse
    parser=argparse.ArgumentParser(description='NIGHTGLASS Post Hunter: offline imports and authorized Page API only')
    parser.add_argument('--import-file',metavar='PATH',help='Read and print posts from permitted local JSON/CSV/JSONL; avoids the interactive prompt')
    parser.add_argument('--save',action='store_true',help='Save results to the private vault (only with --import-file)')
    args=parser.parse_args(argv)
    if not args.import_file:
        if args.save:parser.error('--save requires --import-file')
        return interactive(lambda:0)
    try:
        posts=read_import(args.import_file)
        display(posts,'LOCAL IMPORT','imported records, not live Facebook')
        if args.save:save(posts,'LOCAL IMPORT','imported records, not live Facebook')
    except (ValueError,OSError,json.JSONDecodeError,UnicodeError,RuntimeError) as exc:
        print('[STOP]',str(exc));return 2
    return 0

if __name__=='__main__':raise SystemExit(main())
