#!/bin/bash
# Puts `rc` on your PATH as a symlink to this checkout (so `git pull` updates it).
set -euo pipefail
here=$(cd "$(dirname "$0")" && pwd)
bin=${1:-$HOME/.local/bin}
mkdir -p "$bin" "$HOME/.config/rc"
ln -sf "$here/rc" "$bin/rc"
[ -f "$HOME/.config/rc/config" ] || cp "$here/config.example" "$HOME/.config/rc/config"
echo "installed $bin/rc -> $here/rc"
case ":$PATH:" in *":$bin:"*) ;; *) echo "add to your shell profile: export PATH=\"$bin:\$PATH\"";; esac
"$here/rc" doctor || true
