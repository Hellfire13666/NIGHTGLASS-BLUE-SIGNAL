
"""Offline research over saved NIGHTGLASS Blue Signal text reports."""
from pathlib import Path
import re, json, html, difflib
from datetime import datetime, timezone
from urllib.parse import urlsplit

ROOT=Path.home()/'Documents'/'NIGHTGLASS-VAULT'/'blue-signal-runs'
EXPORTED=ROOT/'exports'
ANSI=re.compile(r'\x1b\[[0-9;]*[A-Za-z]')
URL=re.compile(r'https://[^\s<>]+')
SENSITIVE=re.compile(r'(?i)(access_token|token|cookie|session|password|secret)=([^\s&]+)')
def reports(root=ROOT):
    return sorted((p for p in root.glob('run-*.txt') if p.is_file() and not p.is_symlink()),key=lambda p:p.name,reverse=True) if root.exists() else []
def safe(line):
    return SENSITIVE.sub(r'\1=[REDACTED]',ANSI.sub('',line))
def read_report(path):
    # Only local user-selected reports in the vault, never arbitrary paths.
    return safe(path.read_text(encoding='utf-8',errors='replace')[:2_000_000])
def summarize(text):
    counts={}
    for name in ('Discovered references','Unique URLs','Possible post links','Facebook Page links','Media references','Distinct media files','Site resources','Other links'):
        m=re.search(r'^\s*'+re.escape(name)+r'\s*:\s*(\d+)',text,re.M)
        if m: counts[name]=int(m.group(1))
    source=re.search(r'^SOURCE:\s*(https://\S+)',text,re.M)
    links=set()
    for line in text.splitlines():
        if re.match(r'^\s*\[\d{3}\]',line):
            for url in URL.findall(line):
                url=url.rstrip('),.;')
                if '…' not in url and '[REDACTED]' not in url:
                    p=urlsplit(url)
                    if p.scheme=='https':links.add(url)
    return {'source':source.group(1) if source else None,'counts':counts,'visible_complete_links':sorted(links),
            'notice':'Complete links visible in saved text only; abbreviated media URLs cannot be compared accurately.'}
def choose(items):
    for i,p in enumerate(items[:40],1):print(f'[{i}] {p.name}')
    value=input('Report number (Enter to cancel) > ').strip()
    return items[int(value)-1] if value.isdecimal() and 1<=int(value)<=min(40,len(items)) else None
def search():
    items=reports()
    if not items:return print('[VAULT] No saved Blue Signal scans.')
    term=input('Search saved reports for text > ').strip().casefold()
    if not term:return
    matched=0
    for file in items:
        lines=[(i,line) for i,line in enumerate(read_report(file).splitlines(),1) if term in line.casefold()]
        if lines:
            print(f'\n[VAULT] {file.name} | {len(lines)} line matches')
            for i,line in lines[:8]:print(f'  {i}: {line[:210]}')
            matched+=1
    print(f'[SEARCH] reports_matched={matched} reports_examined={len(items)} | offline')
def compare():
    items=reports()
    if len(items)<2:return print('[VAULT] Two saved scans required.')
    print('Select older/base scan:');a=choose(items)
    if not a:return
    print('Select comparison scan:');b=choose(items)
    if not b:return
    sa=summarize(read_report(a)); sb=summarize(read_report(b))
    x=set(sa['visible_complete_links']);y=set(sb['visible_complete_links'])
    print(f'[COMPARE] {a.name} vs {b.name}')
    for key in sorted(set(sa['counts'])|set(sb['counts'])):
        old=sa['counts'].get(key,0);new=sb['counts'].get(key,0)
        print(f'  {key}: {old} -> {new} ({new-old:+d})')
    print(f'  Visible complete URLs: added={len(y-x)} removed={len(x-y)} unchanged={len(x&y)}')
    for url in sorted(y-x)[:25]:print('  +',url)
    for url in sorted(x-y)[:25]:print('  -',url)
    print('[NOTE] Differences are public source snapshots, not account activity proof; shortened media URLs excluded.')
def export():
    items=reports()
    if not items:return print('[VAULT] No saved scans.')
    selected=choose(items)
    if not selected:return
    data=summarize(read_report(selected))
    data['scan_file']=selected.name
    data['exported_at_utc']=datetime.now(timezone.utc).isoformat()
    EXPORTED.mkdir(parents=True,exist_ok=True,mode=0o700)
    json_path=EXPORTED/(selected.stem+'.summary.json')
    html_path=EXPORTED/(selected.stem+'.summary.html')
    if json_path.exists() or html_path.exists():
        return print('[VAULT] Export already exists. No overwrite.')
    json_path.write_text(json.dumps(data,indent=2,ensure_ascii=False),encoding='utf-8')
    rows=''.join('<tr><td>'+html.escape(k)+'</td><td>'+str(v)+'</td></tr>' for k,v in data['counts'].items())
    links=''.join('<li>'+html.escape(url)+'</li>' for url in data['visible_complete_links'])
    html_path.write_text('<!doctype html><html lang="en"><meta charset="utf-8"><title>NIGHTGLASS Summary</title><style>body{background:#071328;color:#cde8ff;font:16px sans-serif;max-width:850px;margin:3rem auto}h1{color:#55dfff}td{padding:9px;border-bottom:1px solid #2452a2}</style><h1>NIGHTGLASS // BLUE SIGNAL</h1><p>Offline saved-scan summary: '+html.escape(selected.name)+'</p><table>'+rows+'</table><h2>Complete visible URLs</h2><ul>'+links+'</ul><p>Abbreviated media URLs omitted. Public HTML, not authenticated posts.</p></html>',encoding='utf-8')
    json_path.chmod(0o600);html_path.chmod(0o600)
    print('[VAULT] Exported locally:',json_path.name, 'and',html_path.name)
def menu():
    print('\n\033[96mNIGHTGLASS // BLUE SIGNAL · INTEL VAULT\033[0m')
    print('[1] Search saved scans (offline)')
    print('[2] Compare two scan summaries (offline)')
    print('[3] Export summary as HTML and JSON')
    print('[4] List saved scans')
    print('[0] Original Report Vault')
    c=input('BLUE VAULT > ').strip()
    if c=='0':return None
    if c=='1':search()
    elif c=='2':compare()
    elif c=='3':export()
    elif c=='4':
        for p in reports()[:40]:print(' ',p.name)
    else:print('Unknown option')
    return 0
if __name__=='__main__':menu()
