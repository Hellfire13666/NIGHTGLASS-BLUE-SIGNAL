"""NIGHTGLASS local reply trees. No network access. No hidden collection."""
import json,re
from pathlib import Path

def safe(value, limit=420):
    return re.sub(r"[\x00-\x1f\x7f\x1b\u202e\u202d\u2066-\u2069]", " ", str(value or ""))[:limit]

def load(path):
    obj=json.loads(Path(path).read_text(encoding="utf-8"))
    if not isinstance(obj,dict) or not isinstance(obj.get("records"),list) or not all(isinstance(x,dict) for x in obj["records"]):
        raise ValueError("Invalid local NIGHTGLASS report")
    return obj["records"]

def make_tree(records,term=""):
    indexed={}; children={}; roots=[]; orphan=[]
    for n,r in enumerate(records):
        key=str(r.get("id") or f"unidentified-{n}")
        if key in indexed:key=f"{key}#duplicate-{n}"
        indexed[key]=r
    for key,r in indexed.items():
        pid=str(r.get("parent_id") or "")
        if not pid:roots.append(key)
        elif pid==key or pid not in indexed:orphan.append(key)
        else:children.setdefault(pid,[]).append(key)
    result=[]; visited=set()
    def visit(key,depth,root,ancestors):
        if key in visited:return
        visited.add(key);result.append({'key':key,'record':indexed[key],'depth':min(depth,12),'root':root,'orphan':key in orphan,'child_count':len(children.get(key,[])),'cycle':key in ancestors})
        for k in children.get(key,[]):
            if k not in ancestors:visit(k,depth+1,root,ancestors|{key})
    for key in roots:visit(key,0,key,set())
    for key in orphan:visit(key,0,key,set())
    for key in indexed:visit(key,0,key,set())
    if term.strip():
        needles=term.casefold().strip();hits={x['key'] for x in result if needles in (str(x['record'].get('text',''))+' '+str(x['record'].get('author',''))).casefold()}
        keep=set(hits)
        for key in list(hits):
            seen=set()
            while key in indexed and key not in seen:
                seen.add(key);parent=str(indexed[key].get('parent_id') or '')
                if parent not in indexed:break
                keep.add(parent);key=parent
        result=[x for x in result if x['key'] in keep]
    return result

def describe(nodes,index,term=""):
    if not nodes:return 'No matching comments.'
    node=nodes[index];r=node['record'];parent=str(r.get('parent_id') or '')
    label='ORPHAN REPLY' if node['orphan'] else 'REPLY' if parent else 'COMMENT'
    prefix='  '*min(node['depth'],8)
    lines=[f"{index+1}/{len(nodes)}  {prefix}{label}",f"Author: {safe(r.get('author'))}",f"Date: {safe(r.get('created_at'))}",f"Source: {safe(r.get('source'))} | IMPORTED / NOT LIVE",f"Parent ID: {safe(parent) or 'NONE'}",f"Direct replies: {node['child_count']}",f"Text: {safe(r.get('text'))}"]
    if node['orphan']:lines.append('Notice: Parent not present in this report; no relationship inferred.')
    if term:lines.append('Filter: '+safe(term,120))
    return '\n'.join(lines)

def explore(path, input_fn=input, output_fn=print):
    try:records=load(path)
    except (OSError,ValueError,TypeError) as exc:
        output_fn('Cannot read local report: '+safe(exc));return 1
    term='';cursor=0
    while True:
        nodes=make_tree(records,term);cursor=min(cursor,max(0,len(nodes)-1))
        output_fn('\n◆ THREAD FUSION · LOCAL REPORT · NOT LIVE FACEBOOK')
        output_fn(describe(nodes,cursor,term))
        output_fn('[N/P] Next/Previous  [R] First direct reply  [U] Parent  [T] Tree  [/] Filter  [C] Clear  [Q] Return')
        try:cmd=input_fn('FUSION ❯ ').strip().lower()
        except (EOFError,KeyboardInterrupt):return 0
        if cmd in ('q','00','exit'):return 0
        if cmd in ('n',''):cursor=min(cursor+1,max(0,len(nodes)-1))
        elif cmd=='p':cursor=max(cursor-1,0)
        elif cmd=='/':
            try:term=input_fn('Name / keyword filter: ').strip()[:120];cursor=0
            except (EOFError,KeyboardInterrupt):return 0
        elif cmd=='c':term='';cursor=0
        elif cmd=='t':
            for i,node in enumerate(nodes):
                kind='↳' if node['record'].get('parent_id') else '◆'
                output_fn(f"{i+1:>3} {'  '*min(node['depth'],8)}{kind} {safe(node['record'].get('author'),36)} · {safe(node['record'].get('id'),32)}" + (' [ORPHAN]' if node['orphan'] else ''))
        elif cmd in ('u','r') and nodes:
            r=nodes[cursor]['record'];pid=str(r.get('parent_id') or '');key=nodes[cursor]['key']
            wanted=(pid if cmd=='u' else next((x['key'] for x in nodes if str(x['record'].get('parent_id') or '')==key),None))
            new=next((i for i,x in enumerate(nodes) if x['key']==wanted),None)
            if new is None:output_fn('No accessible '+('parent' if cmd=='u' else 'direct reply')+' in this view.')
            else:cursor=new
    return 0
