#!/bin/sh
# Start a new cartoon episode from the latest one: ./new-episode.sh ep03-counting "Episode 03 - Counting 1 to 10"
set -e
[ -n "$1" ] && [ -n "$2" ] || { echo "usage: ./new-episode.sh <folder-slug> \"<Episode NN - Title>\""; exit 1; }
cd "$(dirname "$0")/cartoon-3d/episodes"
# A planned episode already has a folder holding only its script.md; that is fine. Copy from the newest episode that has files.
[ -e "$1/episode.html" ] && { echo "$1 is already started"; exit 1; }
src=$(dirname "$(ls -d ep*/episode.html | sort | tail -1)")
mkdir -p "$1/out"
cp "$src"/episode.py "$src"/sound.py "$src"/visemes.py "$src"/episode.html "$src"/render.cjs "$src"/thumb.cjs "$1/"
[ -f "$src/scenes2.js" ] && cp "$src/scenes2.js" "$1/scenes.js"
mkdir -p "$HOME/Downloads/Lumi Land/$2"
echo "Copied $src -> $1 and made ~/Downloads/Lumi Land/$2"
echo "Next: write SCENES in $1/episode.py, then the scene drawings in $1/episode.html (see CLAUDE.md)."
