"""Offline public-post fusion from permitted local exports and verified source metadata."""
from pathlib import Path
from datetime import datetime, timezone
import json, csv, hashlib
from POST_INTELLIGENCE import analyze_export
from RESEARCH_DESK import normalize

def load_sources(root):
    p=Path(root)/'ResearchDesk'/'sources.json'
    if not p.is_file(): return []
    data=json.loads(p.read_text(encoding='utf-8'))
    if not isinstance(data,list):raise ValueError('Source index must be a list')
    return data[:10000]

def load_checks(root):
    folder=Path(root)/'SourceChecks'
    records={}
    if not folder.is_dir():return records
    for path in sorted(folder.glob('source-check-*.json')):
        if path.is_symlink() or path.stat().st_size>100_000:continue
        try:
            item=json.loads(path.read_text(encoding='utf-8'))
            url=normalize(item.get('url',''))
            if isinstance(item.get('checked_utc'),str) and (url not in records or item['checked_utc']>records[url].get('checked_utc','')):
                records[url]=item
        except (ValueError,TypeError,KeyError,json.JSONDecodeError):continue
    return records

def fuse(export,root,keyword=''):
    result=analyze_export(export,keyword)
    indexed=set()
    for item in load_sources(root):
        if isinstance(item,dict):
            try:indexed.add(normalize(item.get('url','')))
            except (ValueError,TypeError):pass
    checks=load_checks(root)
    for item in result['posts']:
        link=item['url']
        observed=checks.get(link,{}) if link else {}
        item['research_index_match']=bool(link and link in indexed)
        item['http_status_observed']=observed.get('status_code')
        item['http_checked_utc']=observed.get('checked_utc')
        item['content_verified']=False
        item['provenance']='IMPORTED RECORD / UNVERIFIED CONTENT'
    result['fusion_type']='OFFLINE IMPORT + LOCAL SOURCE REFERENCES'
    result['source_checks_matched']=sum(p['http_checked_utc'] is not None for p in result['posts'])
    result['indexed_links_matched']=sum(p['research_index_match'] for p in result['posts'])
    result['warning']='HTTP accessibility does not authenticate the imported post or prove public visibility.'
    return result

def save(result,root):
    folder=Path(root)/'FusionReports'
    folder.mkdir(mode=0o700,parents=True,exist_ok=True)
    dest=folder/('fusion-'+datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S%fZ'))
    dest.mkdir(mode=0o700)
    jp=dest/'fusion.json'
    jp.write_text(json.dumps(result,indent=2,ensure_ascii=False),encoding='utf-8');jp.chmod(0o600)
    cp=dest/'fusion.csv'
    fields=['date','post_id','text','url','research_index_match','http_status_observed','http_checked_utc','provenance']
    with cp.open('x',encoding='utf-8',newline='') as fp:
        writer=csv.DictWriter(fp,fieldnames=fields,extrasaction='ignore');writer.writeheader()
        for post in result['posts']:
            writer.writerow({k: ('\t'+str(post.get(k,'')) if str(post.get(k,''))[:1] in '=+-@' else post.get(k,'')) for k in fields})
    cp.chmod(0o600)
    return dest

def interactive(root):
    print('\n◆ NIGHTGLASS // PUBLIC POST FUSION · OFFLINE SOURCE RESEARCH')
    print('Permitted export only · Local source references · No Facebook post scraping')
    source=input('Local CSV/JSON/JSONL export (Enter cancels): ').strip()
    if not source:return 0
    keyword=input('Optional keyword (Enter for all): ').strip()
    try:
        report=fuse(source,root,keyword)
        print(f"INPUT {report['input_count']} | RETAINED {report['retained_count']} | DEDUP {report['duplicates_removed']}")
        print(f"INDEX MATCHES {report['indexed_links_matched']} | HTTP CHECK MATCHES {report['source_checks_matched']}")
        for i,post in enumerate(report['posts'][:100],1):
            print(f"[{i:03}] {post['date']} | {post['text'][:200]}")
            print('  LINK:',post['url'] or 'NONE','| HTTP:',post['http_status_observed'] or 'NOT CHECKED')
            print('  STATUS: IMPORTED, NOT AUTHENTICATED')
        dest=save(report,root)
        print('SAVED:',dest/'fusion.json','|',dest/'fusion.csv')
        return 0
    except (OSError,ValueError,json.JSONDecodeError,UnicodeError) as exc:
        print('Fusion stopped:',exc);return 2
