#!/usr/bin/env python3
"""Spawn one builder thread per catalog entry. Usage: spawn.py [--family claude|sol|alt] catalog.json [slug ...]
--family alt (default): even catalog index Claude, odd index Sol. Family per slug goes to briefs/families.json."""
import json, subprocess, sys, pathlib
ROOT = pathlib.Path('/home/nm/workspaces/how-things-work')
args = sys.argv[1:]
family = 'alt'
if args[0] == '--family':
    family, args = args[1], args[2:]
FAM = {'claude': ['--provider','claude-code','--model','claude-opus-5-5'], 'sol': ['--provider','codex','--model','gpt-6.1-sol']}
items = json.load(open(args[0]))
only = set(args[1:])
famfile = ROOT / 'briefs' / 'families.json'
families = json.load(open(famfile)) if famfile.exists() else {}
done = ROOT / 'briefs' / 'spawned.json'
spawned = json.load(open(done)) if done.exists() else {}
for i, it in enumerate(items):
    s = it['slug']
    fam = family if family != 'alt' else ('claude' if i % 2 == 0 else 'sol')
    if (only and s not in only) or s in spawned or (ROOT/'figures'/s/'index.html').exists():
        continue
    brief = ROOT / 'briefs' / f'{s}.md'
    brief.write_text(f"""Build the Colorfigures figure for SLUG={s}. Read /home/nm/workspaces/how-things-work/briefs/COMMON.md first and follow it exactly.

Title: {it['title']}
Prompt (write this verbatim into meta.json "prompt"): {it['prompt']}
Source: {it['source']}, {it.get('sourceUrl') or '(our idea)'}
Category: {it['category']}
""")
    r = subprocess.run(['bb','thread','spawn','--parent-self','--project','proj_personal',*FAM[fam],
        '--reasoning-level','high','--permission-mode','full','--environment','env_zm6fsd4ykj',
        '--title',f'build: {s}','--prompt-file',str(brief),'--json'], capture_output=True, text=True, cwd=ROOT)
    try:
        tid = json.loads(r.stdout)['id']; spawned[s] = tid; families[s] = fam; print(s, fam, tid)
    except Exception:
        print('FAIL', s, r.stdout[-200:], r.stderr[-200:])
    done.write_text(json.dumps(spawned, indent=1))
    famfile.write_text(json.dumps(families, indent=1))
