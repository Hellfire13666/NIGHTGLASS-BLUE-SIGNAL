# BLUE SIGNAL VAULT INTEL v2.3.3
# BLUE SIGNAL MASTER FUSION 2.3.2
#!/usr/bin/env python3
"""BLACKGLASS: independent NIGHTGLASS 0.5 live local session panels, real offline engine."""
from pathlib import Path
import os, shutil, subprocess, sys, webbrowser, time, json
from datetime import datetime, timezone
from nightglass.__main__ import main as engine
from THREAD_EXPLORER import interactive as explore_threads
from SOURCE_BRIDGE import inspect_source, render_summary
from THREAD_FUSION import explore as explore_fusion
from RESEARCH_DESK import interactive as research_desk
from SOURCE_CHECK import interactive as source_check
from SOURCE_ENGINE import interactive as independent_source_engine
from PUBLIC_POST_FUSION import interactive as public_post_fusion
from REPORT_DECK import main as report_deck
from EASY_RESULTS import interactive as easy_results
from UNIFIED_RESULTS import interactive as unified_results
ROOT=Path(__file__).resolve().parent
PINK='\033[38;2;255;20;147m'; BLUE='\033[38;2;45;135;255m'; CYAN='\033[38;2;0;245;255m'; LIME='\033[38;2;182;255;0m'; PURPLE='\033[38;2;176;110;255m'; MUTED='\033[90m'; RESET='\033[0m'
COLOR=sys.stdout.isatty() and not os.environ.get('NO_COLOR')
def ink(s,t):return t+str(s)+RESET if COLOR else str(s)
def width():return max(26, min(110,shutil.get_terminal_size((88,24)).columns-2))
def edge(c=PINK):return ink('═'*width(),c)
ROWS=[('01','COMMENT FUSION','Fictional demo / genuine parser'),('02','IMPORT STATION','CSV / JSON / JSONL'),('03','SEARCH LENS','Local name and keyword filter'),('04','CROSS-REFERENCE','Compare two real exports'),('05','REPORT VAULT','Open local HTML report'),('06','RECIPE DECK','Copyable CLI examples'),('07','SYSTEM DOCTOR','Check local requirements'),('08','TEST SUITE','Run complete local tests')]
SELECTED='01'
BOOT_LINES=['Loading BLACKGLASS shell','Initializing offline modules','Reports vault ready','Transparent terminal preserved','Command center ready']
SCENES={'01':('◉ THREADS','Replies / dedup / comment evidence'), '02':('⇣ FILE RAIL','Local CSV · JSON · JSONL'), '03':('⌕ SEARCH SCAN','Local names and keyword filters'), '04':('◇ LINK MAP','Two supplied exports / comparison'), '05':('▤ EVIDENCE VAULT','Local HTML · CSV · JSON'), '06':('≡ RECIPES','Copy-paste local workflows'), '07':('✚ DIAGNOSTICS','Runtime health / zero network'), '08':('▦ VERIFICATION','Regression test suite')}

MODULE_NOTES={
 '01': ('COMMENT FUSION', 'Inspect fictional demo comments, thread replies and deduplication.', 'DEMO · FICTIONAL DATA'),
 '02': ('IMPORT STATION', 'Open a local CSV, JSON or JSONL export and create private reports.', 'LOCAL FILES ONLY'),
 '03': ('SEARCH LENS', 'Filter a local export by a supplied name or keyword.', 'LOCAL FILES ONLY'),
 '04': ('CROSS-REFERENCE', 'Compare two supplied exports without network requests.', 'LOCAL FILES ONLY'),
 '05': ('REPORT VAULT', 'Open the latest local HTML report when one exists.', 'LOCAL REPORTS'),
 '06': ('RECIPE DECK', 'Show copyable local analysis commands.', 'LOCAL RECIPE GUIDE'),
 '07': ('SYSTEM DOCTOR', 'Inspect Python and local package readiness.', 'READ-ONLY CHECK'),
 '08': ('TEST SUITE', 'Run automated regression checks on this prototype.', 'LOCAL TESTS'),
}
def terminal_columns():
 return shutil.get_terminal_size((96,24)).columns
def fit(line,limit):
 return line if len(line)<=limit else line[:max(0,limit-1)]+'…'
