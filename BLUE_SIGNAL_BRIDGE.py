"""NIGHTGLASS Master Fusion bridge: opt-in public-source scans, no credentials."""
from pathlib import Path
import subprocess
import sys

SCANNER = (Path.home() / 'Downloads' / 'NIGHTGLASS-BLUE-SIGNAL-v1.0.4' /
           'nightglass-fusion' / 'nightglass_linkfusion.py')
RECIPES = {
    '1': ('JediSecFB public link hunt', 'https://www.facebook.com/JediSecFB', 'posts,photos,reels,videos'),
    '2': ('Meta public link hunt', 'https://www.facebook.com/Meta', 'photos,posts,meta'),
}

import os
import re
from datetime import datetime, timezone
from urllib.parse import urlsplit

VAULT = Path.home() / 'Documents' / 'NIGHTGLASS-VAULT' / 'blue-signal-runs'

def _vault():
    VAULT.mkdir(parents=True, exist_ok=True, mode=0o700)
    return VAULT

def _reports():
    root = _vault()
    return sorted(root.glob('run-*.txt'), reverse=True)

def view_latest():
    reports = _reports()
    if not reports:
        print('[VAULT] No saved Blue Signal scans yet.'); return 0
    print('[VAULT] Latest saved scan:', reports[0].name)
    print(reports[0].read_text(encoding='utf-8', errors='replace'))
    return 0

def browse_reports():
    reports = _reports()
    if not reports:
        print('[VAULT] No saved Blue Signal scans yet.'); return 0
    for i, p in enumerate(reports[:30], 1):
        print(f'[{i}] {p.name}')
    choice = input('VIEW REPORT NUMBER (Enter to return) > ').strip()
    if not choice: return 0
    if not choice.isdecimal() or not 1 <= int(choice) <= min(30,len(reports)):
        print('[VAULT] Invalid selection.'); return 2
    print(reports[int(choice)-1].read_text(encoding='utf-8', errors='replace'))
    return 0

def _safe_display(line):
    # Terminal and local report receive the same cleaned source line.
    # Strip ANSI, control chars and high-risk URL query keys before saving.
    line = re.sub(r'\x1b\[[0-9;]*[A-Za-z]', '', line)
    line = ''.join(c for c in line if c == '\n' or (ord(c) >= 32 and ord(c) != 127))
    line = re.sub(r'(?i)(access_token|token|cookie|session|password|secret)=([^\s&]+)', r'\1=[REDACTED]', line)
    return line

def launch(url, terms):
    if not SCANNER.is_file():
        print('[BLUE SIGNAL] Scanner not found; extract verified v1.0.4 into Downloads first.')
        return 2
    if not urlsplit(url).hostname in {'facebook.com','www.facebook.com','m.facebook.com','mbasic.facebook.com','web.facebook.com'}:
        print('[SOURCE GUARD] Invalid public Facebook host.'); return 2
    root = _vault()
    stamp = datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S%fZ')
    path = root / f'run-{stamp}.txt'
    print('[BLUE SIGNAL] LIVE PRINT + PRIVATE VAULT SAVE | Public HTML only', flush=True)
    command = [sys.executable, '-u', str(SCANNER), url, '--check']
    if terms: command += ['--hunt',terms]
    fd = os.open(path, os.O_CREAT | os.O_EXCL | os.O_WRONLY, 0o600)
    rc=2
    with os.fdopen(fd,'w',encoding='utf-8') as report:
        report.write('NIGHTGLASS BLUE SIGNAL | Read-only public HTML scan\n')
        report.write('SOURCE: '+urlsplit(url)._replace(query='',fragment='').geturl()+'\n')
        try:
            proc = subprocess.Popen(command, cwd=str(SCANNER.parent), stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, bufsize=1)
            for line in proc.stdout:
                safe = _safe_display(line)
                print(safe,end='',flush=True)
                report.write(safe)
                report.flush()
            rc = proc.wait()
        except KeyboardInterrupt:
            proc.terminate()
            rc = 130
            print('\n[BLUE SIGNAL] User interrupted scan.')
        except OSError as exc:
            print('[BLUE SIGNAL] Could not run scanner:',type(exc).__name__)
        report.write(f'\nEXIT STATUS: {rc}\n')
    print('[VAULT] Saved local scan:',path.name)
    return rc

def recipe_deck():
    print('\n\033[96mNIGHTGLASS // BLUE SIGNAL · VERIFIED RECIPES\033[0m')
    for n, (name, _, _) in RECIPES.items(): print(f'[{n}] {name}')
    print('[3] View latest saved Blue Signal scan')
    print('[4] Browse saved Blue Signal scans')
    print('[0] Return to original recipes')
    choice=input('BLUE SIGNAL > ').strip()
    if choice=='3': return view_latest()
    if choice=='4': return browse_reports()
    if choice in RECIPES:
        _, url, terms=RECIPES[choice]
        if input('Run and privately save this public scan? [y/N] ').strip().lower()=='y':
            return launch(url,terms)
        print('Cancelled; no network request made.')
    return None

def research_desk():
    print('\n\033[96mNIGHTGLASS // BLUE SIGNAL · LINK RESEARCH\033[0m')
    print('[1] Inspect and save a public Facebook URL')
    print('[2] View latest saved Blue Signal scan')
    print('[3] Browse saved Blue Signal scans')
    print('[0] Return to original Research Desk')
    choice=input('BLUE SIGNAL > ').strip()
    if choice=='2':return view_latest()
    if choice=='3':return browse_reports()
    if choice!='1':return None
    url=input('Public Facebook HTTPS URL: ').strip()
    p=urlsplit(url)
    if p.scheme!='https' or p.hostname not in {'facebook.com','www.facebook.com','m.facebook.com','mbasic.facebook.com','web.facebook.com'} or p.username or p.password or p.port not in (None,443):
        print('[SOURCE GUARD] Only HTTPS public Facebook URLs. No request made.');return 2
    terms=input('Hunt terms (comma-separated; optional): ').strip()
    if input('Run and privately save this public scan? [y/N] ').strip().lower()!='y':
        print('Cancelled; no network request made.');return 0
    return launch(url,terms)
