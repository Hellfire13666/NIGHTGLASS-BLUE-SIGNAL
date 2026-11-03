"""Offline Page Research Fusion. No network calls or browser sessions."""
from pathlib import Path
from datetime import datetime, timezone
from urllib.parse import urlsplit
import hashlib, json, csv
from RESEARCH_DESK import list_entries, normalize, classify
from POST_INTELLIGENCE import analyze_export


def match_page(page, post):
    """Match a post link only if its URL explicitly begins with saved Page path."""
    try:
        a=urlsplit(normalize(page)); b=urlsplit(normalize(post))
        if a.hostname != b.hostname: return False
        path=a.path.rstrip('/').casefold()
        if not path or path in ('/photo.php','/story.php'):return False
        sub=b.path.casefold()
        return sub.startswith(path + '/posts/') or sub.startswith(path + '/videos/') or sub.startswith(path + '/photos/') or sub.startswith(path + '/reels/')
    except (ValueError,TypeError):return False


def fuse(root, filename):
    root=Path(root)
    refs=[r for r in list_entries(root/'ResearchDesk') if r.get('kind')=='Page/profile or other link (unverified)']
    imported=analyze_export(filename)
    matches=[];unmatched=[]
    for post in imported['posts']:
        linked=[r for r in refs if match_page(str(r.get('url','')),post.get('url',''))]
        entry={'post':post,'matching_reference_ids':[r['id'] for r in linked], 'match_basis':'URL PATH ONLY / UNVERIFIED' if linked else 'NONE'}
        (matches if linked else unmatched).append(entry)
    return {'mode':'LOCAL PAGE RESEARCH FUSION / NO NETWORK','created_utc':datetime.now(timezone.utc).isoformat(),
        'verification':'USER-SUPPLIED / NOT AUTHENTICATED AS FACEBOOK CONTENT',
        'source_file':Path(filename).name,'source_file_sha256':imported['file_sha256'],
        'page_reference_count':len(refs),'post_count':len(imported['posts']),
        'matched_count':len(matches),'unmatched_count':len(unmatched),
        'import_reference_count':imported['reference_count'],
        'pages':[{'reference_id':r['id'],'url':r['url'],'status':'SAVED LINK / NOT FETCHED'} for r in refs],
        'matched_posts':matches,'unmatched_posts':unmatched,
        'warning':'URL-only association is not proof of authorship, public visibility, authenticity, or a relationship. No Facebook content was fetched.'}


def save(result,root):
    root=Path(root)/'PageFusionReports'
    if root.is_symlink():raise ValueError('Unsafe report folder')
    root.mkdir(parents=True,exist_ok=True,mode=0o700)
    stem='page-fusion-'+datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S%fZ')
    dest=root/(stem+'.json')
    with dest.open('x',encoding='utf-8') as f:json.dump(result,f,indent=2,ensure_ascii=False)
    dest.chmod(0o600)
    return dest


def interactive(root):
    print('\n◆ NIGHTGLASS // PAGE RESEARCH FUSION · OFFLINE ONLY')
    print('Saved Page references + permitted local post exports · No Facebook requests')
    name=input('Local post CSV / JSON / JSONL (Enter cancels): ').strip()
    if not name:return 0
    try:
        result=fuse(root,name)
        path=save(result,root)
        print('PAGES:',result['page_reference_count'],'POSTS:',result['post_count'],
              'MATCHED:',result['matched_count'],'UNMATCHED:',result['unmatched_count'])
        for entry in result['matched_posts'][:50]:
            p=entry['post']
            print('MATCH · URL ONLY:',p.get('url',''),'·',','.join(entry['matching_reference_ids']))
        print('STATUS: IMPORTED / UNVERIFIED · NOT LIVE')
        print('SAVED:',path)
        return 0
    except (OSError,ValueError,UnicodeError,json.JSONDecodeError) as exc:
        print('Fusion stopped:',exc);return 2
