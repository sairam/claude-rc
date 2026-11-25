#!/bin/bash
# Puts `rc` on your PATH as a symlink to this checkout (so `git pull` updates it).
# rc keeps everything else in ~/.rc/ (config, pins, session records, logs).
set -euo pipefail
here=$(cd "$(dirname "$0")" && pwd)
bin=${1:-$HOME/.local/bin}
rcdir=${RC_DIR:-$HOME/.rc}
if [ ! -e "$rcdir" ] && [ -d "$HOME/.config/rc" ]; then mv "$HOME/.config/rc" "$rcdir"; fi
mkdir -p "$bin" "$rcdir/logs"
ln -sf "$here/rc" "$bin/rc"
[ -f "$rcdir/config" ] || cp "$here/config.example" "$rcdir/config"
echo "installed $bin/rc -> $here/rc (state in $rcdir)"
case ":$PATH:" in *":$bin:"*) ;; *) echo "add to your shell profile: export PATH=\"$bin:\$PATH\"";; esac
"$here/rc" doctor || true
