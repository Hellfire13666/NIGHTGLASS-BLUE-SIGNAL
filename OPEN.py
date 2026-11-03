#!/usr/bin/env python3
"""Start a local BLACKGLASS copy. No installation or terminal setting changes."""
import subprocess,sys
from pathlib import Path
base=Path(__file__).resolve().parent
args=[sys.executable,str(base/'COMMAND_CENTER.py'),*sys.argv[1:]]
try:sys.exit(subprocess.run(args,cwd=base,check=False).returncode)
except KeyboardInterrupt:print('\nBLACKGLASS closed safely.')
