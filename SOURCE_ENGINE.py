"""Standalone, no-API, no-cookie browser-snapshot source adapter. Does not fetch URLs."""
from pathlib import Path
from html.parser import HTMLParser
from datetime import datetime, timezone
from urllib.parse import urlsplit
import hashlib, json, re
from POST_INTELLIGENCE import analyze_export, save_private
from PHOTO_POST_FUSION import interactive as photo_fusion
from PAGE_RESEARCH_FUSION import interactive as page_fusion

MAX_SNAPSHOT=5_000_000
class Metadata(HTMLParser):
 def __init__(self):
  super().__init__(convert_charrefs=True);self.meta={};self.title='';self._title=False
 def handle_starttag(self,tag,attrs):
  attrs=dict(attrs)
  if tag=='title':self._title=True
  if tag=='meta':
   key=(attrs.get('property') or attrs.get('name') or '').lower()
   if key in ('og:title','og:description','og:url','article:published_time','description'):
    self.meta[key]=str(attrs.get('content',''))[:2000]
 def handle_endtag(self,tag):
  if tag=='title':self._title=False
 def handle_data(self,data):
  if self._title:self.title+=data[:300]

def analyze_snapshot(filename,source_url=''):
 p=Path(filename).expanduser()
 if not p.is_file() or p.is_symlink() or p.suffix.lower() not in ('.html','.htm'):
  raise ValueError('Choose a regular browser-saved HTML file')
 if p.stat().st_size>MAX_SNAPSHOT:raise ValueError('HTML exceeds 5 MB limit')
 if source_url:
  u=urlsplit(source_url)
  if u.scheme!='https' or (u.hostname or '').lower() not in ('facebook.com','www.facebook.com','m.facebook.com') or u.username or u.password:
   raise ValueError('Source URL must be a direct HTTPS facebook.com URL')
 parsed=Metadata();parsed.feed(p.read_text(encoding='utf-8',errors='replace'))
 data={'mode':'USER-SAVED BROWSER HTML / NOT LIVE','source_url':source_url or None,
 'checked_utc':datetime.now(timezone.utc).isoformat(),'file_sha256':hashlib.sha256(p.read_bytes()).hexdigest(),
 'file_name':p.name,'html_title':parsed.title.strip()[:500], 'metadata':parsed.meta,
 'posts':[], 'post_count':0, 'content_verified':False,
 'warning':'HTML metadata is a lead, not authenticated Facebook posts; no cookies, posts, friends or comments collected.'}
 return data

def save_snapshot(result,root):
 root=Path(root);root.mkdir(parents=True,exist_ok=True,mode=0o700)
 import uuid
 dest=root/('snapshot-'+datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')+'-'+uuid.uuid4().hex[:8]+'.json')
 with dest.open('x',encoding='utf-8') as f:json.dump(result,f,indent=2,ensure_ascii=False)
 dest.chmod(0o600);return dest


def local_source_status(root):
 """Read-only summary of known local records; never claims that HTML/HEAD verified a post."""
 root=Path(root)
 kinds=(('SourceChecks','source-check-*.json','HTTP CHECK ONLY'),('SourceSnapshots','snapshot-*.json','SAVED HTML METADATA'),('PostReports','posts.json','IMPORTED POST REPORT'))
 print('\n◆ NIGHTGLASS // SOURCE STATUS · LOCAL RESEARCH')
 print('NETWORK: OFF · PRIVATE FILES: READ ONLY · FACEBOOK CONTENT: NOT VERIFIED BY CHECKS')
 for folder,pattern,label in kinds:
  where=root/folder
  found=sorted((p for p in where.rglob(pattern) if p.is_file() and not p.is_symlink()),key=lambda p:p.stat().st_mtime,reverse=True) if where.is_dir() else []
  print(f'{label}: {len(found)} saved record(s)')
  if not found:continue
  item=found[0]
  try:
   if item.stat().st_size>5_000_000:raise ValueError('Oversized report')
   value=json.loads(item.read_text(encoding='utf-8'))
   if not isinstance(value,dict):raise ValueError('Unexpected format')
   if folder=='SourceChecks':
    print('  Latest HTTP status:',value.get('status_code','UNKNOWN'),'· Content collected:',value.get('content_collected',False))
   elif folder=='SourceSnapshots':
    print('  Latest HTML title available:',bool(value.get('html_title')),'· Post records:',value.get('post_count',0))
   else:print('  Latest imported post count:',value.get('retained_count','UNKNOWN'))
  except (OSError,ValueError,UnicodeError,json.JSONDecodeError):print('  Latest report unreadable; originals untouched')
 print('TIP: A reachable URL or saved HTML does not verify Facebook posts.')
 return 0

def interactive(root):
 print('\n◆ NIGHTGLASS // INDEPENDENT SOURCE ENGINE · MODULE 17')
 print('1 · Import permitted post CSV/JSON/JSONL')
 print('2 · Inspect browser-saved public Page HTML (metadata only)')
 print('3 · Run fictional post demo (no filename)')
 print('4 · Source status / saved local checks (read only)')
 print('5 · Photo Post Fusion / authorized local captions and comments')
 print('6 · Page Research Fusion / saved Page + permitted post export')
 print('0 · Return')
 choice=input('SOURCE ❯ ').strip()
 try:
  if choice in ('0',''):return 0
  if choice=='4':return local_source_status(root)
  if choice=='5':return photo_fusion(root)
  if choice=='6':return page_fusion(root)
  if choice=='3':
   path=Path(__file__).parent/'examples'/'fictional_posts.csv';kw=''
  elif choice=='1':
   raw=input('Local post export path: ').strip()
   if not raw:return 0
   path=Path(raw);kw=input('Keyword (Enter for all): ').strip()
  elif choice=='2':
   raw=input('Browser-saved HTML file path: ').strip()
   if not raw:return 0
   url=input('Optional original public Facebook URL (Enter skips): ').strip()
   result=analyze_snapshot(raw,url)
   print('STATUS: SAVED HTML / UNVERIFIED · NO NETWORK')
   print('TITLE:',result['html_title'] or 'NOT FOUND')
   print('META:', ', '.join(result['metadata']) or 'NONE')
   print('POST RECORDS: 0 · HTML metadata is not post collection')
   print('SAVED:',save_snapshot(result,root/'SourceSnapshots'))
   return 0
  else:print('Choose 1, 2, 3, 4, 5, 6, or 0');return 0
  result=analyze_export(path,kw)
  print('STATUS: USER-SUPPLIED IMPORT / NOT LIVE')
  print('INPUT:',result['input_count'],'RETAINED:',result['retained_count'],'DUPLICATES:',result['duplicates_removed'])
  for i,post in enumerate(result['posts'][:100],1):
   print(f"[{i:03}] {post['date']}  {post['text'][:240]}\n      SOURCE: {post['url'] or 'NO URL IN EXPORT'}")
  folder=save_private(result,root/'PostReports')
  print('SAVED:',folder/'posts.json')
  return 0
 except (ValueError,OSError,UnicodeError,json.JSONDecodeError) as e:
  print('SOURCE ENGINE STOPPED:',e);return 2
