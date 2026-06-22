# Data model and backend — World Cup 2026 Predictor

Source: `Code.gs` and `index.html`. Verified 22 June 2026.

## The sheet
Two tabs.

`data` tab, columns in order: `timestamp, stage, name, type, data`.
- `timestamp` — server time the row was appended.
- `stage` — a string, e.g. `GROUP`. Knockout stages write their own stage value.
- `name` — the player's name, or the reserved `__RESULTS__` for the results row.
- `type` — `prediction` or `result`.
- `data` — a JSON string. An object mapping match number (as a string key) to a two-element array `[home_goals, away_goals]`. Example: `{"1":[2,0],"2":[2,1],"3":[1,1]}`. Goal order is always home first, away second, matching the fixture table.

`pins` tab, columns `name, pin`. Holds each name's 4-digit PIN. Never served back to the page. `claimedNames_()` returns the names in this tab excluding `__RESULTS__`, which is what the page uses to grey out already-claimed names.

## How writes work (PINs)
First time a name submits, the PIN it sends is saved and becomes that name's PIN. After that, any write under that name must send the matching PIN or it is rejected with `bad_pin`. PIN must match `^[0-9]{4}$`.

`__RESULTS__` sets the organiser PIN the first time results are saved. That same PIN also works as an `adminPin` override, used when the organiser imports someone's backup code on their behalf. Organiser PIN is `1712`.

Error codes returned: `no_name`, `pin_required`, `bad_pin`. Success is `{"ok":true}`.

## The endpoint
`https://script.google.com/macros/s/AKfycbyr6wUiySfXwM9mvkMGGqmcDqZe5iu3nZvO7Wcu9iVfCYi0w8pmq0YMXdd2w1K58ian_g/exec`

Everything is JSONP through `doGet`.

Read: `?action=all&callback=cb` returns `cb({"rows":[{ts,stage,name,type,data},...],"claimed":[names]})`. Reads come back as parsed objects in `data`.

Write: `?action=submit&stage=...&name=...&type=...&data=<json string>&pin=1712&callback=cb`. Wrapped in a script lock. Returns `{"ok":true}` or an error object.

`doPost` is kept as a fallback with identical PIN rules, but the page uses the JSONP `doGet` path.

## Restoring or migrating the backend
The whole backend is the single `Code.gs` file pasted into the sheet's Apps Script editor, deployed as a Web app (Execute as: Me, Who has access: Anyone), per `SETUP.md`. If the sheet is lost, recreate a blank sheet, paste `Code.gs`, redeploy, and the data tabs rebuild themselves on first use. The live data itself (predictions and results) only exists in the sheet, so the JSON snapshot in `backups/<date>/sheet-snapshot-*.json` is the only off-Google copy. Keep snapshotting it.
