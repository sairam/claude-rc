#!/bin/bash
# Keeps one `claude remote-control` running for a repo. Started by `rc open` inside tmux
# (session "rc", one window per repo). If Remote Control exits (Claude updated itself,
# network dropped, the Mac slept too long) it starts again after 5 s.
# While it runs, every Claude session on this computer is recorded in ~/.rc/sessions.json
# once a minute (`rc save`), so `rc sessions` / `rc resume` know them after they stop.
#   usage: rc-loop.sh <dir> <name> [permission-mode]
# Git repos get --spawn worktree (each remote session in its own git worktree);
# other folders fall back to same-dir.
export PATH="$HOME/.local/bin:/opt/homebrew/bin:/usr/local/bin:$PATH"
here=$(cd "$(dirname "$0")" && pwd)
dir=$1 name=$2 mode=${3:-}
cd "$dir" || exit 1
spawn=same-dir
git rev-parse --is-inside-work-tree >/dev/null 2>&1 && spawn=worktree
extra=()
[ -n "$mode" ] && extra=(--permission-mode "$mode")
( while sleep 60 && kill -0 $$ 2>/dev/null; do python3 "$here/lib/sessions.py" save 2>/dev/null; done ) &
saver=$!
trap 'kill $saver 2>/dev/null' EXIT
while true; do
  claude remote-control --spawn "$spawn" --name "$name" \
    --remote-control-session-name-prefix "$name" ${extra[@]+"${extra[@]}"}
  echo "[$(date '+%F %T')] remote-control ($name) exited; restarting in 5s"
  sleep 5
done
