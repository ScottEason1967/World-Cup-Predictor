#!/usr/bin/env python3
"""
World Cup Predictor - release consistency checker.

Run before shipping a new round. It checks the handful of things that must
change together every round and keep getting missed when they're hand-edited
across ten near-duplicate HTML files:

  1. index.html default redirect points at the current live round
  2. every predict page has the full tab bar AND the CSS behind it
  3. every predict page's round switcher SHOWS the open rounds (not hidden)
  4. today.html / yesterday.html carry the full fixture + kickoff schedule,
     with a stage label for every knockout tag they use
  5. every scoring page applies the +1 who-goes-through bonus
  6. final.html is structurally ready for when the Final opens

One knob: CURRENT_ROUND. Bump it the moment a round opens and the checker
enforces the new expectations.  Usage:  python3 check-consistency.py
Exit code is 0 only if nothing FAILED.
"""
import re, sys, glob, os

# ---- the single source of truth: which round is live -----------------------
CURRENT_ROUND = "sf"          # group | r32 | r16 | qf | sf | final

ROUND_ORDER = ["r32", "r16", "qf", "sf", "final"]
MAX_MATCH   = {"group":72, "r32":88, "r16":96, "qf":100, "sf":102, "final":103}
KO_LABEL    = {"R32":"Round of 32", "R16":"Round of 16", "QF":"Quarter-final",
               "SF":"Semi-final", "F":"Final", "FINAL":"Final", "3P":"Third place"}
TABLINKS    = ["yesterday.html", "today.html", "predictions.html"]

os.chdir(os.path.dirname(os.path.abspath(__file__)) or ".")
def read(f): return open(f, encoding="utf-8", errors="replace").read()

fails, warns = [], []
def check(cond, label, detail=""):
    print("  [%s] %s%s" % ("PASS" if cond else "FAIL", label,
                           ("  -- " + detail) if (detail and not cond) else ""))
    if not cond: fails.append(label + ((" (" + detail + ")") if detail else ""))
def warn(cond, label):
    print("  [%s] %s" % ("ok  " if cond else "WARN", label))
    if not cond: warns.append(label)

open_rounds = ROUND_ORDER[:ROUND_ORDER.index(CURRENT_ROUND)+1] if CURRENT_ROUND in ROUND_ORDER else []
tabs_pages  = sorted(f for f in glob.glob("*.html") if '<nav class="tabs">' in read(f))
score_pages = sorted(f for f in glob.glob("*.html") if "scoreOne" in read(f))

print("\nWorld Cup Predictor consistency check  (CURRENT_ROUND = %s)" % CURRENT_ROUND)
print("open rounds: %s\n" % (", ".join(open_rounds) or "(group only)"))

# 1 -- default redirect -------------------------------------------------------
print("1. index.html default redirect")
m = re.search(r'location\.replace\("([^"]+?)(?:\.html)?"', read("index.html"))
target = (m.group(1) if m else "")
check(m is not None, "index.html has a default redirect")
check(target == CURRENT_ROUND, "redirect points at the live round",
      "points at '%s', expected '%s'" % (target, CURRENT_ROUND))

# 2 -- tab bar + CSS on every predict page ------------------------------------
print("\n2. Tab bar + tablink CSS on every predict page")
for f in tabs_pages:
    s = read(f)
    nav = re.search(r'<nav class="tabs">.*?</nav>', s, re.S)
    nav = nav.group(0) if nav else ""
    check(all('data-tab="%s"' % b in nav for b in ("predict","leaderboard","organiser")),
          "%s: 3 tab buttons present" % f)
    check(all('href="%s"' % t in nav for t in TABLINKS) and nav.count('class="tablink"') >= 3,
          "%s: 3 view tablinks present" % f, "missing Yesterday/Today/Everyone links")
    check("nav.tabs a.tablink{" in s,
          "%s: a.tablink CSS present" % f, "links would render as bare text")

