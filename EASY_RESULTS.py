#!/usr/bin/env python3
"""NIGHTGLASS offline menu-driven result browser. Never fetches network resources."""
from pathlib import Path
import json, csv, textwrap
from REPORT_DECK import reports, TYPES
ROOT=Path(__file__).resolve().parent

def records(kind,path):
    data=json.loads(path.read_text(encoding="utf-8"))
    if kind=="fusion": return data.get("posts",[])
    if kind=="comments": return data.get("records",data.get("comments",[]))
    if kind=="posts": return data.get("posts",[])
    return [data]

def index():
    return reports('all')

def show_report(kind,path,limit=100):
    data=json.loads(path.read_text(encoding="utf-8"))
    print("\n◆ BLACKGLASS // SAVED RESULT")
    print("KIND:",kind.upper(),"| FILE:",path.relative_to(ROOT))
    print("SOURCE: LOCAL SAVED REPORT | NOT LIVE COLLECTION")
    if kind=="source":
        for field in ('url','checked_utc','status_code','retrieval','content_collected','note'):
            if field in data:print(field.upper()+':',data[field])
        return
    entries=records(kind,path)
    print("RECORDS:",len(entries),"| DISPLAY LIMIT:",limit)
    for n,item in enumerate(entries[:limit],1):
        if not isinstance(item,dict):continue
        headline=item.get('text',item.get('message',''))
        print(f"[{n:03}] {item.get('date',item.get('created_time',''))} | {item.get('author',item.get('name',''))}")
        for line in textwrap.wrap(str(headline),width=90)[:6]:print('  '+line)
        if item.get('url'):print('  LINK:',item['url'])
    print('End of saved local result. Report unchanged.')

def interactive():
    while True:
        entries=index()
        print('\n◆ NIGHTGLASS // EASY RESULTS BROWSER')
        print('LOCAL FILES ONLY · REPORTS NOT AUTHENTICATED AS FACEBOOK CONTENT')
        print('  1  VIEW LATEST RESULT')
        print('  2  CHOOSE SAVED RESULT')
        print('  3  SHOW LATEST CSV')
        print('  0  BACK TO COMMAND CENTER')
        try:choice=input('RESULTS ❯ ').strip()
        except (EOFError,KeyboardInterrupt):print();return 0
        if choice=='0':return 0
        if not entries:print('No reports in this version. Choose 20 to create a fictional demo.');continue
        if choice=='1':
            kind,path=entries[0]
            try:show_report(kind,path)
            except (OSError,ValueError,TypeError) as exc:print('Unable to read report:',exc)
        elif choice=='2':
            for n,(kind,path) in enumerate(entries[:25],1):print(f' {n:2} {kind.upper():9} {path.relative_to(ROOT)}')
            try:chosen=int(input('REPORT NUMBER (0 cancels) ❯ ').strip())
            except (ValueError,EOFError):continue
            if 1<=chosen<=min(25,len(entries)):
                kind,path=entries[chosen-1]
                try:show_report(kind,path)
                except (OSError,ValueError,TypeError) as exc:print('Unable to read report:',exc)
        elif choice=='3':
            selected=next(((kind,path) for kind,path in entries if TYPES[kind][2] and (path.parent/TYPES[kind][2]).is_file()),None)
            if not selected:print('No CSV counterpart found.');continue
            kind,path=selected;csvpath=path.parent/TYPES[kind][2]
            print('CSV:',csvpath.relative_to(ROOT))
            try:
                with csvpath.open(newline='',encoding='utf-8-sig') as handle:
                    for n,row in enumerate(csv.reader(handle)):
                        if n>=21:print('Only first 20 rows shown.');break
                        print(' | '.join(row)[:260])
            except (OSError,UnicodeError,csv.Error) as exc:print('Cannot read CSV:',exc)
        else:print('Choose 1, 2, 3 or 0.')

if __name__=='__main__':interactive()
