#!/usr/bin/env python3
"""NIGHTGLASS verified public-source recipes. Add-on, no original menu edits."""
import os, sys, subprocess
from pathlib import Path

RECIPES={
 "1":("JediSecFB verified public-source hunt","https://www.facebook.com/JediSecFB","posts,photos,reels,videos"),
 "2":("Meta public-source hunt","https://www.facebook.com/Meta","photos,posts,meta"),
}
def main():
    scanner=Path.home()/"Downloads"/"NIGHTGLASS-BLUE-SIGNAL-v1.0.4"/"nightglass-fusion"/"nightglass_linkfusion.py"
    if not scanner.is_file():
        print("[NIGHTGLASS] Blue Signal v1.0.4 missing. Extract its ZIP into Downloads first.")
        return 2
    print("\033[96mNIGHTGLASS // BLUE SIGNAL · VERIFIED RECIPES\033[0m")
    for k,(name,*_) in RECIPES.items():print(f"[{k}] {name}")
    print("[0] Exit")
    choice=input("NIGHTGLASS > ").strip()
    if choice=="0":return 0
    if choice not in RECIPES:
        print("Unknown selection");return 2
    name,url,hunt=RECIPES[choice]
    print(f"[SOURCE] {url} | Public HTML only | Results can change")
    return subprocess.call([sys.executable,str(scanner),url,"--check","--hunt",hunt],cwd=str(scanner.parent))
if __name__=="__main__":raise SystemExit(main())
