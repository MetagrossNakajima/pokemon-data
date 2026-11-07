"""Cross-check each Champions form against Serebii's separate move tables.
Caches HTML outside the repository; records URL, hash, heading and exact set differences.
Usage: python3 scripts/champions/verify-serebii.py CACHE_DIRECTORY
"""
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
import hashlib
import html
import json
from pathlib import Path
import re
import sys
import time
from urllib.request import Request, urlopen

root = Path(__file__).resolve().parents[2]
cache = Path(sys.argv[1]); cache.mkdir(parents=True, exist_ok=True)
master = json.loads((root/'data/v1/pokemons.json').read_text())
moves = json.loads((root/'data/v1/moves.json').read_text())
learnsets = json.loads((root/'data/v1/learnsets.json').read_text())
def norm(s): return re.sub('[^a-z0-9]', '', s.lower())

def fetch(slug):
    path = cache/f'{slug}.html'
    url = f'https://www.serebii.net/pokedex-champions/{slug}/'
    if not path.exists():
        time.sleep(0.3)
        with urlopen(Request(url, headers={'User-Agent':'PokedexDataVerification/1.0'}), timeout=40) as response:
            path.write_bytes(response.read())
    body = path.read_bytes()
    return url, body

index = fetch('venusaur')[1].decode('utf-8', errors='replace')
slugs = {int(num):slug for slug,num in re.findall(r'<option value="/pokedex-champions/([^/]+)/">(\d+) ',index)}
nums = sorted({p['pokedex'] for p in master.values() if p['champions']})
def get_page(num):
    slug = slugs[num]
    url, body = fetch(slug)
    text = body.decode('utf-8', errors='replace')
    tables = []
    for table in re.findall(r'<table class="dextable">(.*?)</table>', text, re.S):
        heading = re.search(r'<h3>(.*?)</h3>',table,re.S)
        if not heading or 'Standard Moves' not in heading[1]: continue
        label = html.unescape(re.sub('<[^>]+>','',heading[1]))
        move_ids = {norm(x) for x in re.findall(r'href="/attackdex-champions/([^/.]+)\.shtml"',table)}
        tables.append((label,move_ids))
    if num == 479:
        standard = tables[0][1]
        for row in re.findall(r'<tr>(.*?)</tr>', text, re.S):
            move = re.search(r'href="/attackdex-champions/([^/.]+)\.shtml"', row)
            form = re.search(r'alt="(Heat|Wash|Frost|Fan|Mow) Rotom"', row)
            if move and form: tables.append(('Standard + Special Moves - ' + form[1], standard | {norm(move[1])}))
    assert tables, (num,url)
    return num, (url,hashlib.sha256(body).hexdigest(),tables)
with ThreadPoolExecutor(max_workers=4) as pool:
    pages = dict(pool.map(get_page, nums))
report=[]
for key,p in master.items():
    if not p['champions']: continue
    url,sha,tables=pages[p['pokedex']]
    expected={norm(moves[m]['en']) for m in learnsets[key]}
    label,actual=min(tables,key=lambda t:len(t[1]^expected))
    report.append({'key':key,'url':url,'sha256':sha,'table':label,'missingFromSerebii':sorted(expected-actual),'extraOnSerebii':sorted(actual-expected)})
output={'retrievedAt':datetime.now(timezone.utc).isoformat(), 'forms':report}
(root/'docs/champions/serebii-verification.json').write_text(json.dumps(output,ensure_ascii=False,indent=2)+'\n')
failures=[r for r in report if r['missingFromSerebii'] or r['extraOnSerebii']]
print(f'{len(report)} forms checked; {len(failures)} differences')
for r in failures:print(r)
sys.exit(bool(failures))
