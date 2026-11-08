"""Validate the release without fetching any upstream data. Used before R2 publication."""
import json
from pathlib import Path

root=Path(__file__).resolve().parents[2]
data = {name: json.loads((root/f'data/v1/{name}.json').read_text()) for name in ['pokemons', 'moves', 'abilities', 'types']}
data['learnsets'] = json.loads((root/'data/v1/learnset.json').read_text())
data['typeChart'] = json.loads((root/'data/v1/type-chart.json').read_text())
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
assert data['typeChart'].keys() == data['types'].keys()
for row in data['typeChart'].values():
    assert row.keys() == data['types'].keys()
    assert all(value in (0, 0.5, 1, 2) for value in row.values())
print(f'Validated {len(data["pokemons"])} Pokémon, {len(data["moves"])} moves')
