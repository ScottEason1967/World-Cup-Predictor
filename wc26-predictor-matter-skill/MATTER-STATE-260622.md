---
name: World Cup 2026 Predictor — State of Play as at 22 June 2026
description: "Forensic handoff for the World Cup 2026 family prediction game. Current posture, the backup just taken, the full thinking, open items and hazards, and where the working files and the live-data snapshot live. Read ALONGSIDE SKILL.md before responding to anything about the predictor, the leaderboard, the sheet, or the results task."
type: handoff
snapshotDate: 22 June 2026
---

# World Cup 2026 Predictor — State of Play, 22 June 2026

## 1. Headline posture
The game is live and mid-tournament. Group stage is part-played: results for matches 1 to 40 are confirmed and on the sheet, the rest of the group stage is still to come. The app, the backend and the auto-results task are all working. This session did two things: it ran the scheduled results task (a no-op, nothing new to confirm), and it took a full backup and built this matter skill at Scott's request. Nothing is on fire. One real issue is flagged for attention: the leaderboard may double-count players who submitted more than once.

## 2. Timeline of the current phase
| Date | Event |
|------|-------|
| 11 Jun 2026, 20:00 UK | Predictions locked at first kick-off (Mexico v South Africa). Form read-only from here. |
| 11–14 Jun | First group matches play. 14 Jun: a live Germany v Curacao score posted in error by the task, caught by Scott, rule tightened. |
| 11–22 Jun | Task runs several times daily, building the `__RESULTS__` row up to match 40. |
| 22 Jun (this session) | Results task run: re-verified all 40, nothing new confirmed, no write. Then full backup taken and this matter skill built. |

## 3. Work done and landed this session
- Ran `wc26-auto-results`. Re-verified matches 1 to 40 against FourFourTwo's full results table. All correct. No new finished matches (the 22 June fixtures were not confirmed full-time). No write to the sheet, which is the correct self-healing outcome.
- Took a full backup to the durable drive at `World Cup Predictor/backups/260622/`:
  - `sheet-snapshot-260622.json` — the live Google Sheet data (76 rows: 24 prediction rows across 16 names, 52 `__RESULTS__` history rows, plus claimed names). This is the only off-Google copy of the live data and the most important part of the backup.
  - `app-snapshot-260622.zip` — the full app, 72 files, zip integrity verified, file count matches source.
  - `git-HEAD.txt` — current commit and last ten log lines for restore reference.
- Built this matter skill: `SKILL.md`, `references/data-model.md`, `references/scheduled-task.md`, and this state file.

## 4. The thinking
The backup matters because of where the value actually sits. The code is already safe twice over, in the local folder and on GitHub (`ScottEason1967/World-Cup-Predictor`, branch `main`). What is not safe anywhere else is the live data. Every prediction and every result lives only in the Google Sheet. If that sheet is deleted or the Apps Script deployment breaks, there is no other copy unless we snapshot it. So the real backup is the JSON pull of `action=all`, and that should be repeated periodically, not just once. The app zip is belt and braces.

On the results task, the standing logic is accuracy over freshness. The task re-posts the whole verified set every run rather than appending, so a single bad run cannot permanently poison the board, the next good run overwrites it. The 14 June Germany v Curacao incident is why the "finished" test is strict and why omitting is always safe. This session followed that: search summaries claimed France 3-1 Iraq, Norway 4-1 Senegal and Argentina 1-0 Austria for 22 June, but the clean results table showed those games as not yet played and the summaries were internally contradictory and looked like conflations of the 16/17 June matchday-1 games. So they were omitted. Correct call.

The double-counting concern is the one genuine technical risk. The leaderboard code (`index.html`, around line 587) iterates every prediction row and adds each to the player keyed by name, with no step that keeps only the latest row per name. Sean has 8 prediction rows, Dave E has 2, everyone else has 1, and Dave W has none. If there is no dedup, Sean's and Dave E's points are being summed multiple times and their standing is inflated. Sean also has a dedicated `sean-entry.html` page and, oddly, neither Sean nor Dave E appears in the `claimed` names list, which suggests their submissions came in by a path that did not set a PIN. This needs checking against the code before anyone trusts the current table.

