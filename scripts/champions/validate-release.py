"""Validate the release without fetching any upstream data. Used before R2 publication."""
import hashlib
import json
from pathlib import Path

root=Path(__file__).resolve().parents[2]
manifest=json.loads((root/'data/pokedex/manifest.json').read_text())
assert manifest['formatVersion']==1
version=manifest['dataVersion']
assert manifest['url']==f'https://poke-data-r2.terurun.jp/data/pokedex/{version}.json'
body=(root/f'data/pokedex/{version}.json').read_bytes()
assert hashlib.sha256(body).hexdigest()==manifest['sha256']
data=json.loads(body)
assert all(data[k]==manifest[k] for k in ['formatVersion','dataVersion','updatedAt'])
assert 'TypeNull' in data['pokemons'] and 'Type:Null' not in data['pokemons']
assert data['learnsets'].keys()==data['pokemons'].keys()
for key,p in data['pokemons'].items():
    assert type(p['champions']) is bool, key
    assert set(p['abilities'])<=data['abilities'].keys(), key
    assert set(p['types'])<=data['types'].keys(), key
    assert p['champions'] or not data['learnsets'][key], key
    for m in data['learnsets'][key]: assert data['moves'][m]['champions'], (key,m)
for key,m in data['moves'].items():
    assert type(m['champions']) is bool,key
    assert m['type'] in data['types'],key
    assert 'ja' in m['description'] and 'en' in m['description'],key
assert data['abilities']['WaveShield']['en']=='Aura Guard'
assert data['moves']['Protect']['pp']==5
assert data['learnsets']['Meowstic'] != data['learnsets']['Meowstic-F']
assert data['learnsets']['Meowstic-Mega'] == data['learnsets']['Meowstic']
assert data['learnsets']['Meowstic-F-Mega'] == data['learnsets']['Meowstic-F']
assert len(data['typeChart'])==18
print(f'Validated {version}: {len(data["pokemons"])} Pokémon, {len(data["moves"])} moves, {manifest["sha256"]}')