def latest_report():
 folder=ROOT/'NightglassReports'
 try:
  reports=sorted(folder.rglob('report.html'),key=lambda p:p.stat().st_mtime,reverse=True) if folder.exists() else []
  return reports[0] if reports else None
 except OSError:return None

STATE_FILE=ROOT/'.blackglass-session.json'
SESSION={'last_session':'NOT RUN', 'last_report':'NONE', 'import_count':'NOT TRACKED', 'unique_count':'NOT TRACKED', 'duplicate_count':'NOT TRACKED', 'reply_count':'NOT TRACKED', 'test_status':'NOT RUN', 'source_mode':'OFFLINE / IMPORT ONLY'}
def load_state():
 try:
  raw=json.loads(STATE_FILE.read_text(encoding='utf-8'))
  if isinstance(raw,dict):
   for k in SESSION:
    v=raw.get(k)
    if isinstance(v,(str,int)) and len(str(v))<=300:SESSION[k]=str(v)
 except (FileNotFoundError,OSError,ValueError,TypeError):pass

def save_state():
 # Only local aggregate counts and relative report paths, never source file names,
 # credentials, input paths, machine identifiers or imported comment contents.
 try:
  fd=os.open(str(STATE_FILE),os.O_WRONLY|os.O_CREAT|os.O_TRUNC,0o600)
  with os.fdopen(fd,'w',encoding='utf-8') as f:json.dump(SESSION,f,indent=2)
 except OSError as exc:print('Session metadata not saved:',exc)

def telemetry():
 return {**SESSION, 'quick_keys':'01 DEMO  12 THREADS  13 SOURCE  00 CLOSE'}

def process_result(command,args,report_rel):
 # Called only after engine succeeds and the exact expected report exists.
 report=ROOT/report_rel/'report.json'
 try:
  obj=json.loads(report.read_text(encoding='utf-8'))
  rows=obj['records'];meta=obj.get('metadata',{})
  if not isinstance(rows,list):raise ValueError('No records')
  original=meta.get('original_count',len(rows)+int(meta.get('duplicates_removed',0)))
  if not isinstance(original,int):raise ValueError('Invalid count')
  SESSION.update(last_session=command.upper()+' · '+datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M UTC'),
   last_report=str(report_rel/'report.html'),import_count=str(original),
   unique_count=str(len(rows)),duplicate_count=str(meta.get('duplicates_removed',0)),
   reply_count=str(sum(bool(r.get('parent_id')) for r in rows if isinstance(r,dict))))
  save_state()
  print(ink('◆ LIVE LOCAL SESSION: processed '+str(original)+' records; '+str(len(rows))+' in report',CYAN))
  return True
 except (OSError,ValueError,KeyError,TypeError) as exc:
  print('No verified session update:',exc);return False

def analyze(command,args):
 # Unique dedicated report directory prevents accidental overwrite of previous reports.
 tag=datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S%fZ')
 report_rel=Path('NightglassReports')/(command+'-'+tag)
 argv=[command,*args,'--out',str(report_rel)]
 try:
  rc=engine(argv)
  if rc in (0,None):process_result(command,args,report_rel)
  else:print('No session update: engine returned',rc)
  return rc
 except (ValueError,OSError,json.JSONDecodeError) as exc:
  print('Analysis stopped:',exc);return 2


def startup(stream=None):
 out=stream if stream is not None else sys.stdout
 for message in BOOT_LINES:print(ink('  ◆ '+message,CYAN),file=out)

def micro_panels(w):
 t=telemetry()
 print(edge(BLUE))
 print(ink(fit('◈ LAST SESSION  '+t['last_session'],w),CYAN))
 print(ink(fit('▤ LAST REPORT   '+t['last_report'],w),BLUE))
 print(ink(fit('⇣ IMPORTED '+t['import_count']+'  ·  REPORT '+t['unique_count']+'  ·  DEDUP '+t['duplicate_count']+'  ·  REPLIES '+t['reply_count'],w),LIME))
 print(ink(fit('✓ TEST STATUS   '+t['test_status'],w),CYAN))
 print(ink(fit('⌨ QUICK KEYS    '+t['quick_keys'],w),PURPLE))
 print(ink(fit('◉ SOURCE MODE   '+t['source_mode'],w),LIME))

