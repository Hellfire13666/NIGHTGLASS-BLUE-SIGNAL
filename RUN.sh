#!/bin/sh
# nightglass portable launcher
set -eu
cd "$(dirname "$0")"
exec python3 -B COMMAND_CENTER.py "$@"
