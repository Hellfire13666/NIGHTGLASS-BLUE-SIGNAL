#!/usr/bin/env python3
"""Import Facebook links manually supplied by the user. No network or login."""
import argparse
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urlsplit, urlunsplit, parse_qsl, urlencode
import json
import os
import re
import sys

ALLOWED = {'facebook.com', 'www.facebook.com', 'm.facebook.com', 'mbasic.facebook.com', 'web.facebook.com', 'fb.watch'}
URL_RE = re.compile(r'https?://[^\s<>"\']+', re.I)
POST_RE = re.compile(r'^/[^/]+/posts/[^/]+/?$', re.I)
REEL_RE = re.compile(r'^/reel/[^/]+/?$', re.I)
VIDEO_RE = re.compile(r'^/(?:[^/]+/videos/[^/]+|watch)/?$', re.I)
KEEP_QUERY = {'story_fbid', 'fbid', 'id', 'v'}
PROFILE_RE = re.compile(r'^/profile\.php/?$', re.I)
SHARE_POST_RE = re.compile(r'^/share/p/[A-Za-z0-9_-]+/?$', re.I)
SHARE_VIDEO_RE = re.compile(r'^/share/v/[A-Za-z0-9_-]+/?$', re.I)
SEARCH_RE = re.compile(r'^/search/(?:top|posts|people|pages|videos|photos|groups)/?$', re.I)


def parse_link(raw):
    raw = raw.strip().strip('()[]{}<>,;"\'')
    try:
        p = urlsplit(raw)
        host = (p.hostname or '').lower()
        if p.scheme != 'https' or host not in ALLOWED or p.username or p.password or p.port not in (None, 443):
            return None
        # Use one canonical host for normal Facebook URLs. fb.watch remains separate.
        canonical_host = 'fb.watch' if host == 'fb.watch' else 'www.facebook.com'
        path = re.sub(r'/+', '/', p.path)
        parameters = parse_qsl(p.query,keep_blank_values=False)
        qs = dict(parameters)
        if canonical_host == 'fb.watch':
            kind = 'SHORT LINK'
            allowed = set()
        elif POST_RE.fullmatch(path):
            kind = 'POST'
            allowed = set()
        elif SHARE_POST_RE.fullmatch(path):
            kind = 'SHARED POST'
            allowed = set()
        elif SHARE_VIDEO_RE.fullmatch(path):
            kind = 'VIDEO'
            allowed = set()
        elif REEL_RE.fullmatch(path):
            kind = 'REEL'
            allowed = set()
        elif VIDEO_RE.fullmatch(path) or path == '/watch/':
            kind = 'VIDEO'
            allowed = {'v'}
        elif path.lower() in ('/permalink.php','/story.php','/photo.php'):
            kind = 'POST' if any(k in qs for k in ('story_fbid','fbid')) else 'OTHER PUBLIC LINK'
            allowed = {'story_fbid','fbid','id'}
        elif PROFILE_RE.fullmatch(path):
            kind = 'PROFILE'
            allowed = {'id'}
        elif SEARCH_RE.fullmatch(path):
            kind = 'SEARCH'
            allowed = {'q'}
        elif path in ('/', ''):
            kind = 'OTHER PUBLIC LINK'
            allowed = set()
        elif re.fullmatch(r'/[^/]+/?',path):
            kind = 'PROFILE'
            allowed = set()
        else:
            kind = 'OTHER PUBLIC LINK'
            allowed = set()
        # q is retained solely for the Facebook search route. Drop tracking,
        # login/session parameters, comment_id and unknown query strings.
        clean_q = [(k,v) for k,v in parameters if k in allowed]
        query = urlencode(sorted(set(clean_q)))
        # Avoid counting a comment-specific deep link as another post.
        canonical = urlunsplit(('https',canonical_host,path.rstrip('/') or '/',query,''))
        return {'type':kind,'url':canonical}
    except ValueError:
        return None

def extract(text,limit):
    links=[];seen=set();rejected=0
    for raw in URL_RE.findall(text):
        item=parse_link(raw)
        if item is None:
            rejected+=1
            continue
        if item['url'] not in seen:
            seen.add(item['url']);links.append(item)
        if len(links) >= limit:
            break
    return links,rejected

def save(links):
    directory=Path.home()/'Documents'/'NIGHTGLASS-VAULT'/'manual-link-imports'
    directory.mkdir(parents=True,exist_ok=True,mode=0o700)
    os.chmod(directory,0o700)
    filename='links-'+datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S%fZ')+'.json'
    dest=directory/filename
    fd=os.open(dest,os.O_CREAT|os.O_EXCL|os.O_WRONLY,0o600)
    with os.fdopen(fd,'w',encoding='utf-8') as fp:
        json.dump({'source':'MANUALLY SUPPLIED LINKS / NOT VERIFIED LIVE POSTS','links':links},fp,indent=2)
    return dest

def main(argv=None):
    parser=argparse.ArgumentParser(description='NIGHTGLASS link importer: paste URLs or read a text file; strictly offline')
    parser.add_argument('--file',type=Path,help='Text file containing URLs, one or more per line')
    parser.add_argument('--target',type=int,default=50)
    parser.add_argument('--save',action='store_true',help='Save private JSON in NIGHTGLASS Vault')
    args=parser.parse_args(argv)
    if not 1 <= args.target <= 500:
        parser.error('--target must be between 1 and 500')
    try:
        if args.file:
            source=args.file.expanduser()
            if source.is_symlink() or not source.is_file():
                print('[STOP] Link text file missing or symlink');return 2
            if source.stat().st_size > 2*1024*1024:
                print('[STOP] File exceeds 2MB limit');return 2
            content=source.read_text(encoding='utf-8',errors='replace')
        elif not sys.stdin.isatty():
            content=sys.stdin.read(2*1024*1024+1)
            if len(content)>2*1024*1024:
                print('[STOP] Input exceeds 2MB limit');return 2
        else:
            print('NIGHTGLASS // SMART LINK FUSION v2.6.9')
            print('Paste one or more PUBLIC Facebook URLs. Type DONE on its own line to finish.')
            buffer=[]
            while True:
                try:line=input('LINK > ')
                except EOFError:break
                if line.strip().upper()=='DONE':break
                buffer.append(line)
            content='\n'.join(buffer)
        links,rejected=extract(content,args.target)
        print('\nNIGHTGLASS // SMART LINK FUSION v2.6.9')
        print('[MODE] OFFLINE | USER-SUPPLIED URLS | NO FACEBOOK REQUESTS')
        for i,item in enumerate(links,1):
            print(f"[{i:03d}] {item['type']} (UNVERIFIED): {item['url']}")
        print(f'[TARGET] {args.target} | [FOUND] {len(links)} distinct accepted URLs | [REJECTED] {rejected}')
        counts={k:sum(x['type']==k for x in links) for k in ('POST','SHARED POST','REEL','VIDEO','PROFILE','SEARCH','SHORT LINK','OTHER PUBLIC LINK')}
        print('[TYPES] '+' | '.join(f'{k}={v}' for k,v in counts.items()))
        print('[NOTE] These are supplied URL strings, not verified accessible post contents')
        if args.save:
            print('[SAVED] Private report:',save(links).name)
        return 0
    except OSError as exc:
        print('[STOP] File operation failed:',type(exc).__name__);return 2

if __name__=='__main__':raise SystemExit(main())
