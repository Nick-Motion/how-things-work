#!/usr/bin/env python3
"""Assemble site/ from figures/*/ : index.html + copies of each figure and its front shot."""
import json, pathlib, shutil, html
ROOT = pathlib.Path(__file__).parent
OUT = ROOT / 'site'
figs = []
for d in sorted((ROOT / 'figures').iterdir()):
    meta, built = d / 'meta.json', d / 'index.html'
    if not (meta.exists() and built.exists()):
        continue
    m = json.load(open(meta)); m['slug'] = d.name
    dst = OUT / 'f' / d.name; dst.mkdir(parents=True, exist_ok=True)
    shutil.copy(built, dst / 'index.html')
    shot = d / 'shots' / 'front.png'
    if shot.exists():
        shutil.copy(shot, dst / 'front.png'); m['shot'] = f'f/{d.name}/front.png'
    figs.append(m)

ORDER = ['kitchen','home','street','play','music','workshop','electronics','transport','science','other']
SRC = {'site': "From April Zhu's examples", 'x': 'Seen on X', 'original': 'Our own'}
figs.sort(key=lambda m: (ORDER.index(m.get('category','other')) if m.get('category') in ORDER else 99, m['title']))

def card(m):
    img = f'<img src="{m["shot"]}" alt="" loading="lazy">' if m.get('shot') else '<div class="noshot"></div>'
    btns = ' · '.join(html.escape(b) for b in m.get('buttons', []))
    return f'''<a class="card" href="f/{m['slug']}/" data-cat="{m.get('category','other')}" data-src="{m.get('source','')}">
  {img}
  <h2>{html.escape(m['title'])}</h2>
  <p>{html.escape(m.get('blurb',''))}</p>
  <small>{btns}</small>
</a>'''

cats = [c for c in ORDER if any(m.get('category') == c for m in figs)]
filters = ''.join(f'<button data-f="{c}">{c}</button>' for c in cats)
page = f'''<!doctype html><html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>How Things Work</title>
<meta name="description" content="{len(figs)} hand-inked isometric machines you can turn round, see inside and play with.">
<style>
:root{{--paper:#f6f0e4;--ink:#2b2a28;--mute:#7a7369;--acc:#e2483d}}
*{{box-sizing:border-box}}body{{margin:0;background:var(--paper);color:var(--ink);font:16px/1.45 Georgia,'Iowan Old Style',serif}}
header{{padding:48px 24px 16px;max-width:1200px;margin:auto}}h1{{font-size:44px;margin:0 0 8px;letter-spacing:-.01em}}
header p{{margin:0;color:var(--mute);max-width:60ch}}header a{{color:inherit}}
nav{{max-width:1200px;margin:16px auto 0;padding:0 24px;display:flex;gap:8px;flex-wrap:wrap}}
nav button{{font:inherit;font-size:14px;border:2px solid var(--ink);background:none;border-radius:999px;padding:4px 12px;cursor:pointer}}
nav button.on{{background:var(--ink);color:var(--paper)}}
main{{max-width:1200px;margin:24px auto 80px;padding:0 24px;display:grid;grid-template-columns:repeat(auto-fill,minmax(260px,1fr));gap:20px}}
.card{{display:block;color:inherit;text-decoration:none;background:#fff;border:2.5px solid var(--ink);border-radius:14px;padding:14px;box-shadow:6px 6px 0 #9fc3d6;transition:transform .12s}}
.card:hover{{transform:translate(-2px,-2px);box-shadow:8px 8px 0 #9fc3d6}}
.card img,.noshot{{width:100%;aspect-ratio:9/8;object-fit:cover;border-radius:8px;background:#efe7d6}}
.card h2{{font-size:20px;margin:12px 0 4px}}.card p{{margin:0;color:var(--mute);font-size:14px}}
.card small{{display:block;margin-top:8px;color:var(--acc);font-size:12px;text-transform:uppercase;letter-spacing:.04em}}
.card[hidden]{{display:none}}footer{{text-align:center;color:var(--mute);padding:24px;font-size:14px}}
</style></head><body>
<header><h1>How Things Work</h1>
<p>{len(figs)} everyday machines, hand-inked and isometric. Drag one to turn it round, switch on See-through to watch the mechanism, press the buttons. Built with <a href="https://april-zhu.com/colorfigures">Colorfigures</a> by April Zhu.</p></header>
<nav><button data-f="" class="on">all</button>{filters}</nav>
<main>{''.join(card(m) for m in figs)}</main>
<footer>Each figure is one self-contained HTML file. No tracking, no accounts. <a href="https://github.com/Nick-Motion/how-things-work">Source</a>.</footer>
<script>
document.querySelector('nav').onclick=e=>{{const b=e.target.closest('button');if(!b)return;
document.querySelectorAll('nav button').forEach(x=>x.classList.toggle('on',x===b));
document.querySelectorAll('.card').forEach(c=>c.hidden=b.dataset.f&&c.dataset.cat!==b.dataset.f)}};
</script></body></html>'''
OUT.mkdir(exist_ok=True)
(OUT / 'index.html').write_text(page)
(OUT / 'figures.json').write_text(json.dumps(figs, indent=1))
print(len(figs), 'figures')