## 5. Live strategy / plan
- Keep letting the task run. It heals itself. No manual results entry needed unless the task is failing.
- As the group stage finishes (matches up to 72), the task keeps extending `__RESULTS__`.
- When the Round of 32 bracket is set, the knockout pages (`r32.html` onward) already exist and point at the same sheet, so totals carry forward. If new fixtures need wiring into a stage page, that is the moment.
- Re-snapshot the sheet data every so often, especially around each matchday and before any change to `Code.gs` or the deployment.
- Resolve the double-counting question (open item 1) before publishing or relying on standings.

## 6. Working files offloaded
The app source already lives on the durable drive and on GitHub, so it did not need rescuing from the workspace. What was genuinely workspace-or-cloud-only, the live sheet data, was snapshotted to the durable drive.

Backup location: `World Cup Predictor/backups/260622/`
- `sheet-snapshot-260622.json` (153,239 bytes, the full `action=all` payload)
- `app-snapshot-260622.zip` (3,344,630 bytes, 72 files, integrity verified)
- `git-HEAD.txt`

One housekeeping note: an orphaned temp file `zi6KqMkL` (an identical copy of the zip, left over from a zip write that the mount blocked) sits in that folder. The mount would not let me delete it. It is harmless. Delete it by hand if you want the folder tidy.

To restore: the app restores from the zip or from GitHub. The live data restores by recreating a sheet, pasting `Code.gs`, redeploying as a Web app, then re-importing rows from the JSON snapshot. Note there is no one-click resume of the data into a fresh sheet, the snapshot is a record you would replay, not an automated import.

## 7. Factual additions for merge into SKILL.md
- None outstanding. SKILL.md was written fresh this session and already carries the player list, the endpoint, the PIN, the deadline, the scoring and the data model. Next refresh should fold in the resolution of the double-counting question once known.

## 8. Hazards and things not to repeat
- Posting an unconfirmed score. The 14 June live-score error is the precedent. Strict FT proof or omit.
- Trusting the leaderboard's per-player totals while the multiple-submission question is open.
- Writing backups into the workspace. The mount blocks zip's temp-file creation, so build the zip in scratch (`/tmp`) and copy the finished file to the drive. Do not try to zip straight onto the mount.
- Exposing the organiser PIN (1712) or the `pins` tab anywhere family-facing.
- Treating knockout matches as in scope for the group-stage results task.

## 9. Open decisions / pending
1. **Leaderboard double-counting.** Owner: Scott. Confirm whether `index.html` keeps only each player's latest prediction row when scoring. If it does not, decide the fix (dedup to latest by timestamp) and whether Sean's and Dave E's current totals need correcting. Needs a read of the scoring block and a test with Sean's 8 rows.
2. **Sean and Dave E not in `claimed` names.** Owner: Scott. Work out why their submissions did not set a PIN (likely the `sean-entry.html` path or an admin import). Decide if it matters.
3. **Backup cadence.** Owner: Scott. Decide how often to snapshot the sheet data. Suggest before and after each matchday at least.

## 10. Communication style and working preferences
Scott wants accuracy first and no guessing. Flag uncertainty plainly. Challenge weak assumptions rather than smoothing them over, which is why the double-counting issue is called out here rather than buried. UK English, no em-dashes, tight and direct. Do not dress up a no-op run as an achievement.

## 11. How to use this file
Read `SKILL.md` first, then this file, then the relevant reference. Everything factual should trace to a file, the live sheet, or the task spec. If a claim cannot be sourced, verify it before stating it. The single most important standing rule is the strict full-time test before any score goes on the sheet.