def render(selected=None):
 global SELECTED
 if selected in MODULE_NOTES:SELECTED=selected
 w=width(); compact=w<84
 print('\n'+ink('◆ NIGHTGLASS // BLACKGLASS v2.3.0',PINK))
 print(ink('FACEBOOK-SIDE INTELLIGENCE  //  CYBER-GOTH COMMAND CENTER',BLUE))
 print(edge(PINK))
 print(ink(fit('SOURCE: IMPORTED FILES   ·   OFFLINE   ·   NOT LIVE FACEBOOK',w),LIME))
 print(ink(fit('PRIVACY: LOCAL REPORTS   ·   NO NETWORK   ·   TRANSPARENT TERMINAL UNCHANGED',w),CYAN))
 print(edge(CYAN))
 if not compact:
  print(ink(f'{"  MODULE":<31}',BLUE)+ink('FUNCTION',CYAN))
 for code,name,desc in ROWS:
  chosen=(code==SELECTED)
  label=f' {"▶" if chosen else " "} [{code}] {name}'
  if compact:
   print(ink(fit(label,w),PINK if chosen else CYAN))
  else:
   print(ink(f'{label:<31}',PINK if chosen else CYAN)+ink(fit(desc,max(0,w-31)),LIME if chosen else BLUE))
 print(edge(BLUE))
 scene,scene_detail=SCENES[SELECTED]
 print(ink(fit('╭─ '+scene+' ─ '+scene_detail,w),BLUE))
 title,detail,status=MODULE_NOTES[SELECTED]
 print(ink(fit('◆ SELECTED / '+title,w),PINK))
 print(ink(fit(detail,w),CYAN))
 print(ink(fit('MODULE: '+status,w),LIME))
 micro_panels(w)
 print(edge(CYAN))
 print(ink('◆ MORE COMMANDS · ALL NUMBERS VISIBLE',PINK))
 for code,title in FOOTER_COMMANDS:
  print(ink(f' [{code}] {title}',CYAN if int(code)%2 else BLUE))
 print(ink(' [25] HELP / ALL COMMANDS · full descriptions',LIME))
 print(ink(fit('STATUS: LOCAL ENGINE READY  ·  NETWORK: OFF BY DEFAULT · SOURCE CHECK OPT-IN',w),BLUE))
 print(ink('[25] ALL COMMANDS  |  [HELP / ?] INSTRUCTIONS  |  [00] EXIT',LIME))
FOOTER_COMMANDS=[
 ('09','LAYOUT / terminal width'),('10','COLORS / toggle'),
 ('11','SPOTLIGHT / explain a core module'),('12','THREAD EXPLORER'),
 ('13','SOURCE BRIDGE / local imports'),('14','THREAD FUSION / replies'),
 ('15','RESEARCH DESK / saved links'),('16','SOURCE GUARD / one-check cooldown'),
 ('17','INDEPENDENT SOURCE ENGINE / local'),('18','LINK FUSION / offline'),
 ('19','REPORT DECK / cat CSV list open'),('20','EASY DEMO / no filename'),
 ('21','READ LATEST FUSION REPORT'),('22','LIST SAVED REPORTS'),
 ('23','EASY RESULTS / menu'),('24','ALL VERSIONS / read-only archive')]
COMMAND_HELP={
 '01':('COMMENT FUSION','Run fictional comment demo and generate local reports.'),
 '02':('IMPORT STATION','Import a permitted CSV, JSON or JSONL file.'),
 '03':('SEARCH LENS','Search within an imported local file by name or keyword.'),
 '04':('CROSS-REFERENCE','Compare two locally supplied exports.'),
 '05':('REPORT VAULT','Find and optionally open the latest local HTML report.'),
 '06':('RECIPE DECK','Display copyable command examples.'),
 '07':('SYSTEM DOCTOR','Check local requirements and tool readiness.'),
 '08':('TEST SUITE','Run the Python unit tests.'),
 '09':('LAYOUT','Print the current terminal width and layout mode.'),
 '10':('COLORS','Toggle ANSI colors; does not change terminal transparency.'),
 '11':('SPOTLIGHT','Preview what a core module 01–08 does.'),
 '12':('THREAD EXPLORER','Browse imported comments with next/previous/search.'),
 '13':('SOURCE BRIDGE','Validate a permitted local export and optionally import.'),
 '14':('THREAD FUSION','Navigate parent/reply relationships in local reports.'),
 '15':('RESEARCH DESK','Save and browse supplied Facebook source links without scraping.'),
 '16':('SOURCE GUARD','One opt-in HTTP check; saves cooldown and stops repeated requests.'),
 '17':('SOURCE ENGINE','Import permitted posts or inspect browser-saved HTML metadata.'),
 '18':('LINK FUSION','Merge imported posts with local source references.'),
 '19':('REPORT DECK','Read latest JSON/CSV, list reports, or open saved results.'),
 '20':('EASY DEMO','Run fictional post demo without a filename.'),
 '21':('READ LATEST','Show latest local Fusion JSON report.'),
 '22':('LIST REPORTS','List saved local report files.'),
 '23':('EASY RESULTS','Open simple results submenu.'),
 '24':('ALL VERSIONS','Browse available saved reports from prior installations.'),
 '25':('HELP / ALL COMMANDS','Display this complete numbered reference.')}
