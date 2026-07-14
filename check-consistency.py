#!/usr/bin/env python3
"""
World Cup Predictor - release consistency checker.

Run this before shipping a new round. It checks the handful of things that
have to change together every round and that keep getting missed when they're
edited by hand across ten near-duplicate HTML files:

  1. index.html default redirect points at the current live round
  2. every predict page has the full tab bar AND the CSS behind it
  3. every predict page's round switcher links all the open rounds
  4. today.html / yesterday.html carry the full fixture + kickoff schedule,
     with a stage label for every knockout tag they use
  5. every scoring page applies the +1 who-goes-through bonus
  6. final.html is structurally ready for when the Final opens

There is ONE knob: CURRENT_ROUND. Bump it the moment a round opens and the
checker enforces the new expectations. Usage:  python3 check-consistency.py
Exit code is 0 only if nothing FAILED.
"""
import re, sys, glob, os

# ---- the single source of truth: which round is live -----------------------
CURRENT_ROUND = "sf"          # group | r32 | r16 | qf | sf | final

ROUND_ORDER   = ["r32", "r16", "qf", "sf", "final"]
MAX_MATCH     = {"group":72, "r32":88, "r16":96, "qf":100, "sf":102, "final":103}
KO_LABEL      = {"R32":"Round of 32", "R16":"Round of 16", "QF":"Quarter-final",
                 "SF":"Semi-final", "F":"Final", "FINAL":"Final", "3P":"Third place"}
TABLINKS      = ["yesterday.html", "today.html", "predictions.html"]

os.chdir(os.path.dirname(os.path.abspath(__file__)) or ".")
def read(f): return open(f, encoding="utf-8", errors="replace").read()

fails, warns = [], []
def check(cond, label, detail=""):
    print(f"  [{'PASS' if cond else 'FAIL'}] {label}" + (f"  -- {detail}" if detail and not cond else ""))
    if not cond: fails.append(label + (f" ({detail})" if detail else ""))
def warn(cond, label, detail=""):
    if not cond:
        print(f"  [WARN] {label}" + (f"  -- {detail}" if detail else ""))
        warns.append(label)
    else:
        print(f"  [ok]   {label}")

open_rounds = ROUND_ORDER[:ROUND_ORDER.index(CURRENT_ROUND)+1] if CURRENT_ROUND in ROUND_ORDER else []
tabs_pages  = sorted(f for f in glob.glob("*.html") if '<nav class="tabs">' in read(f))
score_pages = sorted(f for f in glob.glob("*.html") if "scoreOne" in read(f))

print(f"\nWorld Cup Predictor consistency check  (CURRENT_ROUND = {CURRENT_ROUND})")
print(f"open rounds: {', '.join(open_rounds) or '(group only)'}\n")

# 1 -- default redirect --------------------------------------------------------
print("1. index.html default redirect")
idx = read("index.html")
m = re.search(r'location\.replace\("([^"]+?)(?:\.html)?"', idx)
target = (m.group(1) if m else "").replace(".html","")
check(m is not None, "index.html has a default redirect")
check(target == CURRENT_ROUND, "redirect points at the live round",
      f"points at '{target}', expected '{CURRENT_ROUND}'")

# 2 -- tab bar + CSS on every predict page ------------------------------------
print("\n2. Tab bar + tablink CSS on every predict page")
for f in tabs_pages:
    s = read(f)
    nav = re.search(r'<nav class="tabs">.*?</nav>', s, re.S)
    nav = nav.group(0) if nav else ""
    ok_btns = all(f'data-tab="{b}"' in nav for b in ("predict","leaderboard","organiser"))
    ok_links = all(f'href="{t}"' in nav for t in TABLINKS) and nav.count('class="tablink"') >= 3
    ok_css  = "nav.tabs a.tablink{" in s
    check(ok_btns,  f"{f}: 3 tab buttons present")
    check(ok_links, f"{f}: 3 view tablinks present", "missing Yesterday/Today/Everyone links")
    check(ok_css,   f"{f}: a.tablink CSS present", "links would render as bare text")

# 3 -- round switcher SHOWS every open round (a hidden link doesn't count) ----
# Each page carries a link for every round; a round that hasn't opened is kept
# style="display:none" and unhidden on release. So the real check is visibility,
# not mere presence -- that's the step that gets forgotten.
print("\n3. Round switcher shows every open round (not hidden)")
sw_pages = sorted(f for f in glob.glob("*.html") if 'class="stage-switch"' in read(f))
for f in sw_pages:
    block = re.search(r'<div class="stage-switch".*?</div>', read(f), re.S)
    block = block.group(0) if block else ""
    for r in open_rounds:
        tag = re.search(rf'<a[^>]*href="{r}\.html"[^>]*>', block)
        visible = tag is not None and "display:none" not in tag.group(0)
        check(visible, f"{f}: {r.upper()} tab shown in switcher",
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
    label_line = re.search(r'\$\{g==="[^}]*?"Group "\+g\}', s)
    sched[f] = dict(fx=fx, ko=ko, fx_keys=fx_keys, ko_keys=ko_keys, stages=stages,
                    label=label_line.group(0) if label_line else "")
    exp = MAX_MATCH[CURRENT_ROUND]
    check(fx_keys == ko_keys, f"{f}: every fixture has a kickoff", f"FX^KO diff {fx_keys ^ ko_keys}")
    check(fx_keys == set(range(1, exp+1)), f"{f}: covers matches 1..{exp}",
          f"missing {sorted(set(range(1,exp+1))-fx_keys)}, extra {sorted(fx_keys-set(range(1,exp+1)))}")
    for st in stages:
        if re.fullmatch(r"[A-L]", st):  # group tag, handled by else-branch
            continue
        need = KO_LABEL.get(st.upper())
        check(need is not None and need in sched[f]["label"],
              f"{f}: stage '{st}' has a label", f"'{st}' would show as 'Group {st}'")
check(sched["today.html"]["fx"] == sched["yesterday.html"]["fx"], "today/yesterday FX identical")
check(sched["today.html"]["ko"] == sched["yesterday.html"]["ko"], "today/yesterday KO identical")

# 5 -- scoring: +1 through-bonus everywhere -----------------------------------
print("\n5. Knockout +1 through-bonus on every scoring page")
bonus = re.compile(r'\w+\[2\]&&\w+\[2\]&&\w+\[2\]===\w+\[2\]\)pts\+=1')
for f in score_pages:
    nospace = re.sub(r'\s', '', read(f))
    check(bool(bonus.search(nospace)), f"{f}: applies the +1 bonus")

# 6 -- Final readiness ---------------------------------------------------------
print("\n6. Final readiness")
fin = read("final.html")
warn("nav.tabs a.tablink{" in fin and fin.count('class="tablink"') >= 3,
     "final.html tab bar + CSS ready")
if CURRENT_ROUND != "final":
    print("     When the Final pairing is known, one release does all of this:")
    print("       - add match 103 to FX and KO in today.html AND yesterday.html")
    print("       - add a 'Final' case to the stage label in both")
    print("       - flip CURRENT_ROUND to 'final' here and re-run")
    print("       - set index.html redirect to final.html")
    print("       - add href=\"final.html\" to the switcher on r32/r16/qf/sf")

# ---- summary ----------------------------------------------------------------
print("\n" + "="*60)
if fails:
    print(f"RESULT: {len(fails)} FAILED, {len(warns)} warning(s)")
    for x in fails: print("  FAIL:", x)
    sys.exit(1)
print(f"RESULT: all checks passed" + (f", {len(warns)} warning(s)" if warns else ""))
sys.exit(0)
