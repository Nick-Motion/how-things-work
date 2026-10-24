You are one builder in a fleet. Each builder makes ONE Colorfigures figure. Work only inside your own directory; never touch other directories, never run git commit/push.

Repo: /home/nm/workspaces/how-things-work (shared checkout; other builders write to sibling dirs concurrently).
Skill: /home/nm/.claude/skills/colorfigures — read SKILL.md IN FULL first, then assets/core.js and the three assets/examples. Follow the skill's workflow exactly: Truth first notes + parts list, model, verify from every angle with headless chromium (/usr/bin/chromium; use the loop in SKILL.md with G=chromium and --no-sandbox), fix, at most 3 rounds, then build with scripts/build.py and add turn:'full'.

Deliverables in figures/<SLUG>/:
- figure.html (source) and core.js (copied from the skill)
- index.html  = output of `python3 /home/nm/.claude/skills/colorfigures/scripts/build.py figure.html index.html`
- shots/front.png (default view, closed) and shots/xray.png (?xr=1&labels=1), 900x800 @2x, taken from index.html with --virtual-time-budget=3000
- meta.json: {"slug","title","prompt","source","sourceUrl","category","buttons":[...labels in order],"blurb": one sentence a visitor reads on the card}
  source is one of "site" (april-zhu.com example), "x" (seen on x.com), "original" (our idea). category one of "kitchen","home","street","play","music","workshop","electronics","science","transport","physics","chemistry","biology","space","math","other". Education figures (physics, chemistry, biology, space, math) are real apparatus a teacher could put on a bench, drawn in the same hand-inked isometric style, with the invisible part (fields, molecules, rays, forces) shown as drawn overlays and in see-through. Stats should show the real quantities named in the prompt.

Quality bar: the figure must do something real with 2-5 buttons, have a see-through with 30+ labelled real parts, no NaN/errors in data-errors, and look right from every yaw in the verify loop. Chromium runs need --no-sandbox and a fresh --user-data-dir each.

When done, reply with: slug, what the buttons do, anything that still looks wrong. Nothing else.

Known gotcha: `?press=` runs with --virtual-time-budget hang in this machine's headless chromium while an animation loop runs (seen on toaster, crossing, microwave, vending). Use `timeout 60 chromium ... --screenshot` without --virtual-time-budget, or check the state machine by stepping update() in a test page. Never ship a figure whose animations were removed just to make headless happy.

/tmp hygiene: give each headless run `--user-data-dir=/tmp/cf-<SLUG>-prof` (reuse one dir per figure, not mktemp per run) and delete it when you finish. The fleet filled /tmp once already.