def command_directory():
 print('\n'+ink('◆ NIGHTGLASS // ALL COMMANDS · 01–25',PINK))
 print(ink('FACEBOOK-BLUE DIRECTORY · descriptions · OFFLINE BY DEFAULT',BLUE))
 print(edge(CYAN))
 for num,(title,description) in COMMAND_HELP.items():
  print(ink(f'[{num}] {title}',CYAN))
  print('     '+description)
 print(edge(BLUE))
 print('00 / Q · Exit safely  |  HELP / ? · Show this list again')
 print('Option 16 and opt-in Blue Signal checks within 06/15 may request public URLs; no Facebook posts or private lists fetched.')

def ask_path(label):
 p=input(label).strip().strip('\"')
 if not p:return None
 path=Path(p).expanduser()
 if not path.is_file() or path.suffix.lower() not in ('.csv','.json','.jsonl'):
  print('File not found or unsupported type (CSV / JSON / JSONL).');return None
 return str(path)
def report():
 folder=ROOT/'NightglassReports'
 found=sorted(folder.rglob('report.html'),key=lambda p:p.stat().st_mtime,reverse=True) if folder.exists() else []
 if not found:print('No report in this independent prototype yet. Try 01.');return
 print('Latest local report:',found[0].relative_to(ROOT))
 if input('Open in default browser? [y/N] ').strip().lower()=='y':webbrowser.open(found[0].resolve().as_uri())
