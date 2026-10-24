#!/usr/bin/env bash
# Coordinator spot-check of one built figure. Exit 0 = pass. Prints one line per check.
set -u
usage(){ echo "Usage: verify_figure.sh <slug> [minimum-labels]" >&2; echo "minimum-labels must be a positive integer (default 25); declare book overrides in the figure brief." >&2; exit 2; }
[ "$#" -ge 1 ] && [ "$#" -le 2 ] && [ -n "$1" ] || usage
minimum=${2-25}
[[ "$minimum" =~ ^[0-9]+$ && "$minimum" =~ [1-9] ]] || usage
cd "$(dirname "$0")/figures/$1" || exit 2
fail=0; ok(){ echo "ok   $1"; }; bad(){ echo "FAIL $1"; fail=1; }
for f in index.html figure.html core.js meta.json shots/front.png shots/xray.png; do [ -s "$f" ] && ok "$f present" || bad "$f missing"; done
python3 -I - <<'EOF' || fail=1
import json,sys
m=json.load(open('meta.json'))
need={'title','prompt','source','category','buttons','blurb'}
missing=need-m.keys(); print(('FAIL meta missing '+','.join(missing)) if missing else 'ok   meta fields')
buttons=m.get('buttons',[])
valid_buttons=isinstance(buttons,list) and 2<=len(buttons)<=6
print('ok   buttons %d'%len(buttons) if valid_buttons else 'FAIL buttons must contain 2..6 labels')
sys.exit(1 if missing or not valid_buttons else 0)
EOF
grep -q "turn:'full'\|turn: 'full'\|turn:\"full\"" index.html && ok "turn:full" || bad "turn:full missing"
grep -q "xrMount" index.html && ok "see-through wired" || bad "no xrMount"
labels=0
grep -q "<script src=\"core.js\"" index.html && bad "index.html not built (still loads core.js)" || ok "self-contained"
T=$(mktemp -d /tmp/vf.XXXXXX) || exit 2
trap 'rm -rf -- "$T"' EXIT
trap 'exit 130' INT
trap 'exit 143' TERM
for v in "yaw=45" "yaw=200" "yaw=300&xr=1&labels=1" "yaw=110&xr=1&labels=1"; do
  profile=$(mktemp -d "$T/p.XXXXXX") || exit 2
  if ! timeout --kill-after=5s 30s chromium --headless=new --no-sandbox --hide-scrollbars --user-data-dir="$profile" --window-size=900,800 \
    --virtual-time-budget=3000 --dump-dom "file://$PWD/index.html?free=1&$v" > "$T/dom.html" 2>/dev/null; then
    bad "render $v Chromium failed or timed out"; continue
  fi
  [ -s "$T/dom.html" ] || { bad "render $v empty DOM"; continue; }
  python3 -I - "$T/dom.html" > "$T/render.html" <<'EOF' || { bad "render $v DOM parse failed"; continue; }
from html.parser import HTMLParser
import sys
class Rendered(HTMLParser):
    source = False
    def handle_starttag(self, tag, attrs):
        if tag in ('script', 'style'):
            self.source = True
        elif not self.source:
            print(self.get_starttag_text())
    def handle_endtag(self, tag):
        if tag in ('script', 'style'):
            self.source = False
    def handle_data(self, data):
        if not self.source:
            print(data)
Rendered().feed(open(sys.argv[1]).read())
EOF
  err=$(grep -o 'data-errors="[^"]*"' "$T/render.html" | head -1)
  if [ "$err" = 'data-errors=""' ]; then ok "render $v"; else bad "render $v ${err:-missing data-errors marker}"; fi
  sed 's/data:image[^"'"'"']*//g' "$T/render.html" | grep -q "NaN" && bad "NaN at $v"
  n=$(grep -o 'data-t="[^"]*"' "$T/render.html" | sort -u | wc -l); [ "$n" -gt "$labels" ] && labels=$n
done
python3 -I - "$labels" "$minimum" <<'EOF' || fail=1
import sys
labels, minimum = map(int, sys.argv[1:])
print(('ok   ' if labels >= minimum else 'FAIL ') + f'labels rendered {labels} (minimum {minimum})')
sys.exit(0 if labels >= minimum else 1)
EOF
exit $fail
