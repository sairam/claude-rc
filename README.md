# rc: Claude Code Remote Control for your local repos

`rc` is a small bash script for macOS (it also runs on Linux). It runs
[Claude Code Remote Control](https://code.claude.com/docs) for the git repos on
your computer, so you can open a repo and work on tasks from **claude.ai/code** or
the **Claude app** (phone, tablet, another computer). The code stays on your
computer and runs there.

```
rc repos                         repos under ~/dev: branch, uncommitted changes, running or not
rc open <repo>                   start Remote Control for a repo (each session gets its own git worktree)
rc stop <repo>                   stop it
rc ls                            running Remote Control instances and how many sessions each has
rc task <repo> "<task>"          start one session now, in a new worktree, with the task as its first message
rc tasks                         task sessions that are open
rc sessions [<repo>]             every Claude session rc recorded: running or stopped, name, link
rc resume <id|name>              bring back a stopped session with its full history
rc forget <id>                   drop a session record
rc attach [<window>]             look at an instance or a task in tmux (detach with Ctrl-b d)
rc pin|unpin <repo>              keep a repo always running
rc up                            start every pinned repo that is not running
rc trust <repo>                  mark a folder trusted for Claude
rc autostart on|off              run `rc up` when you log in (launchd agent)
rc doctor                        check tmux, git, claude, python3 and your Claude login
```

`<repo>` is a path, or a folder name under `$RC_DEV` (default `~/dev`).

## Install

```bash
brew install tmux                       # git and python3 come with the Xcode command line tools (python3 is required)
git clone https://github.com/sairam/claude-rc.git ~/dev/claude-rc
~/dev/claude-rc/install.sh                     # symlink ~/.local/bin/rc, create the config, run rc doctor
```

You also need Claude Code (`claude`) and a login (`claude`, then `/login`).
Remote Control needs a claude.ai plan that includes it.

## Two ways to work

**1. Open a repo, then start tasks from your phone.**

```bash
rc open my-app
```

This runs `claude remote-control --spawn worktree --name my-app` in the repo, inside
the tmux session `rc` (one window per repo). "my-app" shows up in claude.ai/code and
in the Claude app. Each new session you start there gets its own git worktree, so
several tasks can run in parallel without touching each other or your own checkout.
If Remote Control stops (Claude updated itself, the network dropped, the Mac slept),
`rc-loop.sh` starts it again after 5 seconds.

**2. Start a task from the terminal, continue anywhere.**

```bash
rc task my-app "Fix the Safari sign-in bug and add a test"
```

This runs `claude -w <slug> --remote-control "my-app · <slug>" "<task>"` in a new
tmux window (session `rc-tasks`). Claude makes a new worktree (branch
`worktree-<slug>`) and starts on the task at once. The session shows in claude.ai/code
under that name, so you can follow it and answer from your phone. `rc attach <window>`
shows it in the terminal.

## Sessions are kept

rc records every Claude session on your computer in `sessions.json` (in the rc folder, below): id, folder
(worktree), repo, branch, name, claude.ai link, and the task text for `rc task`.
`rc task` records its session before it starts (it gives Claude the id with
`--session-id`); the others are picked up from `~/.claude/sessions/` once a minute while
any `rc open` instance runs, and each time you run `rc sessions`.

```bash
rc sessions            # ID, running/stopped, last seen, repo, name, link
rc resume 4477e7d3     # or the session name
```

`rc resume` runs `claude --resume <id> --remote-control "<name>"` in a new tmux window
(session `rc-tasks`), from the folder the conversation started in. If that worktree was
deleted, rc creates it again at the same path on its old branch. The session keeps its
name and full history; it gets a new claude.ai link. rc refuses to resume a session that
is still running. Records not seen running for 30 days are dropped.

## Folder trust

The first time Claude runs in a folder it asks whether you trust it. Inside tmux nobody
sees that question, so `rc open` stops and tells you. Then do one of these:

- `rc attach my-app`, answer the question, detach with Ctrl-b d, or
- `rc trust my-app`, which sets the same flag in `~/.claude.json`
  (`hasTrustDialogAccepted`), then `rc stop my-app && rc open my-app`.

`rc pin` and `rc open --trust` also mark the folder trusted. Only trust repos you know.

## Settings

Everything rc keeps is in one folder: `~/.config/rc` when `~/.config` exists (as on most
Macs), else `~/.rc`. Set `RC_DIR` to use another folder.

| File | What |
|---|---|
| `config` | settings (bash, all optional; see `config.example`) |
| `projects.txt` | pinned repos, one path per line |
| `sessions.json` | session records |
| `logs/autostart.log` | output of `rc up` at login |

If you used a version that kept them in `~/.rc` and `~/.config` exists, rc moves them to
`~/.config/rc` on first run.

Settings in `config`:

| Setting | Default | Meaning |
|---|---|---|
| `RC_DEV` | `~/dev` | folder that holds your repos |
| `RC_PERMISSION_MODE` | empty (Claude's default) | `acceptEdits`, `auto`, `plan`, `default` or `dontAsk` for new sessions |
| `RC_TMUX_SESSION` | `rc` | tmux session for `rc open` |
| `RC_TMUX_TASKS` | `rc-tasks` | tmux session for `rc task` |

## Start at login

```bash
rc pin my-app
rc autostart on       # ~/Library/LaunchAgents/dev.rc.up.plist runs `rc up` 20 s after login
```

Remote Control can only answer while your Mac is awake. To keep it awake on power:
`caffeinate -s` in a terminal, or System Settings › Battery › Options.

## Files

| File | What it is |
|---|---|
| `rc` | the command (bash 3.2, the version macOS ships) |
| `rc-loop.sh` | keeps one `claude remote-control` running for a repo; restarts it when it exits; records sessions every minute |
| `lib/sessions.py` | session records in `sessions.json` (save, list, resume lookup, forget) |
| `install.sh` | symlinks `rc` into `~/.local/bin` and creates the config |
| `config.example` | settings template |
| `launchd/rc-up.plist` | template for `rc autostart on` |

## License

Public domain ([Unlicense](https://unlicense.org/)): no copyright, use it for anything.
Written by Claude Code from requirements by sairam.