def act(choice):
 if choice=='01':return analyze('demo',[])
 if choice=='02':
  p=ask_path('Local CSV/JSON/JSONL path: ')
  if p:return analyze('import',[p,'--limit','100'])
 if choice=='03':
  p=ask_path('Local export path: ')
  if p:
   word=input('Search name or keyword: ').strip()
   if word:return analyze('import',[p,'--search',word,'--limit','100'])
 if choice=='04':
  a=ask_path('First export: ')
  if a:
   b=ask_path('Second export: ')
   if b:return analyze('compare',[a,b])
 if choice=='05':
  from BLUE_SIGNAL_VAULT_INTEL import menu as blue_vault
  result=blue_vault()
  return report() if result is None else result
 if choice=='06':
  from BLUE_SIGNAL_BRIDGE import recipe_deck
  result=recipe_deck()
  return engine(['examples']) if result is None else result
 if choice=='07':return engine(['doctor'])
 if choice=='08':
  rc=subprocess.run([sys.executable,'-m','unittest','discover','-s','tests','-v'],cwd=ROOT,check=False).returncode
  SESSION['test_status']='PASSED' if rc==0 else 'FAILED ('+str(rc)+')'
  save_state();return rc
 if choice=='13':
  p=ask_path('Permitted local CSV/JSON/JSONL export: ')
  if not p:return 0
  try:
   info=inspect_source(p)
   print(ink(render_summary(info),CYAN))
   if not info['schema_detected']:
    print('Schema is unfamiliar; import may require conversion.')
   answer=input('Import using existing offline engine? [y/N] ').strip().lower()
   if answer=='y':return analyze('import',[p,'--limit','100'])
   print('Inspection complete. Nothing imported.');return 0
  except (OSError,ValueError,json.JSONDecodeError) as exc:
   print('Source inspection stopped:',exc);return 2
 if choice=='15':
  from BLUE_SIGNAL_BRIDGE import research_desk as blue_research
  result=blue_research()
  return research_desk(ROOT/'ResearchDesk') if result is None else result
 if choice=='16':
  return source_check(ROOT/'SourceChecks')
 if choice=='17':
  return independent_source_engine(ROOT)
 if choice=='18':
  from POST_HUNTER import interactive as post_hunter
  return post_hunter(lambda: public_post_fusion(ROOT)) # NIGHTGLASS_POST_HUNTER_V260
 if choice=='23':
  return easy_results()
 if choice=='24':
  return unified_results()
 if choice=='20':
  print(ink('◆ EASY MODE · ONE-STEP DEMO · FICTIONAL RECORDS',PINK))
  example=ROOT/'examples'/'fictional_posts.csv'
  from PUBLIC_POST_FUSION import fuse,save
  result=fuse(str(example),ROOT)
  folder=save(result,ROOT)
  print(ink('SAVED: '+str(folder.relative_to(ROOT)),LIME))
  print(ink('◆ REPORT CONTENTS · IMPORTED / NOT LIVE',CYAN))
  return report_deck(['cat'])
 if choice=='21':
  print(ink('◆ LATEST FUSION REPORT · LOCAL ONLY',CYAN))
  return report_deck(['cat'])
 if choice=='22':
  print(ink('◆ SAVED REPORT INDEX',CYAN))
  return report_deck(['reports','--kind','all'])
 if choice=='19':
  print('REPORT DECK: 1=latest fusion JSON 2=latest fusion CSV 3=list reports 4=open latest report')
  pick=input('REPORTS ❯ ').strip()
  return report_deck({'1':['cat'],'2':['csv'],'3':['reports','--kind','all'],'4':['open']}.get(pick,['reports','--kind','all']))
 if choice=='14':
  latest=ROOT/'NightglassReports'
  files=sorted(latest.rglob('report.json'),key=lambda p:p.stat().st_mtime,reverse=True) if latest.exists() else []
  if not files:print('No report yet. Choose 01 for fictional demonstration.');return 0
  print('Opening local reply tree:',files[0].relative_to(ROOT))
  return explore_fusion(files[0])
 if choice=='12':
  latest=ROOT/'NightglassReports'
  files=sorted(latest.rglob('report.json'),key=lambda p:p.stat().st_mtime,reverse=True) if latest.exists() else []
  if not files:print('No local report yet. Run 01 for fictional demo or 02 to import a file.');return 0
  print('Opening latest local report:',files[0].relative_to(ROOT))
  return explore_threads(files[0])
 if choice=='09':print('Current terminal columns:',shutil.get_terminal_size((88,24)).columns,'; layout:', 'compact' if width()<84 else 'wide');return 0
 return 0
def menu():
 global COLOR
 load_state()
 startup()
 while True:
  render()
  try:
   choice=input(ink('BLACKGLASS ❯ ',PINK)).strip().upper()
   choice=choice.zfill(2) if choice.isdigit() else choice
   if choice in ('00','Q','QUIT','EXIT'):print('BLACKGLASS closed safely.');return 0
   if choice in ('25','HELP','?','COMMANDS'):
    command_directory()
    if sys.stdin.isatty():input(ink('\nPress Enter to return...',MUTED))
    continue
   if choice=='10':COLOR=not COLOR;continue
   if choice=='11':
    target=input(ink('Spotlight module 01–08: ',CYAN)).strip().zfill(2)
    if target in MODULE_NOTES:SELECTED=target
    else:print('Unknown module.')
    continue
   if choice in {r[0] for r in ROWS}|{'09','12','13','14','15','16','17','18','19','20','21','22','23','24'}:
    if choice in MODULE_NOTES:SELECTED=choice
    act(choice)
    if sys.stdin.isatty():input(ink('\nPress Enter to return...',MUTED))
   else:print('Choose 01–25, HELP, or 00 to close.')
  except (EOFError,KeyboardInterrupt):print('\nBLACKGLASS closed safely.');return 0
  except (OSError,ValueError) as exc:print('Input issue:',exc)
if __name__=='__main__':
 if '--snapshot' in sys.argv:load_state();render()
 elif '--boot' in sys.argv:startup()
 elif '--self-test' in sys.argv:sys.exit(subprocess.run([sys.executable,'-m','unittest','discover','-s','tests','-v'],cwd=ROOT).returncode)
 else:sys.exit(menu())

# Legacy v0.9.0 test compatibility
def size(): return max(60,min(100,shutil.get_terminal_size((82,25)).columns-2))
