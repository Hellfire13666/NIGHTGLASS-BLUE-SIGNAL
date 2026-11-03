#!/usr/bin/env python3
"""NIGHTGLASS public HTML post-link discovery. No auth, no hidden data, no crawling."""
import argparse
from datetime import datetime, timezone
from html import unescape
from html.parser import HTMLParser
import ipaddress
import json
import os
from pathlib import Path
import re
import urllib.parse as urlp
import urllib.request as req
from urllib.error import HTTPError, URLError

MAX_BYTES=3*1024*1024
UA="NIGHTGLASS-PublicDiscovery/2.6.7 (single public HTML request)"
HOSTS={"facebook.com","www.facebook.com","m.facebook.com","web.facebook.com","mbasic.facebook.com"}
# Domain-only allowlist, no arbitrary endpoints and no authenticated context
def valid_url(url):
    try:
        u=urlp.urlsplit(url)
        if u.scheme!="https" or u.hostname not in HOSTS or u.username or u.password or u.port not in (None,443):
            return False
        if re.search(r"(?:access_token|cookie|password|session|auth|key)=",u.query,re.I):
            return False
        if u.path.startswith(("/login","/settings","/messages","/api/")):
            return False
        return True
    except ValueError:
        return False

class NoUnsafeRedirect(req.HTTPRedirectHandler):
    def redirect_request(self, request, fp, code, msg, headers, newurl):
        if not valid_url(newurl):
            raise ValueError("Redirect left approved public Facebook HTTPS hosts")
        return super().redirect_request(request,fp,code,msg,headers,newurl)

