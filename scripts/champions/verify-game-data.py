"""Verify available numerical data against champout masterdata, with representation conversions.
Usage: python3 scripts/champions/verify-game-data.py SHOWDOWN CHAMPOUT
"""
import json
import re
import subprocess
import sys
from pathlib import Path
root=Path(__file__).resolve().parents[2]
showdown,champout=map(Path,sys.argv[1:3])
source=json.loads(subprocess.check_output(['node',str(root/'scripts/champions/export-showdown.cjs'),str(showdown)]))
master={k:json.loads((root/f'data/v1/{k}.json').read_text()) for k in ['pokemons','moves','abilities']}
def norm(s):return re.sub('[^a-z0-9]','',s.lower())
rom_moves={int(x['id']):x for x in json.loads((champout/'masterdata/waza.json').read_text())}
rom_pokemon=json.loads((champout/'masterdata/personal.json').read_text())
types=['Normal','Fighting','Flying','Poison','Ground','Rock','Bug','Ghost','Steel','Fire','Water','Grass','Electric','Psychic','Ice','Dragon','Dark','Fairy']
ability_names={int(x['LabelName'].split('_')[-1]):x['OriginalText'] for x in json.loads((champout/'rom-txt/usa/tokusei.json').read_text())['mSDataSet']}
report={'pokemon':{},'moves':{},'notes':['Game PP is maximum PP: (base // 5 + 1) * 4, except noPPBoosts.', 'Accuracy 101 denotes always-hit; variable/fixed damage power 1 corresponds to the existing zero base-power representation.']}
errors=[]
for key,p in master['pokemons'].items():
 if not p['champions']:continue
 matches=[]
 for r in rom_pokemon:
  if int(r['no'])!=p['pokedex']:continue
  if [int(r[f]) for f in ['hp','atk','def','spatk','spdef','agi']] != [p[f] for f in ['HP','Atk','Def','Spa','Spd','Spe']]:continue
  if list(dict.fromkeys(types[int(r[f])] for f in ['type1','type2'])) != p['types']:continue
  if abs(int(r['weight'])/10-p['weight'])>0.001:continue
  actual={ability_names[int(r[f])] for f in ['toku0','toku1','toku2']}
  expected={master['abilities'][a]['en'] for a in p['abilities']}
  if actual!=expected:continue
  matches.append(r['id'])
 if not matches:errors.append(('pokemon',key))
 report['pokemon'][key]=matches
for key,m in master['moves'].items():
 if not m['champions']:continue
 sm=source['moves'].get(norm(m['en'])) or source['moves'][norm(key)]
 r=rom_moves.get(sm['num'])
 if not r:
  assert key=='Struggle', key
  report['moves'][key]='automatic fallback move; no masterdata row'
  continue
 for f in ['power','accuracy','pp']:
  actual=m.get(f);expected=int(r[f])
  if f=='pp':actual=actual if sm.get('noPPBoosts') else (actual//5+1)*4
  if f=='accuracy' and actual is None:actual=101
  if f=='power' and actual==0 and expected==1:continue
  if actual!=expected:errors.append((key,f,actual,expected))
 if m['type']!=types[int(r['type'])]:errors.append((key,'type'))
 if m['category']!=['physical','special','status'][int(r['category'])]:errors.append((key,'category'))
 if m['contact']!=bool(int(r['direct'])):errors.append((key,'contact'))
 report['moves'][key]=r['id']
report['differences']=errors
(root/'docs/champions/game-data-verification.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
print(f'{len(report["pokemon"])} Pokémon and {len(report["moves"])} moves compared; {len(errors)} differences')
print(errors)
sys.exit(bool(errors))
