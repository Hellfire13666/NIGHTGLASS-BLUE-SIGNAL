#!/usr/bin/env python3
from pathlib import Path
from urllib.parse import urlparse
import webbrowser
root=Path(__file__).resolve().parent
reports=sorted((root/'NightglassReports').glob('**/report.html'), key=lambda p:p.stat().st_mtime,reverse=True)
if not reports:
    print('No reports found. Run ./RUN.sh demo first.')
else:
    print('Opening most recent LOCAL report:',reports[0].relative_to(root))
    webbrowser.open(reports[0].resolve().as_uri())
