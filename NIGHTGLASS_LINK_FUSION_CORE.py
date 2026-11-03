#!/usr/bin/env python3
"""NIGHTGLASS internal link discovery module. Python standard library only."""
import argparse
from collections import Counter
from html.parser import HTMLParser
import ipaddress
import re
import sys
import urllib.error
import urllib.parse
import urllib.request

ALLOWED = {'facebook.com','www.facebook.com','m.facebook.com','mbasic.facebook.com','web.facebook.com','fb.watch'}
LIMIT = 1024 * 1024
ANSI = {'blue':'\033[94m','pink':'\033[95m','green':'\033[92m','yellow':'\033[93m','red':'\033[91m','white':'\033[97m','dim':'\033[90m','reset':'\033[0m','cyan':'\033[96m'}

def safe_fb_url(url):
    try:
        p = urllib.parse.urlsplit(url)
        host = (p.hostname or '').lower().rstrip('.')
        if (p.scheme != 'https' or host not in ALLOWED or p.username or p.password or p.port not in (None,443)):
            return False
        ipaddress.ip_address(host)  # if literal IP, reject (not among allowed anyway)
        return False
    except ValueError:
        return bool(host in ALLOWED and p.scheme == 'https' and not p.username and not p.password)

def clean_url(url):
    p=urllib.parse.urlsplit(url)
    return urllib.parse.urlunsplit((p.scheme,p.netloc,p.path,p.query,''))

def kind(url):
    host=(urllib.parse.urlsplit(url).hostname or '').lower()
    if host in ALLOWED: return 'FACEBOOK'
    if host == 'static.xx.fbcdn.net' or host in {'scontent.xx.fbcdn.net'} or host.endswith('.fna.fbcdn.net') or host.endswith('.fbcdn.net'): return 'ASSET'
    if re.search(r'\.(?:jpg|jpeg|png|gif|webp|svg|css|js|mp4|ico)(?:\?|$)',url,re.I): return 'ASSET'
    return 'EXTERNAL'

def interest(url):
    """Conservative URL categorization; a link hint is not post content."""
    p=urllib.parse.urlsplit(url)
    host=(p.hostname or '').lower()
    path=p.path.lower()
    if host in ALLOWED:
        if re.search(r'/(?:posts|videos|reel|reels|photos|permalink)/',path) or path.startswith('/story.php') or path.startswith('/watch/'):
            return 'POST-LINK'
        return 'PAGE-LINK'
    if kind(url)=='ASSET':
        if re.search(r'\.(?:jpg|jpeg|png|gif|webp)(?:\?|$)',url,re.I) or 'scontent.' in host:
            return 'MEDIA'
        return 'RESOURCE'
    return 'EXTERNAL'

def display_url(url, width=150):
    """Shorten long asset query strings for readability; requests still use original URLs."""
    if len(url)<=width:return url
    p=urllib.parse.urlsplit(url)
    root=urllib.parse.urlunsplit((p.scheme,p.netloc,p.path,'',''))
    if len(root)>width:return root[:width-3]+'...'
    return root+'?… [query shortened]'

class Extractor(HTMLParser):
    def __init__(self,base):
        super().__init__(convert_charrefs=True); self.base=base; self.links=[]; self.metadata={}; self._title=False
    def handle_starttag(self,tag,attrs):
        d=dict(attrs)
        if tag in ('a','link') and (d.get('href')): self.links.append(urllib.parse.urljoin(self.base,d['href']))
        if tag in ('img','video','source') and d.get('src'): self.links.append(urllib.parse.urljoin(self.base,d['src']))
        if tag=='meta':
            key=d.get('property') or d.get('name')
            if key in ('og:title','og:description','og:image','og:url','description','twitter:title'):
                self.metadata[key]=d.get('content','')[:240]
        if tag=='title':self._title=True
    def handle_endtag(self,tag):
        if tag=='title':self._title=False
    def handle_data(self,data):
        if self._title:self.metadata['title']=(self.metadata.get('title','')+data)[:240]

