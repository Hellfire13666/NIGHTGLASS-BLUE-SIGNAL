"""Offline photo-post fusion. User-owned or authorized exports only. No network functionality."""
from pathlib import Path
from datetime import datetime,timezone
from urllib.parse import urlsplit,parse_qs
import csv,json,hashlib,uuid
from RESEARCH_DESK import list_entries,normalize
MAX_BYTES=5_000_000

def read_records(path):
    p=Path(path).expanduser()
    if p.is_symlink() or not p.is_file() or p.suffix.lower() not in ('.csv','.json','.jsonl') or p.stat().st_size>MAX_BYTES:
        raise ValueError('Use a regular CSV, JSON or JSONL file up to 5 MB')
    if p.suffix.lower()=='.csv':
        with p.open(encoding='utf-8-sig',newline='') as f: rows=list(csv.DictReader(f))
    elif p.suffix.lower()=='.jsonl':
        rows=[json.loads(line) for line in p.read_text(encoding='utf-8-sig').splitlines() if line.strip()]
    else:
        val=json.loads(p.read_text(encoding='utf-8-sig'))
        rows=val if isinstance(val,list) else next((val[k] for k in ('comments','posts','records') if isinstance(val.get(k),list)),[])
    if not isinstance(rows,list) or len(rows)>10000 or any(not isinstance(x,dict) for x in rows):raise ValueError('Expected an array of record objects (max 10,000)')
    return rows,hashlib.sha256(p.read_bytes()).hexdigest()

def photo_id(url):
    try:
        u=urlsplit(normalize(url));return parse_qs(u.query).get('fbid',[''])[0] if u.path.endswith('/photo.php') else ''
    except (ValueError,TypeError):return ''

def fuse(source,post_rows=(),comment_rows=(),post_sha=None,comments_sha=None):
    if not isinstance(source,dict) or not source.get('url'):raise ValueError('Select a valid source')
    link=normalize(source['url']);pid=photo_id(link)
    matches=[]
    for p in post_rows:
        ref=str(p.get('url') or p.get('post_url') or '').strip()
        raw_id=str(p.get('post_id') or p.get('photo_id') or '').strip()
        if (ref and ref==link) or (pid and (raw_id==pid or (ref and photo_id(ref)==pid))):matches.append(p)
    cap=next((str(p.get('text') or p.get('caption') or '')[:5000] for p in matches if p.get('text') or p.get('caption')),'')
    date=next((str(p.get('date') or p.get('created_time') or '')[:100] for p in matches if p.get('date') or p.get('created_time')),'')
    accepted=[];seen=set();skipped=0
    for c in comment_rows:
        ref=str(c.get('post_url') or c.get('url') or '').strip()
        raw_id=str(c.get('post_id') or c.get('photo_id') or '').strip()
        # All comment records must explicitly associate with selected post; never attribute unrelated rows.
        if not ((ref and (ref==link or (pid and photo_id(ref)==pid))) or (pid and raw_id==pid) or (source.get('id') and raw_id==source.get('id'))):
            skipped+=1;continue
        item={'comment_id':str(c.get('comment_id') or c.get('id') or '')[:160], 'parent_id':str(c.get('parent_id') or '')[:160], 'author':str(c.get('author') or c.get('name') or '')[:180], 'text':str(c.get('text') or c.get('message') or '')[:5000], 'date':str(c.get('date') or c.get('created_time') or '')[:100], 'provenance':'USER-SUPPLIED / NOT INDEPENDENTLY VERIFIED'}
        key=item['comment_id'] or hashlib.sha256(json.dumps(item,sort_keys=True).encode()).hexdigest()
        if key in seen:skipped+=1;continue
        seen.add(key);accepted.append(item)
    return {'source':'USER-SUPPLIED LOCAL RESEARCH / NOT LIVE', 'verified_facebook_content':False,'network_requests':0,'checked_utc':datetime.now(timezone.utc).isoformat(), 'reference_id':source.get('id'),'post_url':link,'photo_id':pid,'caption':cap,'post_date':date,'post_match_count':len(matches),'comment_count':len(accepted),'reply_count':sum(bool(c['parent_id']) for c in accepted),'skipped_or_duplicate_comments':skipped,'comments':accepted,'post_file_sha256':post_sha,'comments_file_sha256':comments_sha,'warning':'All content is user-provided and not independently authenticated as Facebook content.'}

def save(result,root):
    d=Path(root);d.mkdir(parents=True,exist_ok=True,mode=0o700)
    p=d/('photo-fusion-'+datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')+'-'+uuid.uuid4().hex[:8]+'.json')
    with p.open('x',encoding='utf-8') as f:json.dump(result,f,indent=2,ensure_ascii=False)
    p.chmod(0o600);return p

def interactive(root):
    print('\n◆ NIGHTGLASS // PHOTO POST FUSION · OFFLINE · NO FACEBOOK REQUESTS')
    sources=list_entries(Path(root)/'ResearchDesk')
    if not sources:print('No local references here. Add one with main menu 15, or import a research index into this installation.');return 0
    for i,s in enumerate(sources,1):print(f"[{i}] {s.get('id')} · {s.get('kind')} · {s.get('url')}")
    try:
        chosen=input('Reference number (Enter cancels): ').strip()
        if not chosen:return 0
        n=int(chosen)
        if n<1 or n>len(sources):raise ValueError('Invalid reference number')
        src=sources[n-1]
        post_path=input('Optional local post CSV/JSON/JSONL (Enter skips): ').strip()
        comment_path=input('Optional local comments CSV/JSON/JSONL (Enter skips): ').strip()
        posts,p_sha=read_records(post_path) if post_path else ([],None)
        comments,c_sha=read_records(comment_path) if comment_path else ([],None)
        result=fuse(src,posts,comments,p_sha,c_sha)
        print('STATUS: USER-SUPPLIED / NOT LIVE · NETWORK: OFF')
        print('PHOTO ID:',result['photo_id'] or 'NOT AVAILABLE')
        print('CAPTION:',result['caption'][:240] or 'NOT PROVIDED')
        print('DATE:',result['post_date'] or 'NOT PROVIDED')
        print('MATCHED POSTS:',result['post_match_count'],'COMMENTS:',result['comment_count'],'REPLIES:',result['reply_count'])
        for i,c in enumerate(result['comments'][:100],1):print(f"[{i:03}] {c['author'] or 'UNKNOWN'} | {c['date'] or 'UNDATED'} | {c['text'][:200]}")
        print('SAVED:',save(result,Path(root)/'PhotoFusionReports'))
        return 0
    except (ValueError,TypeError,OSError,json.JSONDecodeError) as e:print('PHOTO FUSION STOPPED:',e);return 2
