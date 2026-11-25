#!/usr/bin/env python3
"""rc session records, kept in ~/.rc/sessions.json (one entry per Claude conversation).

Claude Code writes ~/.claude/sessions/<pid>.json for every running session (id, folder, name, and
bridgeSessionId = the claude.ai/code link when Remote Control is on). `save` copies every one of
them into ~/.rc/sessions.json, so they are still listed after they stop, and `resume` can
bring one back with its full history.

  sessions.py save                    record live sessions (rc-loop.sh runs this every minute)
  sessions.py add <id> <dir> <name> <task>   record a session `rc task` is about to start
  sessions.py list [<repo>]           recorded sessions: running or stopped, name, repo, link
  sessions.py get <id-prefix|name>    print id, dir, repo, branch, name (separated by \\x1f) of a stopped session (rc resume)
  sessions.py forget <id-prefix>      drop a record
Records not seen running for 30 days are dropped.
"""
import glob, json, os, re, subprocess, sys, tempfile, time

RC_DIR = os.environ.get("RC_DIR") or os.path.expanduser("~/.rc")
STORE = os.path.join(RC_DIR, "sessions.json")
LIVE = os.path.expanduser("~/.claude/sessions")
KEEP_DAYS = 30


def load():
    try:
        with open(STORE) as f:
            return json.load(f)
    except (OSError, ValueError):
        return {}


def write(d):
    os.makedirs(RC_DIR, exist_ok=True)
    fd, tmp = tempfile.mkstemp(dir=RC_DIR, prefix=".sessions.")
    with os.fdopen(fd, "w") as f:
        json.dump(d, f, indent=1, sort_keys=True)
    os.replace(tmp, STORE)


def alive(pid):
    try:
        os.kill(int(pid), 0)
        return True
    except (OSError, ValueError):
        return False


def live():
    """{session id: info} for every running Claude session on this computer."""
    out = {}
    for p in glob.glob(os.path.join(LIVE, "*.json")):
        try:
            with open(p) as f:
                d = json.load(f)
        except (OSError, ValueError):
            continue
        if d.get("sessionId") and alive(d.get("pid")):
            out[d["sessionId"]] = d
    return out


def repo_of(cwd):
    """The repo folder: for a worktree under <repo>/.claude/worktrees/<x>, that <repo>."""
    m = re.match(r"(.*?)/\.claude/worktrees/", cwd + "/")
    return m.group(1) if m else cwd


def branch(cwd):
    try:
        return subprocess.run(["git", "-C", cwd, "branch", "--show-current"], capture_output=True,
                              text=True, timeout=5).stdout.strip()
    except (OSError, subprocess.SubprocessError):
        return ""


def link(bridge):
    return f"https://claude.ai/code/{bridge}" if bridge else ""


def cmd_save():
    d, now = load(), int(time.time())
    for sid, s in live().items():          # every Claude session on this computer, rc's or not
        cwd = s.get("cwd", "")
        r = d.setdefault(sid, {"first_seen": now})
        r.update(dir=cwd, repo=repo_of(cwd), last_seen=now)
        if cwd and not r.get("branch"):
            r["branch"] = branch(cwd)
        if s.get("name"):
            r["name"] = s["name"]
        if s.get("bridgeSessionId"):
            r["link"] = link(s["bridgeSessionId"])
    cutoff = now - KEEP_DAYS * 86400
    d = {k: v for k, v in d.items() if v.get("last_seen", 0) >= cutoff}
    write(d)


def cmd_add(sid, cwd, name, task):
    d, now = load(), int(time.time())
    d[sid] = {"dir": cwd, "repo": repo_of(cwd), "name": name, "task": task, "branch": "worktree-" + os.path.basename(cwd),
              "first_seen": now, "last_seen": now}
    write(d)


def ago(t):
    s = int(time.time()) - int(t)
    for n, u in ((86400, "d"), (3600, "h"), (60, "m")):
        if s >= n:
            return f"{s // n}{u}"
    return f"{s}s"


def cmd_list(args):
    cmd_save()
    d, running = load(), live()
    want = [a for a in args if not a.startswith("-")]
    rows = sorted(d.items(), key=lambda kv: -kv[1].get("last_seen", 0))
    if not rows:
        print("no sessions recorded yet")
        return
    print(f"{'ID':9} {'STATE':8} {'SEEN':5} {'REPO':20} {'NAME':40} LINK")
    for sid, r in rows:
        repo = os.path.basename(r.get("repo", ""))
        if want and want[0] not in (repo, r.get("repo")):
            continue
        state = "running" if sid in running else "stopped"
        print(f"{sid[:8]:9} {state:8} {ago(r.get('last_seen', 0)):5} {repo[:20]:20} {r.get('name', '')[:40]:40} {r.get('link', '')}")


def find(key):
    d = load()
    hits = [k for k in d if k.startswith(key)] or [k for k, v in d.items() if v.get("name") == key]
    if len(hits) != 1:
        sys.exit(f"rc: {'no' if not hits else 'more than one'} session matches {key!r} (see rc sessions)")
    return hits[0], d


def cmd_get(key):
    sid, d = find(key)
    if sid in live():
        sys.exit(f"rc: {sid[:8]} is still running; open it in claude.ai/code ({d[sid].get('link') or 'no link'})")
    r = d[sid]
    name = r.get("name") or os.path.basename(r.get("repo", ""))
    print("\x1f".join([sid, r.get("dir", ""), r.get("repo", ""), r.get("branch", ""), name]))


def cmd_forget(key):
    sid, d = find(key)
    del d[sid]
    write(d)
    print(f"forgot {sid}")


if __name__ == "__main__":
    a = sys.argv[1:] or ["list"]
    if a[0] == "save":
        cmd_save()
    elif a[0] == "add" and len(a) == 5:
        cmd_add(*a[1:])
    elif a[0] == "list":
        cmd_list(a[1:])
    elif a[0] == "get" and len(a) == 2:
        cmd_get(a[1])
    elif a[0] == "forget" and len(a) == 2:
        cmd_forget(a[1])
    else:
        sys.exit(__doc__)
