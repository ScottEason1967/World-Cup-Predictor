# World Cup 2026 Predictor — setup guide

Three files do everything:

* **index.html** — the predictor itself. This is what goes on GitHub and what the family opens.
* **Code.gs** — the small script that catches everyone's predictions and drops them into your Google Sheet.
* **SETUP.md** — this guide.

You touch **index.html** twice (names, then a URL) and you set up one Google Sheet. That's the lot.

---

## Step 1: put the names in

Open **index.html** in any text editor (Notepad is fine). Near the top of the script section you'll find:

```
const PLAYERS = ["Scott", "Player 2", "Player 3", "Player 4"];
```

Replace those with the real names, however many you've got:

```
const PLAYERS = ["Scott", "Joe", "Isobel", "Dave", "Auntie Jan"];
```

These become the dropdown people pick from. No logins, no accounts. Picking your name is how the game knows who you are.

---

## Step 2: build the Google Sheet backend

1. Go to **sheets.google.com** and start a blank sheet. Call it whatever you like.
2. In the menu: **Extensions > Apps Script**. A code editor opens in a new tab.
3. Delete whatever's in there, then paste in the **entire** contents of **Code.gs**.
4. Click the **Save** icon (the floppy disk).
5. Click **Deploy > New deployment**.
6. Click the gear icon next to "Select type" and choose **Web app**.
7. Set it up exactly like this:
   * **Description:** anything (e.g. "WC predictor")
   * **Execute as:** **Me**
   * **Who has access:** **Anyone**
8. Click **Deploy**. Google will ask you to authorise it. Work through the prompts. When it warns the app "isn't verified", click **Advanced**, then **Go to (your project)**, then **Allow**. That warning is normal for your own scripts.
9. It gives you a **Web app URL**. Copy it. It looks like:
   `https://script.google.com/macros/s/AKfy....../exec`

---

## Step 3: connect the page to the sheet

Back in **index.html**, find this line near the top of the script:

```
const SCRIPT_URL = "";
```

Paste your URL inside the quotes:

```
const SCRIPT_URL = "https://script.google.com/macros/s/AKfy....../exec";
```

Save the file. That's the connection done. The page will now send predictions into your sheet and read them back for the leaderboard.

> Quick test before you go further: open index.html by double-clicking it. Pick a name, fill in a few games, then fill the rest, and submit. If you get a green "predictions are saved" message and a row appears in your Google Sheet, it's working.

---

## Step 4: put it on GitHub

1. Create a new repository on GitHub (public is fine).
2. Upload **index.html** to it.
3. In the repo: **Settings > Pages**. Under "Branch" pick **main** and **/ (root)**, then **Save**.
4. Give it a minute. GitHub shows you a live link, something like
   `https://yourname.github.io/your-repo/`
5. Send that link to the family. They open it, pick their name, predict, submit. Done.

---

## How the game runs

**Scoring** is baked in: 3 points for an exact scoreline, 1 for getting the result right but the score wrong, 0 otherwise. An exact score is worth 3, not 3 plus 1.

**The deadline.** Predictions lock automatically at the first kick-off, Mexico v South Africa, set in the file as 11 June 2026, 20:00 UK. Before then people can change their picks as often as they like. After it, the form is read-only. If you ever need to shift that, edit the `DEADLINE_UTC` line.

**Entering results.** Open the **Results** tab (that one's for you, not the family). As games finish, type the actual scores in and hit **Save results to sheet**. Leave unplayed games blank. The leaderboard only scores games you've entered a result for, so it stays correct all the way through.

**The leaderboard** is live for everyone. It reads all the predictions and all your results and works out the table. Hit **Refresh** after you save new results.

**Backup code.** If anyone's connection plays up, the page gives them a short code to send you instead. Paste it into the box at the bottom of the **Results** tab and it goes into the sheet like a normal submission. You probably won't need it, but it's there.

---

## The rerun for each knockout stage

You had this exactly right. Knockout games can't be predicted in advance because nobody knows who's playing until the group results land. So each stage gets its own page.

When the groups finish and the Round of 32 is set, come back to me with the 16 fixtures. I'll hand you a new HTML file that:

* points at the **same** Google Sheet (same URL, no new setup),
* uses the same names and the same scoring,
* and, because every stage writes to the same sheet, **carries the running total forward on its own**. The leaderboard adds up points across every stage, so the group-stage scores stay in the mix. No re-typing anyone's totals.

You upload the new file to the same GitHub repo, send the link round, everyone predicts the next round, you enter results as before. Same rhythm every stage through to the final.
