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

## Status as at 22 June 2026
Latest `__RESULTS__` row holds matches 1 to 40, all confirmed full-time and re-verified against FourFourTwo's full results table. The 22 June group-stage fixtures (41 Norway v Senegal, 42 France v Iraq, 43 Argentina v Austria, 44 Jordan v Algeria) were not yet confirmed full-time at the time of the run, so they were correctly omitted despite some search summaries asserting scores for them. See the matter state file for detail.
