"""Build validated Champions masters from pinned, locally checked out sources.
Usage: python3 scripts/champions/generate.py SHOWDOWN CHAMPOUT RETRIEVED_AT
"""
from functools import lru_cache
import json
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SHOWDOWN, CHAMPOUT = map(Path, sys.argv[1:3])
UPDATED = sys.argv[3]

@lru_cache(maxsize=None)
def read(path):
    return json.loads(path.read_text())

def write(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n')

def ident(value):
    return re.sub('[^a-z0-9]', '', value.lower())

def commit(path):
    return subprocess.check_output(['git', '-C', str(path), 'rev-parse', 'HEAD'], text=True).strip()

source = json.loads(subprocess.check_output(['node', str(ROOT/'scripts/champions/export-showdown.cjs'), str(SHOWDOWN)]))
baseline = '77a3f3d'
masters = {name: json.loads(subprocess.check_output(['git','-C',str(ROOT),'show',f'{baseline}:data/v1/{name}.json'])) for name in ['pokemons','moves','abilities','types']}
# Normalize references, generated types and language maps together, preserving display names.
for relative in ['data/v1/pokemons.json','data/v1/language-maps/pokemons.json','generated-keys/pokemons.ts','language-map/pokemon-maps.ts']:
    path = ROOT / relative
    path.write_text(path.read_text().replace('"Type:Null"', '"TypeNull"'))
masters['pokemons'] = {('TypeNull' if k == 'Type:Null' else k):v for k,v in masters['pokemons'].items()}
aliases = {'Nidoran♀':'nidoranf','Nidoran♂':'nidoranm','Arceus-Normal':'arceus',
           'Meowstic-Mega':'meowsticmmega','Urshifu-Single-Strike':'urshifu',
           'Tatsugiri-Mega':'tatsugiricurlymega','Terapagos-Normal':'terapagos','Terapagos':'terapagosterastal'}
# The existing male mega key is retained; the female form has a separate learnset.
if 'Meowstic-F-Mega' not in masters['pokemons']:
    p = dict(masters['pokemons']['Meowstic-Mega'])
    p.update(en='Meowstic-F-Mega', ja='メガニャオニクス（メス）', baseForm='Meowstic-F')
    masters['pokemons']['Meowstic-F-Mega'] = p

mapped = {}
for kind, table in [('pokemons','species'), ('moves','moves')]:
    mapping = {}
    for key, entry in masters[kind].items():
        candidates = [aliases[key]] if key in aliases else [ident(key), ident(entry['en'])]
        matches = {candidate for candidate in candidates if candidate in source[table]}
        assert len(matches) == 1, (kind,key,matches)
        mapping[key] = matches.pop()
    duplicates = {sid: sorted(k for k,v in mapping.items() if v == sid) for sid in set(mapping.values()) if list(mapping.values()).count(sid) > 1}
    assert not duplicates or duplicates == {'arceus':['Arceus','Arceus-Normal'], 'urshifu':['Urshifu','Urshifu-Single-Strike']}, duplicates
    mapped[kind] = mapping
reverse_moves = {v:k for k,v in mapped['moves'].items()}
ability_names = {int(x['LabelName'].split('_')[-1]):x['OriginalText'] for x in read(CHAMPOUT/'rom-txt/jpn/tokusei.json')['mSDataSet']}
# Correct an existing display name; never create a second ability key.
masters['abilities']['WaveShield']['en'] = 'Aura Guard'
reverse_abilities = {ident(k):k for k in masters['abilities']}
reverse_abilities['auraguard'] = 'WaveShield'
changes = [{'master':'abilities','key':'WaveShield','field':'en','before':'Wave Shield','after':'Aura Guard','source':'https://github.com/projectpokemon/champout/blob/'+commit(CHAMPOUT)+'/rom-txt/usa/tokusei.json'}]

def update(kind,key,field,new):
    entry = masters[kind][key]
    old = entry.get(field)
    if old != new:
        changes.append({'master':kind,'key':key,'field':field,'before':old,'after':new,
                        'source':f'https://github.com/smogon/pokemon-showdown/tree/{commit(SHOWDOWN)}/data/mods/champions'})
        entry[field] = new

learnsets = {}
for key, sid in mapped['pokemons'].items():
    p = source['species'][sid]
    available = p['isNonstandard'] is None
    parent = p.get('battleOnly')
    if isinstance(parent, str): available = available and source['species'][ident(parent)]['isNonstandard'] is None
    masters['pokemons'][key]['champions'] = available
    if not available:
        learnsets[key] = []
        continue
    for stat, field in [('hp','HP'),('atk','Atk'),('def','Def'),('spa','Spa'),('spd','Spd'),('spe','Spe')]:
        update('pokemons',key,field,p['baseStats'][stat])
    for field, value in [('types',p['types']),('weight',p['weightkg']),('abilities',list(dict.fromkeys(reverse_abilities[ident(a)] for slot,a in p['abilities'].items() if slot != 'S' and source['abilities'][ident(a)]['isNonstandard'] is None)))]:
        update('pokemons',key,field,value)
    current, visited = sid, set()
    while current not in source['learnsets'] or not source['learnsets'][current].get('learnset'):
        assert current not in visited, (key,visited)
        visited.add(current)
        form = source['species'][current]
        parent = form.get('changesFrom') or form.get('baseSpecies')
        assert parent and ident(parent) != current, f'No Champions learnset for {key}'
        current = ident(parent)
    moves = source['learnsets'][current]['learnset']
    learnsets[key] = sorted(reverse_moves[m] for m in moves)

# Keep OriginalText byte-for-byte in the masters; strip display tags only in the UI.
for kind, namefile, descfile in [('abilities','tokusei','tokuseiinfo_syn'),('moves','wazaname','wazainfo_syn')]:
    tables = {}
    for lang, directory in [('ja','jpn'),('en','usa')]:
        names = read(CHAMPOUT/f'rom-txt/{directory}/{namefile}.json')['mSDataSet']
        descriptions = read(CHAMPOUT/f'rom-txt/{directory}/{descfile}.json')['mSDataSet']
        descriptions = {x['LabelName'].split('_')[-1]: x['OriginalText'] for x in descriptions}
        if kind == 'moves':
            for move in read(CHAMPOUT/'masterdata/waza.json'):
                texts = read(CHAMPOUT/f"rom-txt/{directory}/{move['ms_name_info']}.json")['mSDataSet']
                text = next((x['OriginalText'] for x in texts if x['LabelName'] == move['ms_lbl_info']), '')
                descriptions[f"{int(move['id']):03}"] = text
        tables[lang] = {ident(x['OriginalText']) if lang == 'en' else x['OriginalText']: descriptions.get(x['LabelName'].split('_')[-1], '') for x in names}
    for key, entry in masters[kind].items():
        entry['description'] = {lang: tables[lang].get(ident(entry['en']) if lang == 'en' else entry['ja'], '') for lang in ['ja','en']}

# Showdown resolves the Champions PP cap and all inherited move fields.
targets = {'normal':'single','adjacentFoe':'single','any':'single','allAdjacent':'allAdjacent',
           'allAdjacentFoes':'allOpponents','all':'all','self':'self','adjacentAlly':'oneAlly',
           'adjacentAllyOrSelf':'userOrAlly','allies':'allAllies','allySide':'userField',
           'allyTeam':'allAllies','foeSide':'opponentField','randomNormal':'randomOpponent',
           'scripted':'varies'}
for key, sid in mapped['moves'].items():
    move = source['moves'][sid]
    entry = masters['moves'][key]
    entry['champions'] = move['isNonstandard'] is None
    if not entry['champions']: continue
    for field,value in [('type',move['type']),('power',move['basePower']),('accuracy',None if move['accuracy'] is True else move['accuracy']),('pp',move['pp']),('category',move['category'].lower()),('target',targets[move['target']]),('contact',bool(move['flags'].get('contact')))]:
        update('moves',key,field,value)
    if not entry['description']['en']:
        assert key == 'Struggle', f'Missing move description {key}'
        entry['supplement'] = {'en':source['moveText'][sid]['desc'], 'ja':''}
for key,moves in learnsets.items():
    assert all(masters['moves'][m]['champions'] for m in moves), key
for key,p in masters['pokemons'].items():
    assert type(p['champions']) is bool
    assert set(p['abilities']) <= masters['abilities'].keys(), key
    assert set(p['types']) <= masters['types'].keys(), key
    if p['champions']:
        assert all(masters['abilities'][a]['description']['en'] for a in p['abilities']), key
for kind,data in masters.items(): write(ROOT/f'data/v1/{kind}.json',data)
language_file = ROOT/'data/v1/language-maps/pokemons.json'
languages = read(language_file)
languages['Meowstic-F-Mega'] = {lang:masters['pokemons']['Meowstic-F-Mega'][lang] for lang in ['ja','en']}
write(language_file, languages)
ability_languages = read(ROOT/'data/v1/language-maps/abilities.json')
ability_languages['WaveShield']['en'] = 'Aura Guard'
write(ROOT/'data/v1/language-maps/abilities.json', ability_languages)
write(ROOT/'data/v1/learnset.json',learnsets)
chart = {defense: {attack: {0:1,1:2,2:0.5,3:0}[source['typeChart'][defense.lower()]['damageTaken'][attack]] for attack in masters['types']} for defense in masters['types']}
write(ROOT/'data/v1/type-chart.json', chart)
write(ROOT/'docs/champions/changes.json',changes)
write(ROOT/'docs/champions/sources.json', {'retrievedAt':UPDATED,'regulation':'M-C','showdown':{'url':'https://github.com/smogon/pokemon-showdown','commit':commit(SHOWDOWN)},'champout':{'url':'https://github.com/projectpokemon/champout','commit':commit(CHAMPOUT)},'baseline':baseline,'aliases':aliases,'abilityAliases':{'auraguard':'WaveShield'}})
print(f'{len(masters["pokemons"])} Pokémon, {sum(p["champions"] for p in masters["pokemons"].values())} available; {len(changes)} field changes')
