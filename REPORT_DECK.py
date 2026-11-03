#!/usr/bin/env python3
"""Read-only report navigation for the local NIGHTGLASS collection."""
from pathlib import Path
import argparse, csv, json, sys, webbrowser
ROOT=Path(__file__).resolve().parent
TYPES={'fusion':('FusionReports','fusion.json','fusion.csv'),'comments':('NightglassReports','report.json','report.csv'),'posts':('PostReports','posts.json','posts.csv'),'source':('SourceChecks','source-check-*.json',None)}

def reports(kind='all', source_dir=None):
    kinds=list(TYPES) if kind=='all' else [kind]
    found=[]
    for k in kinds:
        folder,j,c=TYPES[k]
        directory=(Path(source_dir).expanduser().resolve() if k=='source' and source_dir else ROOT/folder)
        if not directory.is_dir(): continue
        pattern=('**/'+j if '*' not in j else '**/'+j)
        for p in directory.glob(pattern):
            if p.is_file() and not p.is_symlink():found.append((k,p))
    return sorted(found,key=lambda v:(v[1].stat().st_mtime,str(v[1])),reverse=True)

def latest(kind,source_dir=None):
    entries=reports(kind,source_dir)
    return entries[0] if entries else None

def show(kind='fusion',mode='cat',source_dir=None,output=None):
    item=latest(kind,source_dir)
    if not item:
        print('No '+kind+' report found in this version. No files changed.');return 1
    typ,path=item
    if mode=='csv':
        _,jn,cn=TYPES[typ]
        if cn is None:
            print('CSV not available for source checks.');return 1
        path=path.parent/cn
        if not path.is_file():print('CSV counterpart unavailable:',path.name);return 1
    if mode=='open':
        if typ=='comments' and (path.parent/'report.html').is_file():path=path.parent/'report.html'
        print('OPEN:',path)
        webbrowser.open(path.resolve().as_uri());return 0
    if mode=='cat':
        try:print(json.dumps(json.loads(path.read_text(encoding='utf-8')),indent=2,ensure_ascii=False))
        except (OSError,ValueError) as exc:print('Report could not be read:',exc);return 1
    elif mode=='csv':
        try:
            with path.open(newline='',encoding='utf-8-sig') as f:
                for row in csv.reader(f):print(' | '.join(row))
        except (OSError,csv.Error) as exc:print('CSV could not be read:',exc);return 1
    return 0

def main(argv=None):
    parser=argparse.ArgumentParser(description='NIGHTGLASS safe report shortcuts')
    parser.add_argument('command',choices=['cat','csv','reports','open'])
    parser.add_argument('--kind',choices=list(TYPES)+['all'],default='fusion')
    parser.add_argument('--source-check-dir',help='Optional explicit older SourceChecks folder (read-only)')
    args=parser.parse_args(argv)
    if args.command=='reports':
        found=reports(args.kind,args.source_check_dir)
        if not found:print('No reports found in selected locations.');return 0
        for k,p in found:print(k.upper(),p.relative_to(ROOT) if p.is_relative_to(ROOT) else p)
        return 0
    if args.kind=='all':parser.error('Select a report kind for cat, csv or open')
    return show(args.kind,args.command,args.source_check_dir)
if __name__=='__main__':sys.exit(main())
