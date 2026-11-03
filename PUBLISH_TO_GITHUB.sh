#!/bin/sh
# NIGHTGLASS // BLUE SIGNAL | one-time publication from verified release
set -eu
REPO='https://github.com/Hellfire13666/NIGHTGLASS-BLUE-SIGNAL.git'
HERE=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
command -v git >/dev/null 2>&1 || { echo '[STOP] git not installed'; exit 1; }
command -v python3 >/dev/null 2>&1 || { echo '[STOP] python3 not installed'; exit 1; }
# Reject local private output, unreviewed source files, and accidental leftovers.
python3 - "$HERE" <<'PY'
import sys,re
from pathlib import Path
root=Path(sys.argv[1]); allowed={
'BLUE_SIGNAL_BRIDGE.py','BLUE_SIGNAL_VAULT_INTEL.py','COMMANDS.md','COMMAND_CENTER.py','EASY_RESULTS.py','EVIDENCE_INSPECTOR.py','NIGHTGLASS_LINK_FUSION_CORE.py','NIGHTGLASS_LINK_FUSION_FAVORITES.py','NIGHTGLASS_PUBLIC_DISCOVERY.py','NIGHTGLASS_RECIPES.py','NIGHTGLASS_SMART_LINK_FUSION.py','OPEN.py','OPEN_REPORT.py','PAGE_RESEARCH_FUSION.py','PHOTO_POST_FUSION.py','POST_HUNTER.py','POST_INTELLIGENCE.py','PUBLIC_POST_FUSION.py','README.md','REPORT_DECK.py','RESEARCH_DESK.py','SOURCE_BRIDGE.py','SOURCE_CHECK.py','SOURCE_ENGINE.py','THREAD_EXPLORER.py','THREAD_FUSION.py','UNIFIED_RESULTS.py','RUN.sh','.gitignore','PUBLISH_TO_GITHUB.sh',
'assets/NIGHTGLASS-REPOSITORY-BANNER.jpg','assets/NIGHTGLASS-SOCIAL-PREVIEW-1280x640.jpg',
'examples/fictional_posts.csv','examples/fictional_comments.csv','examples/fictional_second_export.json',
' nightglass/__init__.py'.strip(),'nightglass/__main__.py'}
allowed.update(str(p.relative_to(root)) for p in (root/'tests').glob('test_*.py'))
actual={str(p.relative_to(root)) for p in root.rglob('*') if p.is_file()}
if actual!=allowed:
 print('[STOP] Unexpected/missing files:', ', '.join(sorted(actual^allowed)));sys.exit(1)
for n in actual:
 p=root/n
 if p.suffix in {'.py','.sh','.txt','.md','.json','.csv'}:
  b=p.read_bytes()
  for check in (rb'/home/[A-Za-z0-9_.-]+/',rb'-----BEGIN (?:RSA |OPENSSH |EC )?PRIVATE KEY-----',rb'(?i)(?:access_token|api_key|client_secret|password)\s*[:=]\s*[\'\"][^\'\"]{12,}'):
   if re.search(check,b):print('[STOP] Review needed:',n);sys.exit(1)
print('[PASS] Release allowlist + basic privacy scan')
PY
# GitHub authorization is handled by user's existing git/credential-manager setup.
TMP=$(mktemp -d)
trap 'rm -rf "$TMP"' EXIT HUP INT TERM
printf '[GITHUB] Connecting to existing NIGHTGLASS repository...\n'
git clone --quiet "$REPO" "$TMP/repo"
# Never overwrite an existing release or unrelated repository files.
if [ -n "$(git -C "$TMP/repo" ls-files)" ]; then
  echo '[STOP] Repository already has tracked files; no changes made.'
  exit 1
fi
cp -R "$HERE"/. "$TMP/repo"/
git -C "$TMP/repo" add --all
git -C "$TMP/repo" diff --cached --name-only | grep -E '\.(py|md|sh|jpg|json|csv)$|\.gitignore' >/dev/null || { echo '[STOP] Nothing staged'; exit 1; }
git -C "$TMP/repo" commit -qm 'Update tool documentation'
git -C "$TMP/repo" push --quiet origin HEAD
printf '[PUBLISHED] NIGHTGLASS // BLUE SIGNAL code, README, banner, and social preview uploaded.\n'
printf '[NOTE] Set GitHub Social preview manually to assets/NIGHTGLASS-SOCIAL-PREVIEW-1280x640.jpg\n'
