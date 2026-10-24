#!/usr/bin/env bash
# Coordinator spot-check of one built figure. Usage: verify_figure.sh <slug>. Exit 0 = pass. Prints one line per check.
set -u
cd "$(dirname "$0")/figures/$1" || exit 2
fail=0; ok(){ echo "ok   $1"; }; bad(){ echo "FAIL $1"; fail=1; }
for f in index.html figure.html meta.json shots/front.png shots/xray.png; do [ -s "$f" ] && ok "$f present" || bad "$f missing"; done
python3 -I - <<'EOF' || fail=1
import json,sys
m=json.load(open('meta.json'))
need={'title','prompt','source','category','buttons','blurb'}
missing=need-m.keys(); print(('FAIL meta missing '+','.join(missing)) if missing else 'ok   meta fields')
print('ok   buttons %d'%len(m['buttons']) if 2<=len(m['buttons'])<=6 else 'FAIL buttons %d'%len(m['buttons']))
sys.exit(1 if missing else 0)
EOF
grep -q "turn:'full'\|turn: 'full'\|turn:\"full\"" index.html && ok "turn:full" || bad "turn:full missing"
grep -q "xrMount" index.html && ok "see-through wired" || bad "no xrMount"
labels=$(grep -o "text:'[A-Z][A-Z0-9 /-]*'" figure.html | sort -u | wc -l)
[ "$labels" -ge 25 ] && ok "labels $labels" || bad "labels $labels (<25)"
grep -q "<script src=\"core.js\"" index.html && bad "index.html not built (still loads core.js)" || ok "self-contained"
T=$(mktemp -d)
for v in "yaw=45" "yaw=200" "yaw=300&xr=1&labels=1" "yaw=110&xr=1&labels=1"; do
  chromium --headless=new --no-sandbox --hide-scrollbars --user-data-dir="$(mktemp -d)" --window-size=900,800 \
    --virtual-time-budget=3000 --dump-dom "file://$PWD/index.html?free=1&$v" > "$T/dom.html" 2>/dev/null
  err=$(grep -o 'data-errors="[^"]*"' "$T/dom.html" | head -1)
  if [ -z "$err" ] || [ "$err" = 'data-errors=""' ]; then ok "render $v"; else bad "render $v $err"; fi
  grep -q "NaN" "$T/dom.html" && bad "NaN at $v"
done
exit $fail