# 3 -- round switcher SHOWS every open round (a hidden link doesn't count) -----
# Each page carries a link for every round; a round that hasn't opened is kept
# style="display:none" and unhidden on release. So the real check is visibility.
print("\n3. Round switcher shows every open round (not hidden)")
for f in sorted(g for g in glob.glob("*.html") if 'class="stage-switch"' in read(g)):
    block = re.search(r'<div class="stage-switch".*?</div>', read(f), re.S)
    block = block.group(0) if block else ""
    for r in open_rounds:
        tag = re.search(r'<a[^>]*href="%s\.html"[^>]*>' % r, block)
        visible = tag is not None and "display:none" not in tag.group(0)
        check(visible, "%s: %s tab shown in switcher" % (f, r.upper()),
              "missing from switcher" if not tag else "hidden (display:none)")

# 4 -- schedule pages: fixtures, kickoffs, stage labels -----------------------
print("\n4. today.html / yesterday.html schedule")
sched = {}
for f in ("today.html", "yesterday.html"):
    s = read(f)
    fx = re.search(r'const FX=\{(.*?)\};', s, re.S).group(1)
    ko = re.search(r'const KO=\{(.*?)\};', s, re.S).group(1)
    fx_keys = set(map(int, re.findall(r'(\d+):\[', fx)))
    ko_keys = set(map(int, re.findall(r'"(\d+)":', ko)))
    stages  = set(re.findall(r'\d+:\["([^"]+)"', fx))
    lab = re.search(r'\$\{g==="[^}]*?"Group "\+g\}', s)
    sched[f] = {"fx":fx, "ko":ko, "label": lab.group(0) if lab else ""}
    exp = MAX_MATCH[CURRENT_ROUND]
    check(fx_keys == ko_keys, "%s: every fixture has a kickoff" % f, "FX^KO diff %s" % (fx_keys ^ ko_keys))
    check(fx_keys == set(range(1, exp+1)), "%s: covers matches 1..%d" % (f, exp),
          "missing %s" % sorted(set(range(1, exp+1)) - fx_keys))
    for st in stages:
        if re.fullmatch(r"[A-L]", st):    # group tag -> handled by the else branch
            continue
        need = KO_LABEL.get(st.upper())
        check(need is not None and need in sched[f]["label"],
              "%s: stage '%s' has a label" % (f, st), "would show as 'Group %s'" % st)
check(sched["today.html"]["fx"] == sched["yesterday.html"]["fx"], "today/yesterday FX identical")
check(sched["today.html"]["ko"] == sched["yesterday.html"]["ko"], "today/yesterday KO identical")

# 5 -- scoring: +1 through-bonus everywhere -----------------------------------
print("\n5. Knockout +1 through-bonus on every scoring page")
bonus = re.compile(r'\w+\[2\]&&\w+\[2\]&&\w+\[2\]===\w+\[2\]\)pts\+=1')
for f in score_pages:
    check(bool(bonus.search(re.sub(r'\s', '', read(f)))), "%s: applies the +1 bonus" % f)

# 6 -- Final readiness --------------------------------------------------------
print("\n6. Final readiness")
fin = read("final.html")
warn("nav.tabs a.tablink{" in fin and fin.count('class="tablink"') >= 3, "final.html tab bar + CSS ready")
if CURRENT_ROUND != "final":
    print("     When the Final pairing is known, one release does all of this,")
    print("     then re-run this check:")
    print("       - add match 103 to FX and KO in today.html AND yesterday.html")
    print("       - add a Final case to the stage label in both")
    print("       - set index.html redirect to final.html")
    print("       - unhide the Final tab in the switcher on r32/r16/qf/sf")
    print("       - set CURRENT_ROUND = final at the top of this file")

# ---- summary ----------------------------------------------------------------
print("\n" + "=" * 60)
if fails:
    print("RESULT: %d FAILED, %d warning(s)" % (len(fails), len(warns)))
    for x in fails: print("  FAIL:", x)
    sys.exit(1)
print("RESULT: all checks passed" + ((", %d warning(s)" % len(warns)) if warns else ""))
sys.exit(0)
