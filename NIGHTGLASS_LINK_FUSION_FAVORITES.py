#!/usr/bin/env python3
"""NIGHTGLASS Link Fusion favorites inside original [18], public HTML only."""
import sys
from pathlib import Path
from NIGHTGLASS_LINK_FUSION_CORE import run

META='https://www.facebook.com/Meta'
def interactive():
    while True:
        print('\nNIGHTGLASS // LINK FUSION FAVORITES · PUBLIC HTML')
        print('[1] META FULL | useful public links + HTTP check')
        print('[2] META ALL LINKS / NOISY | full public references + resources')
        print('[3] CUSTOM FACEBOOK URL | full + noisy')
        print('[0] Return to POST HUNTER')
        try:choice=input('LINK FUSION > ').strip()
        except (EOFError,KeyboardInterrupt):return
        if choice=='0':return
        if choice not in ('1','2','3'):
            print('[TIP] Choose 0-3');continue
        if choice=='3':
            try: url=input('PUBLIC FACEBOOK HTTPS URL (Enter cancels) > ').strip()
            except (EOFError,KeyboardInterrupt):return
            if not url:continue
        else:url=META
        print('[SOURCE] Public HTML only | link references, not retrieved Facebook posts')
        try:
            # Signature: run(url,check,max_checks,color,focus,full_urls,hunt)
            run(url,check=True,max_checks=20,color=True,focus=(choice=='1'),full_urls=True,hunt=None)
        except Exception as exc:
            # Keep exceptions from printing sensitive URL fragments.
            print('[STOP] Link check unavailable:',type(exc).__name__)
        print('[DONE] Return to LINK FUSION favorites')

if __name__=='__main__':interactive()
