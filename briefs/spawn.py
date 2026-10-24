#!/usr/bin/env python3
"""Spawn one Opus builder thread per catalog entry. Usage: spawn.py catalog.json [slug ...]"""
import json, subprocess, sys, pathlib
ROOT = pathlib.Path('/home/nm/workspaces/how-things-work')
items = json.load(open(sys.argv[1]))
only = set(sys.argv[2:])
done = ROOT / 'briefs' / 'spawned.json'
spawned = json.load(open(done)) if done.exists() else {}
for it in items:
    s = it['slug']
    if (only and s not in only) or s in spawned or (ROOT/'figures'/s/'index.html').exists():
        continue
    brief = ROOT / 'briefs' / f'{s}.md'
    brief.write_text(f"""Build the Colorfigures figure for SLUG={s}. Read /home/nm/workspaces/how-things-work/briefs/COMMON.md first and follow it exactly.

Title: {it['title']}
Prompt (write this verbatim into meta.json "prompt"): {it['prompt']}
Source: {it['source']}, {it.get('sourceUrl') or '(our idea)'}
Category: {it['category']}
""")
    r = subprocess.run(['bb','thread','spawn','--parent-self','--project','proj_personal','--provider','claude-code',
        '--model','claude-opus-5-5','--reasoning-level','high','--permission-mode','full','--environment','env_zm6fsd4ykj',
        '--title',f'build: {s}','--prompt-file',str(brief),'--json'], capture_output=True, text=True, cwd=ROOT)
    try:
        tid = json.loads(r.stdout)['id']; spawned[s] = tid; print(s, tid)
    except Exception:
        print('FAIL', s, r.stdout[-200:], r.stderr[-200:])
    done.write_text(json.dumps(spawned, indent=1))
