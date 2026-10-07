#!/bin/bash
# Memory Kit installer — copies scripts to your agent's script dir
set -e
DEST="${1:-$HOME/.hermes/scripts}"
mkdir -p "$DEST"
cp scripts/*.py "$DEST/"
chmod +x "$DEST"/*.py
echo "✅ Installed to $DEST:"
ls -1 "$DEST"/*.py
echo ""
echo "Next: set up the daily GC cron:"
echo "  15 9 * * * python3 $DEST/memory_gc.py"
