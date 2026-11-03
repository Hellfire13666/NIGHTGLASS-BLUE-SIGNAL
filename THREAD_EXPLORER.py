"""Offline comment/reply explorer. Never requests network access."""
import json, re
from pathlib import Path

def load_report(path):
    file=Path(path)
    obj=json.loads(file.read_text(encoding='utf-8'))
    if not isinstance(obj,dict) or not isinstance(obj.get('records'),list):
        raise ValueError('Invalid local NIGHTGLASS report')
    if not all(isinstance(r,dict) for r in obj['records']):
        raise ValueError('Invalid record')
    return obj

def grouped(rows,filter_text=''):
    by_id={str(r.get('id','')):r for r in rows if r.get('id')}
    roots=[]; attached={}; orphan=[]
    for r in rows:
        parent=str(r.get('parent_id') or '')
        rid=str(r.get('id') or '')
        if parent and parent != rid and parent in by_id:
            attached.setdefault(parent,[]).append(r)
        elif parent:
            orphan.append(r)
        else:
            roots.append(r)
    # Build a flat hierarchy with a visited set to prevent loops or malicious deep nesting.
    ordered=[];seen=set()
    def walk(r,depth):
        rid=str(r.get('id') or id(r))
        if rid in seen:return
        seen.add(rid)
        ordered.append((depth,r))
        for child in attached.get(str(r.get('id','')),[]):
            walk(child,min(depth+1,8))
    for r in roots+orphan:walk(r,0 if r in roots else 1)
    for r in rows:walk(r,0)
    term=filter_text.casefold().strip()
    if term:
        matches={str(r.get('id') or id(r)) for d,r in ordered if term in (str(r.get('author',''))+' '+str(r.get('text',''))).casefold()}
        # Also keep parents so replies retain context.
        wanted=set(matches)
        for d,r in ordered:
            if str(r.get('id') or id(r)) in matches:
                parent=str(r.get('parent_id') or '')
                for _ in range(16):
                    if not parent or parent not in by_id or parent in wanted:break
                    wanted.add(parent);parent=str(by_id[parent].get('parent_id') or '')
        ordered=[(d,r) for d,r in ordered if str(r.get('id') or id(r)) in wanted]
    return ordered

def clean(s,limit=420):
    return re.sub(r'[\x00-\x1f\x7f\x1b\u202e\u202d\u2066-\u2069]',' ',str(s or ''))[:limit]

def view(rows,index,term=''):
    if not rows:return 'No matching records.'
    depth,r=rows[index]
    prefix='  '*min(depth,5)
    data=[f'{index+1}/{len(rows)}  {prefix}{"↳ REPLY" if depth or r.get("parent_id") else "COMMENT"}',
          f'Author: {clean(r.get("author"))}', f'Date: {clean(r.get("created_at"))}',
          f'Source: {clean(r.get("source"))}  |  IMPORTED / NOT LIVE',
          f'Parent: {clean(r.get("parent_id")) or "NONE"}',
          f'Text: {clean(r.get("text"))}']
    if term:data.append('Filter: '+clean(term,80))
    return '\n'.join(data)

def interactive(path, input_fn=input, output_fn=print):
    try: doc=load_report(path)
    except (OSError,ValueError,json.JSONDecodeError) as exc:
        output_fn('Cannot open local report: '+clean(exc));return 1
    term=''; cursor=0
    while True:
        rows=grouped(doc['records'],term)
        if rows:cursor=min(cursor,len(rows)-1)
        output_fn('\n◆ COMMENT THREAD EXPLORER · LOCAL IMPORT / NOT LIVE')
        output_fn(view(rows,cursor,term))
        output_fn('[N] Next  [P] Previous  [/] Search  [C] Clear filter  [Q] Return')
        try: choice=input_fn('THREADS ❯ ').strip()
        except (EOFError,KeyboardInterrupt):output_fn('Explorer closed safely.');return 0
        if choice.lower() in ('q','00','exit'):return 0
        if choice.lower() in ('n','j',''):cursor=min(cursor+1,max(0,len(rows)-1))
        elif choice.lower() in ('p','k'):cursor=max(0,cursor-1)
        elif choice=='/':
            try: term=input_fn('Name / keyword filter: ').strip()[:120]
            except (EOFError,KeyboardInterrupt):return 0
            cursor=0
        elif choice.lower()=='c':term='';cursor=0