class Collector(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.links=[]
        self.meta={}
        self.title=""
        self.in_title=False
    def handle_starttag(self,tag,attrs):
        d=dict(attrs)
        if tag=="title":self.in_title=True
        if tag=="a" and d.get("href"):self.links.append(d["href"])
        if tag=="link" and d.get("rel") in ("canonical","alternate") and d.get("href"):self.links.append(d["href"])
        if tag=="meta":
            name=d.get("property") or d.get("name")
            if name in ("og:title","og:description","og:url","description") and name not in self.meta:
                self.meta[name]=d.get("content","")[:600]
            if name=="og:url" and d.get("content"):self.links.append(d["content"])
    def handle_endtag(self,tag):
        if tag=="title":self.in_title=False
    def handle_data(self,data):
        if self.in_title:self.title+=data

POST_RE=re.compile(r"^/(?:[^/?#]+/posts/(?:[A-Za-z0-9_-]+)|permalink\.php|story\.php|photo\.php|watch/|reel/[A-Za-z0-9_-]+|[^/?#]+/videos/[A-Za-z0-9_-]+)(?:/|$)")
def post_candidate(raw,base):
    raw=unescape(raw).replace(r"\/","/")
    try:
        link=urlp.urljoin(base,raw)
        u=urlp.urlsplit(link)
        if not valid_url(link):return None
        if not POST_RE.match(u.path):return None
        if u.path in ("/permalink.php","/story.php","/photo.php") and not any(k in urlp.parse_qs(u.query) for k in ("story_fbid","fbid","id")):
            return None
        return urlp.urlunsplit((u.scheme,u.netloc,u.path,u.query,""))
    except ValueError:
        return None

def canonical_candidate(url):
    """Collapse comment variants and host aliases, not unrelated post IDs."""
    u=urlp.urlsplit(url)
    path=u.path.rstrip('/') or '/'
    qs=urlp.parse_qs(u.query)
    # Retain only ID parameters that identify a story when the path is generic.
    if path in ('/story.php','/permalink.php','/photo.php'):
        keep=[(k, v[0]) for k in ('story_fbid','fbid','id') if (v:=qs.get(k))]
        query=urlp.urlencode(keep)
    else:
        query=''
    return urlp.urlunsplit(('https','www.facebook.com',path,query,''))

def candidate_type(url):
    path=urlp.urlsplit(url).path
    return 'REEL' if path.startswith('/reel/') else 'VIDEO' if '/videos/' in path or path.startswith('/watch/') else 'POST'

def analyze(html,source,target=50):
    if not 1<=target<=200:raise ValueError('Target must be 1 through 200')
    doc=Collector()
    doc.feed(html)
    # URL forms exposed as escaped strings in raw HTML (not JavaScript execution).
    extra=re.findall(r'https?:(?:\\?/){2}(?:www\.|m\.|web\.)?facebook\.com(?:[^"\s<>\\]|\\.){1,350}',html)
    links=doc.links+extra
    unique={}
    for raw in links:
        candidate=post_candidate(raw,source)
        if candidate:
            key=canonical_candidate(candidate)
            unique.setdefault(key,{'type':candidate_type(key),'url':key})
    all_hits=sorted(unique.values(),key=lambda x:(x['type'],x['url']))
    selected=all_hits[:target]
    return {'source':source,'title':doc.meta.get('og:title') or doc.title.strip()[:200],
            'description':doc.meta.get('og:description') or doc.meta.get('description',''),
            'html_references':len(links),'distinct_candidates':len(all_hits),
            'post_candidates':[x['url'] for x in selected],
            'candidate_details':selected,'target':target,
            'capped':len(all_hits)>target,
            'type_counts':{t:sum(x['type']==t for x in all_hits) for t in ('POST','REEL','VIDEO')}}

def fetch_once(url,timeout=12):
    if not valid_url(url):raise ValueError("Only public HTTPS Facebook page URLs allowed")
    opener=req.build_opener(NoUnsafeRedirect())
    request=req.Request(url,headers={"User-Agent":UA,"Accept":"text/html"},method="GET")
    with opener.open(request,timeout=timeout) as response:
        final=response.geturl()
        if not valid_url(final):raise ValueError("Unexpected final URL")
        contenttype=response.headers.get("Content-Type","")
        if "text/html" not in contenttype.lower():raise ValueError("Response is not HTML")
        raw=response.read(MAX_BYTES+1)
        partial=len(raw)>MAX_BYTES
        if partial:raw=raw[:MAX_BYTES]
        text=raw.decode("utf-8",errors="replace")
        return text,final,partial,getattr(response,"status",None)

def private_save(result):
    vault=Path.home()/"Documents"/"NIGHTGLASS-VAULT"/"public-post-discovery"
    vault.mkdir(parents=True,exist_ok=True,mode=0o700)
    os.chmod(vault,0o700)
    stamp=datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S%fZ")
    report=vault/("discovery-"+stamp+".json")
    fd=os.open(str(report),os.O_WRONLY|os.O_CREAT|os.O_EXCL,0o600)
    with os.fdopen(fd,"w",encoding="utf-8") as f:json.dump(result,f,indent=2,ensure_ascii=False)
    return report

def main(argv=None):
    ap=argparse.ArgumentParser(description="Public Facebook HTML post-link discovery; not a live feed scraper")
    src=ap.add_mutually_exclusive_group(required=True)
    src.add_argument("--url",help="One public HTTPS Facebook URL, one request only")
    src.add_argument("--html",type=Path,help="User-saved public HTML file, completely offline")
    ap.add_argument("--save",action="store_true",help="Save metadata and candidate URLs privately")
    ap.add_argument("--target",type=int,default=50,choices=(10,25,50,100,200),help="Maximum candidates to print (default 50); not a fetch count")
    ap.add_argument("--timeout",type=int,default=12)
    args=ap.parse_args(argv)
    try:
        if args.url:
            html,source,partial,status=fetch_once(args.url,args.timeout)
            mode="PUBLIC HTML RESPONSE"; status_text=str(status)
        else:
            path=args.html.expanduser()
            if not path.is_file() or path.is_symlink():raise ValueError("HTML file missing or symlink")
            with path.open("rb") as f:raw=f.read(MAX_BYTES+1)
            partial=len(raw)>MAX_BYTES
            html=raw[:MAX_BYTES].decode("utf-8",errors="replace")
            source="https://www.facebook.com/"
            mode="USER-SAVED HTML";status_text="NOT CHECKED"
        result=analyze(html,source,args.target)
        result.update({"mode":mode,"http_status":status_text,"partial_html":partial,
                       "status":"CANDIDATE URLS ONLY; NO POSTS RETRIEVED OR VERIFIED"})
        print("\nNIGHTGLASS // PUBLIC POST DISCOVERY v2.6.7")
        print("[MODE]",mode,"| HTTP",status_text,"|",("HTML TRUNCATED" if partial else "HTML READ"))
        print("[TITLE]",result["title"] or "NOT PROVIDED")
        print("[INFO]",result["description"] or "NOT PROVIDED")
        for i,hit in enumerate(result['candidate_details'],1):
            print(f"[{i:03}] {hit['type']} CANDIDATE (UNVERIFIED): {hit['url']}")
        print('[TARGET]',args.target,'| [FOUND]',result['distinct_candidates'],'distinct candidate URLs',
              '| [SHOWN]',len(result['candidate_details']))
        print('[TYPES]', ' | '.join(f'{kind}={amount}' for kind,amount in result['type_counts'].items()))
        print('[REFERENCES]',result['html_references'],'| [REQUESTS]',1 if args.url else 0)
        if result['capped']:print('[LIMIT] Some discovered candidates were not displayed; raise --target to show more.')
        print("[SOURCE] Public HTML only | no feed, comments, friends or private posts")
        if not result["post_candidates"]:
            print("[RESULT] No post-shaped URLs exposed in this HTML. This does NOT prove the Page has no posts.")
        if args.save:print("[SAVED] Private:",private_save(result).name)
        return 0
    except (ValueError,OSError,URLError,HTTPError) as exc:
        print("[STOP] Public HTML inspection failed:",str(exc)[:250]);return 2

if __name__=="__main__":raise SystemExit(main())
