---
name: wc26-predictor-matter
description: "Verified background facts for the World Cup 2026 family prediction game (the web app, the Google Sheet backend, and the wc26-auto-results scheduled task). MANDATORY: read this skill before answering ANY question about the World Cup Predictor, the leaderboard, scoring, the fixtures, the Google Sheet, the results task, or any of the family players. Do not rely on memory. Every factual claim must be sourced from this skill or verified against the actual files and the live sheet."
---

# World Cup 2026 Predictor — Verified Background

## How to use this skill
1. Read this file first for the key facts and how the pieces fit together.
2. For detail, read the reference files under `references/`.
3. For the current state of play, read the most recent `MATTER-STATE-*.md`.
4. If something is not covered here, go to the source (the app files, `Code.gs`, or the live sheet via `action=all`) and verify before stating it.

## What this matter is
A family prediction game for the 2026 FIFA World Cup. People pick scorelines for every match, the app scores them against the real results, and a live leaderboard ranks the family. It is three moving parts:

- A static web app (HTML + inline JS) that the family open in a browser. Hosted on GitHub Pages, repo `ScottEason1967/World-Cup-Predictor`.
- A Google Sheet plus a Google Apps Script web app (`Code.gs`) that stores predictions and results and serves them back over JSONP.
- A scheduled task, `wc26-auto-results`, that auto-enters confirmed full-time group-stage scores into the sheet so the leaderboard updates without Scott typing them in.

Scott is the organiser. The matter type is a build/development project with a live data store.

## The people
Scott Eason is the organiser and owner of the repo and the sheet.

The 17 players hard-coded in `index.html` (`PLAYERS`, line 296): Scott, Vickie, Isobel, Joseph, Nat, Dave E, Maureen, Sean, Jen, Derek, Dave W, Jacob, Esme, Dave B, Claire, Olivia, Josh.

There is no login. Picking your name from the dropdown is how the game knows who you are. A self-service 4-digit PIN protects each name after first use (see Framework below).

## Key files and locations
| Item | What it is | Location |
|------|-----------|----------|
| `index.html` | The predictor, the results admin tab, and the live leaderboard. The main app. | repo root |
| `Code.gs` | Google Apps Script backend. Paste-in to the sheet's Apps Script editor. | repo root |
| `SETUP.md` | Plain-English setup guide for the sheet, the URL wiring, and GitHub Pages. | repo root |
| `predictions.html` | View of submitted predictions. | repo root |
| `today.html` | Today's fixtures view. | repo root |
| `r32.html`, `r16.html`, `qf.html`, `sf.html`, `final.html` | Per-stage knockout prediction pages, added ready for the bracket. All point at the same sheet so totals carry forward. | repo root |
| `sean-entry.html` | A standalone entry page for Sean. Relevant to the Sean data anomaly noted in the state file. | repo root |
| `images/` | Flags (per-country SVGs), mascots, player and trophy art. | repo root |
| Git remote | `https://github.com/ScottEason1967/World-Cup-Predictor.git`, branch `main` | GitHub |

## Critical numbers and parameters
- **Apps Script endpoint:** `https://script.google.com/macros/s/AKfycbyr6wUiySfXwM9mvkMGGqmcDqZe5iu3nZvO7Wcu9iVfCYi0w8pmq0YMXdd2w1K58ian_g/exec` (`SCRIPT_URL`, `index.html` line 293; same value used by the scheduled task).
- **Organiser PIN:** `1712`. Used by the scheduled task to write the `__RESULTS__` row, and as the admin override for importing backup codes. Treat as a secret. It is not stored in the repo, it lives in the task spec and the `pins` tab.
- **Prediction deadline:** `DEADLINE_UTC = "2026-06-11T19:00:00Z"` (`index.html` line 300), which is 20:00 UK on 11 June 2026, first kick-off Mexico v South Africa. Picks lock at that instant and the form goes read-only.
- **Group stage:** 72 matches, numbered 1 to 72. Knockouts are separate stages and out of scope for the results task.
- **Players:** 17 defined, 16 had submitted at least once as at 22 June 2026 (Dave W had not).

## Framework: how the app actually works
**Scoring (baked into `index.html`, function `scoreOne` used around line 593):** 3 points for an exact scoreline, 1 point for the right result (win/draw/loss) but wrong score, 0 otherwise. Exact is a flat 3, not 3 plus 1. A match a player did not predict scores nothing for them.

**Data model:** the sheet has a `data` tab with columns `timestamp, stage, name, type, data`. `type` is either `prediction` or `result`. `data` is a JSON object mapping match number to `[home, away]`, e.g. `{"1":[2,0],"2":[2,1]}`. Results are stored under the reserved name `__RESULTS__` with `type=result`. A separate `pins` tab holds `name, pin` and is never served back to the page. See `references/data-model.md`.

**Read/write path:** everything goes through `doGet` over JSONP. `action=all` returns `{rows:[...], claimed:[...]}`. `action=submit` writes a row after checking the PIN. `doPost` is a fallback with the same PIN rules. See `references/data-model.md`.

**Leaderboard:** computed client-side, live, across every stage found in the sheet, by reading all predictions and all result rows. Knockout pages write to the same sheet so totals accumulate on their own. The leaderboard is the source of truth for standings. The scheduled task does not compute it.

**The scheduled task `wc26-auto-results`:** runs several times a day, re-verifies the entire posted results history against post-match sources, and writes the full cumulative `__RESULTS__` object every run. It only ever touches the `__RESULTS__` row, never a prediction row. Strict rule on what counts as finished. See `references/scheduled-task.md`.

## Decisions taken (verified)
- One page per knockout stage rather than one dynamic bracket, because knockout fixtures are unknown until the groups finish. Each stage page reuses the same names, scoring and sheet URL so running totals carry forward without re-typing. Source: `SETUP.md`, "The rerun for each knockout stage", and the presence of `r32/r16/qf/sf/final.html`.
- Results entry automated via the scheduled task so the leaderboard stays current without Scott manually typing scores. The task re-posts the whole verified set every run as a self-correcting mechanism.
- Accuracy beats freshness on results. A run that writes nothing when nothing is confirmed is fine and self-heals next run. A wrong score corrupts the leaderboard and is the one outcome to avoid.

## What NOT to state without verification
- **Never post a score to the sheet that is not confirmed full-time.** Do not treat a page title, a URL slug, a FIFA match-centre number, or a past-tense recap as proof. If a recap's goal timeline ends at half-time, the match is still live. This rule exists because on 14 June 2026 a live Germany v Curacao score (posted as 3-1, actually 7-1 final) corrupted the board and Scott rightly objected. Confirm an explicit FT marker, cross-check the goal timeline, omit when in doubt.
- **Do not assume the leaderboard dedupes to a player's latest prediction.** As at 22 June the code sums across all prediction rows for a name. Sean has 8 prediction rows and Dave E has 2. This may inflate their totals. Flagged as an open item in the state file. Verify against the code before making any claim about anyone's standing.
- **Do not expose the organiser PIN (1712) or the `pins` tab contents** in anything family-facing.
- **Do not invent player names or match numbers.** The 17 names and the 1 to 72 fixture map are fixed. Use them, do not guess.
- **Do not claim a knockout result was handled by the task.** The task is group stage only, matches 1 to 72.

## Revision history
- 22 June 2026: initial build. Grounded in `index.html`, `Code.gs`, `SETUP.md`, the live sheet snapshot, and the `wc26-auto-results` task spec. Mode A.
