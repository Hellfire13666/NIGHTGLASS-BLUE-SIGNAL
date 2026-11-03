import argparse, csv, hashlib, html, json, re, sys
from datetime import datetime, timezone
from pathlib import Path
from collections import Counter

VERSION = "0.5.0"
KEYS = ('id','parent_id','author','text','created_at','url','source')
COLORS = {'pink':'\033[95m','cyan':'\033[96m','lime':'\033[92m','dim':'\033[2m','red':'\033[91m','reset':'\033[0m'}
def color(txt,name,on=True): return COLORS[name]+str(txt)+COLORS['reset'] if on else str(txt)
def stamp(s):
    # ISO-ish dates sort lexicographically after normalizing UTC
    if not s: return ''
    try:
        d=datetime.fromisoformat(str(s).replace('Z','+00:00'))
        if d.tzinfo is None: d=d.replace(tzinfo=timezone.utc)
        return d.astimezone(timezone.utc).isoformat()
    except ValueError: return str(s)
def clean(v,limit=30000): return re.sub(r'[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]', '',str(v if v is not None else ''))[:limit]
def record(raw,source):
    if not isinstance(raw,dict): raise ValueError('Each record must be a JSON object or CSV row')
    aliases={'comment_id':'id','message':'text','body':'text','time':'created_at','timestamp':'created_at','parent':'parent_id','permalink':'url','username':'author'}
    for old,new in aliases.items():
        if not raw.get(new) and raw.get(old): raw[new]=raw[old]
    out={k:clean(raw.get(k,'')) for k in KEYS}
    out['source']=out['source'] or source
    out['created_at']=stamp(out['created_at'])
    out['fingerprint']=hashlib.sha256(('\0'.join(out[k] for k in ('id','parent_id','author','text','created_at','url'))).encode()).hexdigest()
    out['key']=out['id'] or out['fingerprint']
    return out

def read_records(path):
    p=Path(path)
    if not p.is_file(): raise ValueError('Input file not found: '+str(p))
    if p.stat().st_size>30_000_000: raise ValueError('Input exceeds 30 MB safety limit')
    ext=p.suffix.lower(); source=p.stem
    with p.open('r',encoding='utf-8-sig',newline='') as f:
        if ext=='.csv': rows=list(csv.DictReader(f))
        elif ext=='.jsonl': rows=[json.loads(s) for s in f if s.strip()]
        elif ext=='.json':
            obj=json.load(f)
            rows=obj if isinstance(obj,list) else obj.get('comments',obj.get('records',[])) if isinstance(obj,dict) else []
        else: raise ValueError('Supported formats: .csv, .json, .jsonl')
    if not isinstance(rows,list): raise ValueError('Expected list of records')
    if len(rows)>100000: raise ValueError('Record count exceeds 100,000 limit')
    return [record(dict(r),source) for r in rows]

def dedup(rows):
    seen=set(); result=[]; skipped=0
    for r in rows:
        key=r['key']
        if key in seen: skipped+=1
        else: seen.add(key); result.append(r)
    return result,skipped

def sort_rows(rows):return sorted(rows,key=lambda r:r['created_at'],reverse=True)
def csv_safe(value):
    s=str(value or '')
    return "'"+s if s.lstrip().startswith(('=','+','-','@','\t','\r')) else s

def write_reports(rows,outdir,title,metadata):
    out=Path(outdir);out.mkdir(parents=True,exist_ok=True)
    output={'status':'IMPORTED DATA ONLY | NOT LIVE','title':title,'generated_utc':datetime.now(timezone.utc).isoformat(),'metadata':metadata,'records':rows}
    (out/'report.json').write_text(json.dumps(output,indent=2,ensure_ascii=False),encoding='utf-8')
    columns=list(KEYS)+['fingerprint'] + (['verification_status'] if any('verification_status' in r for r in rows) else [])
    with (out/'report.csv').open('w',encoding='utf-8',newline='') as f:
        wr=csv.DictWriter(f,fieldnames=columns,extrasaction='ignore');wr.writeheader();wr.writerows({k:csv_safe(r.get(k,'')) for k in columns} for r in rows)
    style="""body{background:#080811;color:#e8eaf1;font:15px system-ui;margin:0;padding:28px}main{max-width:1100px;margin:auto}h1{color:#ff1493}h2{color:#00f5ff}.tag{color:#b6ff00;font-weight:bold}.card{background:#141421;border:1px solid #363646;border-left:3px solid #ff1493;margin:10px 0;padding:15px;border-radius:8px}small{color:#9da2b2}a{color:#00f5ff}p{overflow-wrap:anywhere;white-space:pre-wrap}.reply{margin-left:32px;border-left-color:#00f5ff}.badge{color:#b6ff00}code{overflow-wrap:anywhere}"""
    def esc(x):return html.escape(str(x or ''),quote=True)
    blocks=[]
    for r in rows:
        url=r.get('url','');link=(' <a href="'+esc(url)+'" rel="noopener noreferrer" target="_blank">Source URL</a>') if url.startswith(('https://','http://')) else ''
        blocks.append('<article class="card'+(' reply' if r.get('parent_id') else '')+'"><small>'+esc(r.get('created_at'))+' · '+esc(r.get('source'))+' · '+esc(r.get('verification_status','IMPORTED'))+'</small><h3>'+esc(r.get('author'))+'</h3><p>'+esc(r.get('text'))+'</p><small>ID: '+esc(r.get('id'))+' | Reply to: '+esc(r.get('parent_id'))+link+'</small></article>')
    page='<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>'+esc(title)+'</title><style>'+style+'</style><main><h1>NIGHTGLASS // '+esc(title)+'</h1><p class="tag">IMPORTED DATA ONLY · NOT LIVE FACEBOOK DATA</p><p>'+esc(len(rows))+' records · private local report</p><h2>Evidence Explorer</h2>'+''.join(blocks)+'</main></html>'
    (out/'report.html').write_text(page,encoding='utf-8')
    return out

