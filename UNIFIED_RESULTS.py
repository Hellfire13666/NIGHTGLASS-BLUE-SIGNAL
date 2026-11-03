#!/usr/bin/env python3
"""Read-only, opt-in cross-version report browser. No network, no copying or mutation."""
from pathlib import Path
import csv, json, os, re, textwrap

REPORT_PATHS = {
    'fusion': ('FusionReports', 'fusion.json', 'fusion.csv'),
    'comments': ('NightglassReports', 'report.json', 'report.csv'),
    'posts': ('PostReports', 'posts.json', 'posts.csv'),
    'source': ('SourceChecks', None, None),
}
VERSION_PATTERN = re.compile(r'^NIGHTGLASS-(?:BLACKGLASS|COMMAND-CENTER|COMMENT-FUSION|INTERIOR)[A-Za-z0-9._-]*$')

def installations(home=None):
    home = Path(home) if home is not None else Path.home()
    bases = (home / 'Downloads', home / 'PhantomLabsLaunchers')
    found=[]
    for base in bases:
        if not base.is_dir():continue
        for folder in base.iterdir():
            if not folder.is_dir() or folder.is_symlink() or not VERSION_PATTERN.fullmatch(folder.name):continue
            if (folder / 'COMMAND_CENTER.py').is_file() or (folder / 'RUN.sh').is_file():
                found.append(folder)
    return sorted(found,key=lambda x:x.name)

def discover(home=None):
    entries=[]
    for folder in installations(home):
        for kind,(subdir,filename,csvfile) in REPORT_PATHS.items():
            root=folder/subdir
            if not root.is_dir() or root.is_symlink():continue
            try:
                paths=root.glob('source-check-*.json') if kind=='source' else root.glob('*/'+filename)
                for p in paths:
                    if p.is_symlink() or not p.is_file() or p.stat().st_size>8*1024*1024:continue
                    if any(parent.is_symlink() for parent in p.parents if parent!=folder and parent!=folder.parent):continue
                    entries.append({'kind':kind,'path':p,'version':folder.name,'time':p.stat().st_mtime,'csv':p.parent/csvfile if csvfile else None})
            except OSError:continue
    return sorted(entries,key=lambda x:x['time'],reverse=True)

def preview(entry,limit=20):
    path=entry['path']
    data=json.loads(path.read_text(encoding='utf-8'))
    if not isinstance(data,dict):raise ValueError('Unexpected JSON report format')
    print('\n◆ NIGHTGLASS // ARCHIVED RESULT (READ ONLY)')
    print('VERSION:',entry['version'],'| KIND:',entry['kind'].upper())
    print('FILE:',path.name,'| SOURCE: SAVED LOCAL REPORT; NOT LIVE RETRIEVAL')
    if entry['kind']=='source':
        for field in ('url','checked_utc','status_code','retrieval','content_collected','note'):
            if field in data:print(field.upper()+':',str(data[field])[:300])
        return
    rows=data.get('posts',data.get('records',data.get('comments',[])))
    if not isinstance(rows,list):raise ValueError('Unexpected record structure')
    print('RECORDS:',len(rows),'| DISPLAY:',min(limit,len(rows)))
    for n,r in enumerate(rows[:limit],1):
        if not isinstance(r,dict):continue
        print('[%03d]'%n,str(r.get('date',r.get('created_time','')))[:50],str(r.get('author',r.get('name','')))[:70])
        print('  '+str(r.get('text',r.get('message','')))[:280].replace('\n',' '))
        if r.get('url'):print('  LINK:',str(r['url'])[:240])
    print('Original report unchanged.')

def interactive(home=None):
    while True:
        entries=discover(home)
        print('\n◆ NIGHTGLASS // UNIFIED RESULTS · READ ONLY')
        print('Found',len(entries),'saved reports across',len(installations(home)),'local installations')
        print('[1] Read newest report  [2] Choose report  [3] Show report locations  [0] Return')
        try:choice=input('ARCHIVE ❯ ').strip()
        except (EOFError,KeyboardInterrupt):print();return 0
        if choice=='0':return 0
        if not entries:print('No reports found in the known NIGHTGLASS folders. Originals untouched.');continue
        if choice=='1':selection=entries[0]
        elif choice=='2':
            for i,e in enumerate(entries[:30],1):print(f'[{i:02}] {e["version"]} | {e["kind"]} | {e["path"].name}')
            try:num=int(input('REPORT NUMBER (0 cancels) ❯ ').strip())
            except (ValueError,EOFError):continue
            if not 1<=num<=min(30,len(entries)):continue
            selection=entries[num-1]
        elif choice=='3':
            for e in entries[:40]:print(e['version'],'/',e['kind'],'/',e['path'].relative_to(e['path'].parents[2]) if len(e['path'].parents)>2 else e['path'].name)
            continue
        else:print('Choose 1, 2, 3, or 0.');continue
        try:preview(selection)
        except (OSError,ValueError,UnicodeError) as exc:print('Unable to view report:',exc)

if __name__=='__main__':interactive()