class FacebookRedirects(urllib.request.HTTPRedirectHandler):
    def redirect_request(self,req,fp,code,msg,headers,newurl):
        if not safe_fb_url(newurl): raise ValueError('Redirect blocked: destination outside approved Facebook HTTPS hosts')
        return super().redirect_request(req,fp,code,msg,headers,newurl)

def run(url,check=False,max_checks=20,color=True,focus=False,full_urls=False,hunt=None):
    if not safe_fb_url(url):raise ValueError('Only public HTTPS Facebook URLs on approved hosts are supported')
    op=urllib.request.build_opener(FacebookRedirects())
    def ink(s,c):return ANSI[c]+s+ANSI['reset'] if color else s
    print(ink('[NIGHTGLASS // BLUE SIGNAL] PUBLIC SOURCE INTELLIGENCE','cyan'),flush=True)
    req=urllib.request.Request(url,headers={'User-Agent':'NIGHTGLASS-LinkFusion/1.0','Accept':'text/html'})
    with op.open(req,timeout=12) as response:
        final=response.geturl(); status=response.status
        content_type=response.headers.get('Content-Type','')
        if 'html' not in content_type.lower():raise ValueError('URL did not return HTML')
        raw=response.read(LIMIT+1)
        truncated=len(raw)>LIMIT
        if truncated:raw=raw[:LIMIT]
    parser=Extractor(final);parser.feed(raw.decode('utf-8',errors='replace'))
    if truncated:
        print(ink(f'[SOURCE GUARD] Large HTML response: inspected first {LIMIT:,} bytes; partial results only.','yellow'),flush=True)
    print(ink(f'[SOURCE] HTTP {status} | {final}','blue'),flush=True)
    title=parser.metadata.get('og:title') or parser.metadata.get('title') or 'Unknown'
    desc=parser.metadata.get('og:description') or parser.metadata.get('description') or ''
    print(ink('═'*64,'blue'),flush=True)
    print(ink(f'  PAGE  {title[:72]}','white'),flush=True)
    if desc:print(ink(f'  INFO  {desc[:130]}'+('…' if len(desc)>130 else ''),'blue'),flush=True)
    print(ink('  MODE  Public HTML | Read-only | No login','dim'),flush=True)
    seen=set();links=[]
    for candidate in parser.links:
        p=urllib.parse.urlsplit(candidate)
        if p.scheme not in ('https','http'):continue
        value=clean_url(candidate)
        if value in seen:continue
        seen.add(value);links.append(value)
    totals=Counter(kind(v) for v in links)
    groups=Counter(interest(v) for v in links)
    ordered=[('POST-LINK','POSSIBLE POST LINKS','green'),('PAGE-LINK','FACEBOOK PAGE LINKS','blue'),('MEDIA','PUBLIC MEDIA REFERENCES','pink')]
    if not focus:ordered += [('RESOURCE','SITE RESOURCES','dim'),('EXTERNAL','OTHER LINKS','yellow')]
    shown_count=0
    for category,heading,shade in ordered:
        subset=[v for v in links if interest(v)==category]
        if not subset:continue
        print(ink(f'\n  ━━ {heading} ({len(subset)}) ━━',shade),flush=True)
        for v in subset:
            shown_count+=1
            print(ink(f'  [{shown_count:03d}] {v if full_urls else display_url(v,105)}',shade),flush=True)
    print(ink('\n'+'═'*64,'pink'),flush=True)
    print(ink('  NIGHTGLASS // BLUE SIGNAL SUMMARY','cyan'),flush=True)
    print(ink(f'  Discovered references : {len(parser.links)}','blue'),flush=True)
    print(ink(f'  Unique URLs           : {len(links)}','white'),flush=True)
    print(ink(f'  Possible post links   : {groups["POST-LINK"]}','green'),flush=True)
    print(ink(f'  Facebook Page links   : {groups["PAGE-LINK"]}','blue'),flush=True)
    print(ink(f'  Media references      : {groups["MEDIA"]}','pink'),flush=True)
    print(ink(f'  Site resources        : {groups["RESOURCE"]}','dim'),flush=True)
    print(ink(f'  Other links           : {groups["EXTERNAL"]}','yellow'),flush=True)
    if hunt:
        terms=[term.strip().casefold() for term in hunt.split(',') if term.strip()]
        if not terms or len(terms)>10 or any(len(t)>80 for t in terms):
            raise ValueError('--hunt requires 1-10 comma-separated terms (max 80 characters each)')
        print(ink('\n  ━━ INTEL HUNT // PUBLIC SOURCE MATCHES ━━','cyan'),flush=True)
        hits=[]
        for field,value in parser.metadata.items():
            if any(t in value.casefold() for t in terms):
                hits.append(('META:'+field,value))
        for value in links:
            if any(t in urllib.parse.urlsplit(value).path.casefold() for t in terms):
                hits.append((interest(value),value))
        for source,value in hits[:50]:
            print(ink(f'  [{source}] {display_url(value,135) if not full_urls else value}','green'),flush=True)
        print(ink(f'  [HUNT] matched={len(hits)} shown={min(len(hits),50)} scope=public-page-html-only','cyan'),flush=True)
        if not hits: print(ink('  No matching links or metadata in the inspected HTML.','yellow'),flush=True)
    if focus and (groups['RESOURCE'] or groups['EXTERNAL']):
        print(ink(f'  Quietly hidden        : {groups["RESOURCE"]+groups["EXTERNAL"]} noisy links (use --all-links)','dim'),flush=True)
    ok=0;errors=0
    if check:
        candidates=[v for v in links if safe_fb_url(v)][:max_checks]
        for v in candidates:
            try:
                rq=urllib.request.Request(v,headers={'User-Agent':'NIGHTGLASS-LinkFusion/1.0'},method='HEAD')
                with op.open(rq,timeout=8) as resp:code=resp.status
                if 200<=code<400:ok+=1
                else: errors+=1
                print(ink(f'[HTTP {code}] {v}','green' if code<400 else 'yellow'),flush=True)
            except (urllib.error.URLError,ValueError,OSError) as e:
                errors+=1;print(ink(f'[CHECK FAILED] {v} | {type(e).__name__}','red'),flush=True)
    print(ink(f'[TOTAL] discovered={len(parser.links)} unique={len(links)} facebook={totals["FACEBOOK"]} assets={totals["ASSET"]} external={totals["EXTERNAL"]} checked_ok={ok} checked_errors={errors}','cyan'),flush=True)
    print('[SOURCE STATUS] Public HTML links only; not authenticated posts, friends or followers.' + (' HTML truncated; counts are partial.' if truncated else ''),flush=True)
    return links

def main():
    p=argparse.ArgumentParser(description='NIGHTGLASS existing module enhancement: public link discovery and checks')
    p.add_argument('url');p.add_argument('--check',action='store_true');p.add_argument('--max-checks',type=int,default=20);p.add_argument('--no-color',action='store_true');p.add_argument('--all-links',action='store_true',help='Display resources and other links as well as useful URLs');p.add_argument('--focus',action='store_true',help='Compatibility alias for default clean view');p.add_argument('--full-urls',action='store_true',help='Show full URLs including long asset query strings');p.add_argument('--hunt',metavar='TERMS',help='Search fetched public HTML metadata and discovered link paths; comma-separated keywords')
    a=p.parse_args()
    if not 0<=a.max_checks<=50:p.error('--max-checks must be between 0 and 50')
    try:run(a.url,a.check,a.max_checks,not a.no_color,not a.all_links,a.full_urls,a.hunt)
    except (ValueError,urllib.error.URLError,OSError) as e:print(f'[NIGHTGLASS ERROR] {e}',file=sys.stderr);sys.exit(1)
if __name__=='__main__': main()