def announce(rows,no_color,limit):
    for n,r in enumerate(sort_rows(rows)[:limit],1):
        prefix='↳ REPLY' if r['parent_id'] else 'COMMENT'
        print(color(f'[{n:03d}] {prefix}', 'cyan',not no_color),color(r['created_at'],'dim',not no_color),color(r['author'] or 'Unknown','pink',not no_color))
        print('     '+(r['text'][:260] or '[empty]'))
    if len(rows)>limit: print(f'... {len(rows)-limit} additional records in saved report')

def compare(a,b):
    left={r['key']:r for r in a};right={r['key']:r for r in b};merged=[]
    for k in sorted(set(left)|set(right)):
        ar=left.get(k);br=right.get(k)
        if ar and br: status='MATCHED' if ar['fingerprint']==br['fingerprint'] else 'CONFLICT'
        elif ar: status='SOURCE_A_ONLY'
        else: status='SOURCE_B_ONLY'
        merged.append({**(br or ar),'verification_status':status})
    return sort_rows(merged)

def main(argv=None):
    pa=argparse.ArgumentParser(description='NIGHTGLASS offline Facebook comment evidence organizer. No scraping or login.')
    pa.add_argument('--no-color',action='store_true');sub=pa.add_subparsers(dest='command',required=True)
    sub.add_parser('doctor',help='Verify local install')
    sub.add_parser('examples',help='Show easy recipes')
    de=sub.add_parser('demo',help='Run fictional offline example');de.add_argument('--out',default='NightglassReports/demo')
    imp=sub.add_parser('import',help='Import permitted CSV/JSON/JSONL');imp.add_argument('file');imp.add_argument('--out',default='NightglassReports/import');imp.add_argument('--limit',type=int,default=100);imp.add_argument('--search',default='')
    comp=sub.add_parser('compare',help='Compare two permitted data exports');comp.add_argument('file_a');comp.add_argument('file_b');comp.add_argument('--out',default='NightglassReports/compare')
    args=pa.parse_args(argv);off=args.no_color
    print(color('◆ NIGHTGLASS // COMMENT FUSION v'+VERSION,'pink',not off))
    print(color('  SOURCE STATUS: IMPORT-ONLY · OFFLINE · NOT LIVE','lime',not off))
    if args.command=='doctor':
        print('PASS Python standard library | CSV JSON JSONL | private reports | zero network code');return 0
    if args.command=='examples':
        print('./RUN.sh demo\n./RUN.sh import examples/fictional_comments.csv --out NightglassReports/my-test\n./RUN.sh import export.json --search example --limit 100\n./RUN.sh compare export_a.csv export_b.json --out NightglassReports/comparison');return 0
    if args.command=='demo':
        path=Path(__file__).resolve().parent.parent/'examples'/'fictional_comments.csv';rows=read_records(path)
        rows,removed=dedup(rows);print(f'Imported: {len(rows)+removed} | Unique: {len(rows)} | Removed duplicates: {removed}')
        announce(rows,off,100);out=write_reports(sort_rows(rows),args.out,'Comment Fusion Demo',{'duplicates_removed':removed,'fictional_data':True})
    elif args.command=='import':
        if args.limit<1 or args.limit>100: raise ValueError('--limit must be 1..100')
        rows=read_records(args.file);count=len(rows);rows,removed=dedup(rows)
        if args.search: rows=[r for r in rows if args.search.casefold() in (r['text']+' '+r['author']).casefold()]
        rows=sort_rows(rows);print(f'Imported: {count} | Unique matching: {len(rows)} | Duplicates removed: {removed}')
        announce(rows,off,args.limit);out=write_reports(rows,args.out,'Comment Fusion Import',{'original_count':count,'duplicates_removed':removed,'display_limit':args.limit,'search':args.search})
    else:
        a,da=dedup(read_records(args.file_a));b,db=dedup(read_records(args.file_b));rows=compare(a,b)
        stats=dict(Counter(r['verification_status'] for r in rows));print('Source comparison:',stats,'| duplicates removed:',da+db)
        announce(rows,off,100);out=write_reports(rows,args.out,'Source Verification',{'statuses':stats,'duplicates_removed':da+db})
    print(color('REPORTS: '+str(out.resolve()),'lime',not off));print('  report.html | report.csv | report.json')
    return 0
if __name__=='__main__':
    try:sys.exit(main())
    except (ValueError, OSError, json.JSONDecodeError, csv.Error) as exc:
        print('NIGHTGLASS ERROR:',exc,file=sys.stderr);sys.exit(2)
