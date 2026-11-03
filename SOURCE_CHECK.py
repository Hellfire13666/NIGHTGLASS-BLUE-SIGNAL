"""Opt-in unauthenticated, single-URL public source availability check. No scraping of account networks."""
from pathlib import Path
from datetime import datetime,timezone
from urllib.request import Request, build_opener, HTTPRedirectHandler
from urllib.error import HTTPError,URLError
from urllib.parse import urlsplit
import json, hashlib, socket
from datetime import timedelta
from RESEARCH_DESK import normalize
ALLOWED={'facebook.com','www.facebook.com','m.facebook.com','web.facebook.com','mbasic.facebook.com','fb.watch','www.fb.watch'}
class NoRedirect(HTTPRedirectHandler):
    def redirect_request(self,req,fp,code,msg,headers,newurl):
        return None

def inspect(url, fetcher=None):
    clean=normalize(url)
    result={'url':clean,'checked_utc':datetime.now(timezone.utc).isoformat(), 'method':'UNAUTHENTICATED SINGLE-URL HTTP HEAD','retrieval':'NOT CONFIRMED','content_collected':False,'status_code':None,'redirect':None,'note':'An HTTP response does not prove the content is publicly visible.'}
    try:
        if fetcher is None:
            req=Request(clean,method='HEAD',headers={'User-Agent':'NIGHTGLASS-SourceCheck/1.0 (research source availability; no content collection)','Accept':'text/html'})
            try:res=build_opener(NoRedirect).open(req, timeout=8)
            except HTTPError as exc:res=exc
            code=res.code
            loc=res.headers.get('Location')
        else:code,loc=fetcher(clean)
        result['status_code']=int(code)
        if loc:
            # Never automatically follow a redirect. Do not record query strings or tokens.
            parts=urlsplit(loc)
            result['redirect']='IN-DOMAIN (NOT FOLLOWED)' if parts.hostname and parts.hostname.lower() in ALLOWED else 'REDIRECT NOT FOLLOWED'
        if code==429:result['retrieval']='RATE LIMITED / COOLDOWN REQUIRED'
        elif code in (200,204):result['retrieval']='HTTP RESPONSE ONLY · CONTENT NOT VERIFIED'
        elif code in (301,302,303,307,308):result['retrieval']='REDIRECT · NOT FOLLOWED'
        elif code in (401,403):result['retrieval']='ACCESS RESTRICTED / UNAVAILABLE'
        elif code in (404,410):result['retrieval']='NOT FOUND / UNAVAILABLE'
        else:result['retrieval']='HTTP RESPONSE · CONTENT NOT VERIFIED'
    except (URLError,TimeoutError,ValueError,OSError,socket.timeout) as exc:
        result['retrieval']='NETWORK ERROR / NOT VERIFIED'
        result['error_type']=type(exc).__name__
    return result

def save_report(folder,result):
    folder=Path(folder)
    if folder.is_symlink():raise ValueError('Symlink report folder not allowed')
    folder.mkdir(parents=True,exist_ok=True,mode=0o700)
    ident=hashlib.sha256((result['url']+result['checked_utc']).encode()).hexdigest()[:12]
    out=folder/('source-check-'+ident+'.json')
    with out.open('x',encoding='utf-8') as f:json.dump(result,f,indent=2)
    out.chmod(0o600)
    return out

# Persistent source guard. No automatic retries or URL-rotation.
# Guard state contains only normalized URLs and last-check metadata.
DEFAULT_COOLDOWN_HOURS=24
RESTRICTED_COOLDOWN_HOURS=72

def _guard_file(root):
    return Path(root)/'source-guard.json'

def guard_status(root,url,now=None):
    clean=normalize(url)
    now=now or datetime.now(timezone.utc)
    path=_guard_file(root)
    if path.is_symlink():raise ValueError('Symlink guard file not allowed')
    state={}
    if path.is_file():
        try:
            raw=json.loads(path.read_text(encoding='utf-8'))
            if isinstance(raw,dict):state=raw
        except (ValueError,OSError):
            return {'allowed':False,'reason':'GUARD STATE UNREADABLE · FAIL CLOSED'}
    entry=state.get(clean,{})
    try:
        checked=datetime.fromisoformat(entry['checked_utc'])
        if checked.tzinfo is None:raise ValueError('Timestamp lacks timezone')
        hours=RESTRICTED_COOLDOWN_HOURS if entry.get('status_code') in (403,429) else DEFAULT_COOLDOWN_HOURS
        until=checked+timedelta(hours=hours)
        if now<until:
            return {'allowed':False,'reason':'COOLDOWN ACTIVE · SAVED RESULT FIRST','until':until.isoformat(),'last_status':entry.get('status_code')}
    except (KeyError,ValueError,TypeError):
        if entry:return {'allowed':False,'reason':'INVALID GUARD ENTRY · FAIL CLOSED'}
    return {'allowed':True,'reason':'ONE EXPLICIT REQUEST AVAILABLE'}

def _record_guard(root,url,result):
    folder=Path(root)
    if folder.is_symlink():raise ValueError('Symlink folder not allowed')
    folder.mkdir(parents=True,exist_ok=True,mode=0o700)
    path=_guard_file(folder)
    if path.is_symlink():raise ValueError('Symlink guard file not allowed')
    state=json.loads(path.read_text(encoding='utf-8')) if path.exists() else {}
    state[normalize(url)]={'checked_utc':result['checked_utc'],'status_code':result.get('status_code'),'retrieval':result.get('retrieval')}
    # Atomic replace and private permissions
    import os,tempfile
    fd,tmp=tempfile.mkstemp(prefix='.guard-',dir=folder)
    try:
        with os.fdopen(fd,'w',encoding='utf-8') as f:json.dump(state,f,indent=2)
        os.chmod(tmp,0o600)
        os.replace(tmp,path)
    finally:
        if os.path.exists(tmp):os.unlink(tmp)

def interactive(root):
    print('\n◆ NIGHTGLASS // SOURCE GUARD · SPAM-SAFE SINGLE CHECK')
    print('NO AUTORETRY · NO COOKIE ACCESS · NO URL ROTATION')
    print('Saved results are preferred. No posts or comments collected.')
    try:
        url=input('Public Facebook Page/post HTTPS URL (Enter cancels): ').strip()
        if not url:return 0
        clean=normalize(url)
        status=guard_status(root,clean)
        if not status['allowed']:
            print('STOP:',status['reason'])
            if status.get('until'):print('Earliest manual recheck:',status['until'])
            print('No network request made.')
            return 0
        if input('Make ONE HTTP HEAD request, with no retries? [y/N] ').strip().lower()!='y':
            print('Cancelled. No network request made.');return 0
        # Record a cooldown before network work to avoid repeated requests after failures.
        started=datetime.now(timezone.utc).isoformat()
        _record_guard(root,clean,{'checked_utc':started,'status_code':None,'retrieval':'IN PROGRESS / NO RETRY'})
        r=inspect(clean)
        _record_guard(root,clean,r)
        print('HTTP:',r['status_code'] if r['status_code'] is not None else 'NO RESPONSE')
        print('STATUS:',r['retrieval'])
        if r['status_code'] in (403,429):print('SOURCE GUARD: RESTRICTED · 72-HOUR COOLDOWN')
        else:print('SOURCE GUARD: 24-HOUR COOLDOWN · MANUAL CHECK ONLY')
        print('CONTENT: Not downloaded or verified')
        p=save_report(root,r)
        print('SAVED:',p.name)
    except (ValueError,OSError,EOFError,KeyboardInterrupt) as exc:
        print('Source Guard stopped safely:',type(exc).__name__)
    return 0
