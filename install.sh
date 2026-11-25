#!/bin/bash
# Puts `rc` on your PATH as a symlink to this checkout (so `git pull` updates it).
# rc keeps everything else in ~/.config/rc (or ~/.rc without ~/.config): config, pins, sessions, logs.
set -euo pipefail
here=$(cd "$(dirname "$0")" && pwd)
bin=${1:-$HOME/.local/bin}
if [ -n "${RC_DIR:-}" ]; then rcdir=$RC_DIR
elif [ -d "$HOME/.config" ]; then rcdir=$HOME/.config/rc
else rcdir=$HOME/.rc; fi
mkdir -p "$bin" "$rcdir/logs"
ln -sf "$here/rc" "$bin/rc"
[ -f "$rcdir/config" ] || cp "$here/config.example" "$rcdir/config"
echo "installed $bin/rc -> $here/rc (state in $rcdir)"
case ":$PATH:" in *":$bin:"*) ;; *) echo "add to your shell profile: export PATH=\"$bin:\$PATH\"";; esac
"$here/rc" doctor || true
