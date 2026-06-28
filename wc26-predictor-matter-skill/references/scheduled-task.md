# The wc26-auto-results scheduled task

Source: the task `SKILL.md` (the task spec carried in the run), the live sheet, and the run on 22 June 2026. Verified 22 June 2026.

## What it does
Auto-enters confirmed full-time 2026 World Cup group-stage scores into the prediction game's Google Sheet. It runs silently and unattended, several times a day. It writes only the `__RESULTS__` row, never a prediction row.

## What it does each run
1. Reads the current sheet (`action=all`) and notes every match already in the latest `__RESULTS__` row. It does not trust those scores just because they are there.
2. Searches the web for finished group-stage matches and cross-checks each against at least one clear post-match source.
3. Re-verifies the entire posted history every run, not only new matches. Fixes any score that was posted wrong, adds any that have since finished.
4. Maps each confirmed match to its number (1 to 72) using the fixture table in the task spec, ordering goals as `[home, away]`.
5. Builds one cumulative JSON object of all confirmed-finished matches and writes it as the `__RESULTS__` row, then reads back to verify.

Re-posting the full re-verified set every run is deliberate and self-correcting.

## What counts as FINISHED — the hard rule
A match is finished only on an explicit full-time / FT marker or a settled completed-results table from a post-match source. Not proof, and to be omitted: a live ticker or in-progress page, a half-time score, a scoreline that appears only in a URL slug, headline or page title, a FIFA match-centre title number, or any single number that cannot be confirmed as the full-time result. If a recap's goal timeline ends at half-time, the match is still running. When in doubt, omit. A run that writes nothing self-heals on the next run. A wrong score corrupts the leaderboard.

This rule has teeth because of a real failure: on 14 June 2026 a live Germany v Curacao score was posted as final (3-1) off a match-centre title and a past-tense recap. The match was still live and finished 7-1. Scott caught it.

## How it writes
Uses a headless Chromium (Playwright) in the sandbox to fire the JSONP `action=submit` GET, because that replicates exactly what the web page does. Params: `action=submit, stage=GROUP, name=__RESULTS__, type=result, data=<json string>, pin=1712, callback=<random>`. Success is `{"ok":true}`. `{"ok":false,"error":"bad_pin"}` means stop, the PIN is wrong. If Chromium will not launch, try `--no-sandbox` and `--disable-dev-shm-usage`; if it still crashes, write nothing and let the next run heal it. Never post a partial or unverified set because the browser was flaky.

## Round of 32 (added 28 June 2026)
The task now also maintains a second result row, `stage=R32`, for the Round of 32 (matches 73 to 88). It is a separate row from `GROUP` and the leaderboard sums the two stages.

Knockout data format is `{matchNo:[home90, away90, adv]}`:
- `home90`/`away90` — goals at the END OF NORMAL TIME only, i.e. the full-time whistle of the second half INCLUDING all stoppage/injury time. Judge by phase of play, not the clock number: stoppage-time goals (45+X, 90+X, a 95th-minute goal in a game that did not go to extra time) COUNT; only goals in the extra-time periods are excluded. Penalty-shootout goals are never goals.
- `adv` — "H" if the first-listed (home) team progressed, "A" if the second-listed (away) team progressed. A decisive 90-minute result forces `adv` to the winner; only a 90-minute draw leaves it to ET/penalties.

This mirrors `r32.html` exactly (`scoreOne`, `collectResults`): 3 points for the exact 90-minute score, 1 for the right 90-minute result, +1 for the right progressor.

Hard rules for R32: record a tie only when fully resolved — both the 90-minute score AND the progressor confirmed from post-match sources. Beware "a.e.t." scorelines (they include extra time and are not the 90-minute score); if a tie went past 90 it was level at 90, so record the draw and capture the winner via `adv`. Omit anything uncertain. Re-verify the whole R32 set each run; write only when the verified set changes (no more spamming identical rows — this also now applies to the completed GROUP row).

R32 fixture map (match -> home v away), taken from `r32.html` FIXTURES: 73 South Africa v Canada, 74 Germany v Paraguay, 75 Netherlands v Morocco, 76 Brazil v Japan, 77 France v Sweden, 78 Côte d'Ivoire v Norway, 79 Mexico v Ecuador, 80 England v DR Congo, 81 USA v Bosnia & Herzegovina, 82 Belgium v Senegal, 83 Portugal v Croatia, 84 Spain v Austria, 85 Switzerland v Algeria, 86 Argentina v Cabo Verde, 87 Colombia v Ghana, 88 Australia v Egypt.

## Status as at 28 June 2026
Group stage complete: all 72 matches confirmed full-time and re-verified (re-verified again this date against fresh post-match sources, including the two that needed care — 61 Norway 1-4 France and 20 Austria 3-1 Jordan). R32 handling added to the task; no R32 ties recorded yet at the time of the change. The earlier 22 June status (matches 1 to 40 only) is superseded.
