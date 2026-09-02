# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this repo is

Personal automation scripts that perform daily check-in / task collection against six Chinese app and mini-program APIs (Ninebot, SMZDM, Tastien, Zhcommerce, Suntory, DailyCharge), then push one notification via Server酱 (ServerChan). Two deployment targets:

- **GitHub Actions** — `daily.yml` runs on a cron schedule (07:00 Beijing); other workflows are manual-only.
- **青龙 (QingLong) panel** — scripts are imported by their `cron:` / `new Env()` docstring headers and run via `combined_signin.py`.

`zhcommerce/` and `tastien/` are deliberately **not** run on GitHub Actions (their APIs need mainland-China IPs); they run locally or on QingLong.

## Commands

No build, no tests, no linters. Each script is standalone and verifies its own required env vars on startup.

```bash
# Python deps (repo root requirements.txt: requests, pycryptodome — pycryptodome is only used by zhcommerce)
pip install -r requirements.txt

# Node deps (smzdm/ only — installed by the workflows with exactly this command)
npm install crypto-js got@11 tough-cookie
```

Run examples (full env-var reference lives in README.md):

```bash
NINEBOT_TOKEN=... NINEBOT_DEVICE_ID=... python3 ninebot/nine_bot_checkin.py
SMZDM_COOKIE=... node smzdm/smzdm_checkin.js
TASTIEN_USER_TOKENS='token1&token2' python3 tastien/tastien_checkin.py   # multi-account: & or @ separator
ZH_DEVICE_ID=... python3 zhcommerce/zhcommerce_signin.py                 # first run registers device + caches session
SUNTORY_AUTHORIZATION='bearer ...' python3 suntory/suntory_signin.py
DAILYCHARGE_UID=... DAILYCHARGE_USERID_LOCKED=... DAILYCHARGE_USERID_OPEN=... python3 dailycharge/dailycharge_signin.py
python3 combined_signin.py                                              # QingLong combined entry
```

Workflows pin Python 3.10 and Node 20 — keep script syntax compatible with those.

## Architecture

### Per-platform script groups, fully standalone

There is no shared library. Each of the six platform directories is self-contained and duplicates its own helpers (log writing, env checks, retry-session builders, Server酱 push). `notification.py` exists in `ninebot/`, `tastien/`, and `zhcommerce/` separately and has diverged between them — when fixing a bug in one, check the others deliberately rather than assuming they match.

- **Python groups** follow the same shape: a signin script that prints markdown logs, checks required env vars up front, builds a `requests.Session` with `urllib3 Retry` (429/5xx), and exits nonzero on failure.
- **`smzdm/` (Node.js)** is a port of hex-ci/smzdm_script: `env.js` is a multi-runtime (Node/QuantumultX/Surge/Loon) framework; `bot.js` holds the `SmzdmBot` base class plus `requestApi()`, which auto-signs all requests with MD5 (`SIGN_KEY` in bot.js); `library_task.js` holds `SmzdmTaskBot`; each entry script subclasses a bot and defines `run()`.

### Three execution/notification modes (the core design)

A script's behavior is switched by the `COMBINED_SUMMARY_MODE` env var (`yes`/`1`/`true`/`on`):

1. **Combined (GitHub Actions)** — `daily.yml` sets `COMBINED_SUMMARY_MODE=yes`; scripts only print markdown and write log files, no self-notification. Jobs upload logs as artifacts; `send_combined_summary.py` downloads them, reads `*_JOB_RESULT` env vars (injected from `needs.<job>.result`), and pushes one Server酱 message.
2. **Combined (QingLong)** — `combined_signin.py` runs suntory, dailycharge, tastien, and zhcommerce as subprocesses with `COMBINED_SUMMARY_MODE=yes`, concatenates their stdout as one markdown report, and sends it via QingLong's built-in `notify` module (imported through `sys.path.append("/ql/data/scripts")` / `"/ql/scripts"` hacks — do not remove these).
3. **Standalone** — without the mode flag, each script self-notifies at the end: QingLong `notify` if importable, otherwise Server酱 via `SERVER_CHAN_SEND_KEY`, otherwise just prints the summary.

`COMBINED_SUMMARY_MODE` also suppresses verbose output (raw JSON response blocks) in tastien so the combined report stays compact.

### Markdown log convention

Script outputs are concatenated verbatim into summary reports, so format matters: every script prints `### <name>` headings and `- ` bullets; lines wrapped in `=== ... ===` are converted to `## ...` headings by `format_markdown_line()` in the notification helpers. New scripts must follow the same format or the aggregated report breaks.

### QingLong scheduling headers

Every standalone Python/JS script has a docstring/comment header like:

```
cron: 30 7 * * *
new Env('组合签到(三得利&天天充电&塔斯汀&zhcommerce)');
```

QingLong imports read these to auto-create schedules. They have **no effect** on GitHub Actions (workflows define their own schedules). Keep them when editing scripts.

### zhcommerce security module

`zhcommerce/zh_security.py` implements the mini-program v354 security flow: fetch server RSA pubkey → local 1024-bit keypair → register device (payload RSA-encrypted, chunked PKCS1v1.5) → session cached at `~/.zhcommerce/session.json` (~28-day validity, auto re-registers on expiry). Request signing is `SHA256(sorted-params + key)`: with `useNewAlgorithm=false` the key is `WAP_KEYS[timestamp % 10]` (hardcoded key table); with `useNewAlgorithm=true` the key is the session `signKey` and the URL path joins the signed string. `zhcommerce_signin.py` retries once on `PUB-00006` by force re-registering the device.

### tastien multi-account

`TASTIEN_USER_TOKENS` holds one or more `user-token`s split by `&` or `@`. The activity ID is fetched dynamically from the banner API; if that fails, a fallback is computed as `59 + months_since(2025-05-01)` — this formula is date-dependent and may need bumping when the platform rotates activity IDs.

## GitHub Actions workflows

- `daily.yml` — the only scheduled workflow (`0 23 * * *` UTC = 07:00 Beijing). Three parallel jobs (`run-ninebot`, `run-smzdm`, `run-dailycharge`) then a `send-summary` job with `if: always()` and `continue-on-error` artifact downloads, so notification still fires when a job fails.
- All other workflows are `workflow_dispatch` only — manual debugging entries for individual platforms.

## Conventions and gotchas

- Comments, log output, commit messages (conventional prefixes: `fix:`, `refactor:`, `docs:`), and the README are in Chinese — follow suit.
- README.md is the source of truth for env vars, secrets, and the "Workflow Environment Variables" table; the README explicitly asks to keep that table in sync when workflow values change.
- `smzdm.yml` and the README reference `smzdm/send_summary.js`, which does not exist in the repo — the manual smzdm workflow's last step fails as written.
- Scripts hit live third-party APIs: a real local run performs that day's actual check-in, and failed-pattern requests can trip platform risk control. Prefer dry reading/`--help`-style inspection or deferring actual runs to the user.
- Log files (`ninebot_log.txt`, `smzdm_log.txt`, `tastien_log.txt`, `zhcommerce_log.txt`) are written to the CWD and deleted after successful standalone push — don't commit them.
