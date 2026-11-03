"""Offline, opt-in post intelligence from user supplied permitted local exports."""
from pathlib import Path
from datetime import datetime, timezone
import csv, json, hashlib, re
from urllib.parse import urlsplit
from RESEARCH_DESK import normalize, classify

MAX_BYTES=15_000_000
POST_FIELDS=('message','text','content','body','post_text','description')
DATE_FIELDS=('created_time','created_at','timestamp','date','published')
URL_FIELDS=('permalink_url','post_url','url','link')
ID_FIELDS=('post_id','id')

def pick(obj,keys):
    return next((obj[k] for k in keys if isinstance(obj.get(k),(str,int)) and str(obj[k]).strip()), '')

def load_export(path):
    p=Path(path).expanduser()
    if not p.is_file() or p.is_symlink():raise ValueError('Provide a regular local CSV, JSON or JSONL file')
    if p.stat().st_size>MAX_BYTES:raise ValueError('File exceeds 15 MB limit')
    suffix=p.suffix.lower()
    if suffix=='.csv':
        with p.open(encoding='utf-8-sig',newline='') as f: data=list(csv.DictReader(f))
    elif suffix=='.jsonl':
        with p.open(encoding='utf-8-sig') as f:data=[json.loads(line) for line in f if line.strip()]
    elif suffix=='.json':
        data=json.loads(p.read_text(encoding='utf-8-sig'))
        if isinstance(data,dict):
            data=next((data[k] for k in ('posts','data','items','records') if isinstance(data.get(k),list)),None)
    else:raise ValueError('Supported formats: CSV, JSON, JSONL')
    if not isinstance(data,list) or any(not isinstance(item,dict) for item in data):raise ValueError('Expected list of post objects')
    if len(data)>10000:raise ValueError('Too many records')
    return p,data

def analyze_export(path,keyword=''):
    p,items=load_export(path)
    records=[];references=[];seen=set();invalid=0;dupes=0;classified=0
    checksum=hashlib.sha256(p.read_bytes()).hexdigest()
    for obj in items:
        value=str(pick(obj,POST_FIELDS)).strip()[:12000]
        date=str(pick(obj,DATE_FIELDS))[:128]
        rawurl=str(pick(obj,URL_FIELDS)).strip()
        link=''
        if rawurl:
            try: link=normalize(rawurl)
            except (ValueError,TypeError):invalid+=1
        pid=str(pick(obj,ID_FIELDS))[:160]
        kind=classify(link) if link else 'unspecified source'
        # A Research Desk CSV is an index of references, not an export of posts.
        # A URL alone does not establish that post content was supplied.
        is_reference=(p.name.lower()=='sources.csv' and {'url','kind','verification'}.issubset(set(obj))) or (bool(link) and kind=='Page/profile or other link (unverified)' and not value and not date)
        if is_reference:
            references.append({'reference_id':pid,'url':link,'kind':kind,'status':'REFERENCE ONLY / NOT FETCHED'})
            classified+=1
            continue
        if not any((value,link,pid)):
            invalid+=1;continue
        key=(link or pid or hashlib.sha256((date+'\0'+value).encode()).hexdigest())
        if key in seen:dupes+=1;continue
        seen.add(key)
        if keyword and keyword.casefold() not in (value+' '+link+' '+pid).casefold():continue
        records.append({'post_id':pid,'date':date,'text':value,'url':link,'source_mode':'USER-SUPPLIED IMPORT / NOT LIVE','source_file_sha256':checksum})
    records.sort(key=lambda r:r['date'],reverse=True)
    return {'source':'USER-SUPPLIED LOCAL FILE','verification':'NOT AUTHENTICATED AS FACEBOOK CONTENT','checked_utc':datetime.now(timezone.utc).isoformat(),'filename':p.name,'file_sha256':checksum,'input_count':len(items),'reference_count':classified,'references':references,'retained_count':len(records),'duplicates_removed':dupes,'invalid_or_empty':invalid,'keyword_filter':keyword,'posts':records}

def save_private(report,root):
    root=Path(root);root.mkdir(mode=0o700,parents=True,exist_ok=True)
    stamp=datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S%fZ')
    dest=root/('posts-'+stamp);dest.mkdir(mode=0o700)
    p=dest/'posts.json'
    with p.open('x',encoding='utf-8') as f:json.dump(report,f,indent=2,ensure_ascii=False)
    p.chmod(0o600)
    csvpath=dest/'posts.csv'
    with csvpath.open('x',encoding='utf-8',newline='') as f:
        out=csv.DictWriter(f,fieldnames=['post_id','date','text','url','source_mode'],extrasaction='ignore');out.writeheader()
        for row in report['posts']:
            item={k:('\t'+v if isinstance(v,str) and v[:1] in '=+-@' else v) for k,v in row.items()};out.writerow(item)
    csvpath.chmod(0o600)
    return dest

def interactive(root):
    print('\n◆ NIGHTGLASS // POST INTELLIGENCE · OFFLINE IMPORT')
    print('User-supplied permitted exports only · No Facebook fetching · No credentials')
    path=input('Local CSV / JSON / JSONL post export (Enter cancels): ').strip()
    if not path:return 0
    keyword=input('Optional keyword filter (Enter for all): ').strip()
    try:
        report=analyze_export(path,keyword)
        print('INPUT:',report['input_count'],'POSTS:',report['retained_count'],'REFERENCES:',report['reference_count'],'DUPLICATES:',report['duplicates_removed'])
        for ref in report['references'][:100]:print('REFERENCE ONLY:',ref['kind'], '·',ref['url'])
        print('SOURCE STATUS: IMPORTED / UNVERIFIED · NOT LIVE')
        for i,item in enumerate(report['posts'][:100],1):
            print(f"[{i:03}] {item['date']} {item['post_id']}\n     {item['text'][:240]}\n     SOURCE: {item['url'] or 'NOT INCLUDED IN EXPORT'}")
        dest=save_private(report,root)
        print('PRIVATE REPORTS:',dest/'posts.json','|',dest/'posts.csv')
    except (OSError,ValueError,json.JSONDecodeError,UnicodeError) as exc:
        print('Import stopped:',exc);return 2
    return 0
