import csv
import os
import re
import sys
from collections import defaultdict

sys.path.append(os.path.dirname(__file__))
from json_utils import load_json, save_json

DATA_DIR = os.path.join(os.path.dirname(__file__), '..', 'data', 'v1')
POKEMONS_PATH = os.path.join(DATA_DIR, 'pokemons.json')
ABILITIES_PATH = os.path.join(DATA_DIR, 'abilities.json')
CSV_PATH = os.path.join(os.path.dirname(__file__), '..', 'docs', 'pokemon-abilities.csv')

# CSV form names that have no corresponding entry in pokemons.json
SKIP_FORMS = {
    (25, 'おきがえピカチュウ'),
    (172, 'ギザみみピチュー'),
    (658, '特殊個体'),
    (718, '10%フォルム'),
    (718, 'パーフェクトフォルム'),
    (744, '特殊個体'),
    (800, 'ウルトラネクロズマ'),
    (1017, 'テラスタル時'),
}

# Mapping from CSV form description to pokemons.json ja substring/pattern
# For forms where the CSV name doesn't directly map
FORM_NAME_MAP = {
    # Region forms: CSV uses "のすがた", JSON uses short form in parentheses
    'アローラのすがた': 'アローラ',
    'ガラルのすがた': 'ガラル',
    'ヒスイのすがた': 'ヒスイ',
    'パルデアのすがた': 'パルデア',
    # Giratina
    'アナザーフォルム': 'アナザー',
    'オリジンフォルム': 'オリジン',
    # Shaymin
    'ランドフォルム': 'ランド',
    'スカイフォルム': 'スカイ',
    # Basculin
    'あかすじのすがた': '赤',
    'あおすじのすがた': '青',
    'しろすじのすがた': '白',
    # Tornadus/Thundurus/Landorus/Enamorus
    'けしんフォルム': '化身',
    'れいじゅうフォルム': '霊獣',
    # Kyurem
    'キュレムのすがた': '通常',
    'ホワイトキュレム': 'ホワイトキュレム',
    'ブラックキュレム': 'ブラックキュレム',
    # Meowstic / Indeedee / Oinkologne
    'オスのすがた': '♂',
    'メスのすがた': '♀',
    # Toxtricity
    'ハイなすがた': 'ハイ',
    'ローなすがた': 'ロー',
    # Calyrex
    'はくばじょうのすがた': '白',
    'こくばじょうのすがた': '黒',
    # Ursaluna
    'アカツキ': 'アカツキ',
    # Lycanroc
    'まひるのすがた': '昼',
    'まよなかのすがた': '夜',
    'たそがれのすがた': '黄昏',
    # Necrozma
    'たそがれのたてがみ': '日食',
    'あかつきのつばさ': '月食',
    # Zygarde 50% = base form
    '50%フォルム': 'ジガルデ',
    # Ogerpon
    'みどりのめん': '草',
    'いどのめん': '水',
    'かまどのめん': '炎',
    'いしずえのめん': '岩',
    # Terapagos
    'ノーマルフォルム': 'ノーマル',
    'テラスタルフォルム': 'テラパゴス',  # base Terapagos (ja: テラパゴス)
    'ステラフォルム': 'ステラ',
    # Squawkabilly / Gimmighoul: single entry in JSON, all forms map to it
    'グリーンフェザー': None,
    'ブルーフェザー': None,
    'イエローフェザー': None,
    'ホワイトフェザー': None,
    'はこフォルム': None,
    'とほフォルム': None,
}

# ZA/M次元ラッシュ megas: abilities not yet announced, force empty
FORCE_EMPTY_ABILITIES = {
    # Pokemon ZA (25)
    'Clefable-Mega', 'Victreebel-Mega', 'Starmie-Mega', 'Dragonite-Mega',
    'Meganium-Mega', 'Feraligatr-Mega', 'Skarmory-Mega', 'Froslass-Mega',
    'Emboar-Mega', 'Excadrill-Mega', 'Scolipede-Mega', 'Scrafty-Mega',
    'Eelektross-Mega', 'Chandelure-Mega',
    'Pyroar-Mega', 'Floette-Mega', 'Malamar-Mega',
    'Barbaracle-Mega', 'Dragalge-Mega', 'Hawlucha-Mega', 'Zygarde-Mega',
    'Drampa-Mega', 'Falinks-Mega', 'Crabominable-Mega',
    # M次元ラッシュ (18)
    'Raichu-Mega-X', 'Raichu-Mega-Y', 'Chimecho-Mega', 'Lucario-Mega-Z',
    'Absol-Mega-Z', 'Staraptor-Mega', 'Tatsugiri-Mega', 'Meowstic-Mega',
    'Heatran-Mega', 'Golurk-Mega', 'Golisopod-Mega', 'Scovillain-Mega',
    'Glimmora-Mega', 'Darkrai-Mega', 'Magearna-Mega', 'Zeraora-Mega',
    'Baxcalibur-Mega',
}

# Missing abilities to add to abilities.json
MISSING_ABILITIES = {
    'TeraShift': {'ja': 'テラスチェンジ', 'en': 'Tera Shift'},
    'TeraShell': {'ja': 'テラスシェル', 'en': 'Tera Shell'},
    'ZeroForming': {'ja': 'ゼロフォーミング', 'en': 'Zero Forming'},
}


def clean_ability_name(name):
    """Remove annotations like *4, [1], [17] from ability names."""
    return re.sub(r'[\*\[].*$', '', name).strip()


def build_ja_to_key_map(abilities):
    """Build reverse lookup: ja name -> ability key."""
    ja_to_key = {}
    for key, val in abilities.items():
        ja_to_key[val['ja']] = key
    return ja_to_key


def build_pokedex_index(pokemons):
    """Build pokedex number -> [(key, ja_name)] index."""
    index = defaultdict(list)
    for key, val in pokemons.items():
        index[val['pokedex']].append((key, val['ja']))
    return index


def parse_csv(csv_path):
    """Parse CSV and return list of (pokedex, base_name, form_name_or_None, abilities)."""
    rows = []
    with open(csv_path, 'r', encoding='utf-8') as f:
        reader = csv.reader(f)
        for row in reader:
            if len(row) < 3:
                continue
            pokedex_str = row[0].strip()
            if not pokedex_str:
                continue  # Skip unreleased pokemon (empty pokedex)
            pokedex = int(pokedex_str)
            name_field = row[1]
            abilities_raw = [row[i].strip() if i < len(row) else '' for i in range(2, 5)]
            abilities_clean = [clean_ability_name(a) for a in abilities_raw]

            if '\n' in name_field:
                parts = name_field.split('\n')
                base_name = parts[0].strip()
                # Extract form name from parentheses
                form_part = parts[1].strip()
                form_name = form_part.strip('()')
                rows.append((pokedex, base_name, form_name, abilities_clean))
            else:
                base_name = name_field.strip()
                rows.append((pokedex, base_name, None, abilities_clean))
    return rows


def match_form_to_entry(pokedex, base_name, form_name, pokedex_index):
    """Match a CSV form variant to pokemons.json entries. Returns list of keys, ['SKIP'], or []."""
    entries = pokedex_index.get(pokedex, [])
    if not entries:
        return []

    # Check if this form should be skipped
    if (pokedex, form_name) in SKIP_FORMS:
        return ['SKIP']

    # Mega forms: form_name starts with メガ or ゲンシ
    if form_name.startswith('メガ') or form_name.startswith('ゲンシ'):
        for key, ja in entries:
            if ja == form_name:
                return [key]
        return []

    # Look up form name mapping
    if form_name in FORM_NAME_MAP:
        mapped = FORM_NAME_MAP[form_name]

        # None means map to the single/first entry with this pokedex
        if mapped is None:
            if len(entries) == 1:
                return [entries[0][0]]
            # Return first base-form entry
            for key, ja in entries:
                if '-' not in key or key in ('Ho-Oh', 'Porygon-Z', 'Jangmo-o',
                                              'Hakamo-o', 'Kommo-o', 'Wo-Chien',
                                              'Chien-Pao', 'Ting-Lu', 'Chi-Yu'):
                    return [key]
            return [entries[0][0]]

        # Special case: Zygarde 50% maps to base Zygarde (ja == 'ジガルデ')
        if form_name == '50%フォルム':
            for key, ja in entries:
                if ja == 'ジガルデ':
                    return [key]
            return []

        # Special case: Terapagos テラスタルフォルム maps to base (ja == 'テラパゴス')
        if form_name == 'テラスタルフォルム':
            for key, ja in entries:
                if ja == 'テラパゴス':
                    return [key]
            return []

        # Special case: Kyurem ホワイトキュレム/ブラックキュレム - exact ja match
        if mapped in ('ホワイトキュレム', 'ブラックキュレム'):
            for key, ja in entries:
                if ja == mapped:
                    return [key]
            return []

        # For region forms, match ALL entries containing mapped string
        matched = [key for key, ja in entries if mapped in ja]
        return matched

    # Fallback: try to match form_name in ja
    for key, ja in entries:
        if form_name in ja:
            return [key]
    return []


def match_base_to_entry(pokedex, base_name, pokedex_index, pokemons):
    """Match a base CSV entry to a pokemons.json entry. Returns key or None."""
    entries = pokedex_index.get(pokedex, [])
    if not entries:
        return None

    # Exact ja match
    for key, ja in entries:
        if ja == base_name:
            return key

    # Match ja that starts with base_name
    # Prefer formType=base entries, then shortest ja
    candidates = [(key, ja) for key, ja in entries if ja.startswith(base_name)]
    if candidates:
        # Prefer base formType
        base_candidates = [c for c in candidates if pokemons[c[0]].get('formType') == 'base']
        if base_candidates:
            base_candidates.sort(key=lambda x: len(x[1]))
            return base_candidates[0][0]
        candidates.sort(key=lambda x: len(x[1]))
        return candidates[0][0]

    # Some base entries contain base_name
    for key, ja in entries:
        if base_name in ja:
            return key

    # Single entry: just use it
    if len(entries) == 1:
        return entries[0][0]

    return None


def build_abilities_array(ability_names, ja_to_key):
    """Convert ja ability names to ability keys, skipping empty ones."""
    result = []
    unknown = []
    for name in ability_names:
        if not name:
            continue
        if name in ja_to_key:
            key = ja_to_key[name]
            if key not in result:
                result.append(key)
        else:
            unknown.append(name)
    return result, unknown


def insert_abilities(entry, abilities_list):
    """Rebuild dict with abilities inserted after types."""
    new_entry = {}
    for k, v in entry.items():
        new_entry[k] = v
        if k == 'types':
            new_entry['abilities'] = abilities_list
    # If 'types' key was not found, append at end
    if 'abilities' not in new_entry:
        new_entry['abilities'] = abilities_list
    return new_entry


def main():
    # Step 1: Add missing abilities
    abilities = load_json(ABILITIES_PATH)
    for key, val in MISSING_ABILITIES.items():
        if key not in abilities:
            abilities[key] = val
            print(f"Added missing ability: {key} ({val['ja']})")
    save_json(ABILITIES_PATH, abilities)

    # Build reverse lookup
    ja_to_key = build_ja_to_key_map(abilities)

    # Load pokemons
    pokemons = load_json(POKEMONS_PATH)
    pokedex_index = build_pokedex_index(pokemons)

    # Parse CSV
    csv_rows = parse_csv(CSV_PATH)

    # Track which pokemon keys got abilities assigned
    assigned = {}
    unmatched_csv = []
    unknown_abilities = []
    all_forms_apply = []

    for pokedex, base_name, form_name, ability_names in csv_rows:
        abilities_list, unknowns = build_abilities_array(ability_names, ja_to_key)
        if unknowns:
            unknown_abilities.extend([(pokedex, base_name, form_name, u) for u in unknowns])

        if form_name is not None:
            # Form variant
            matched_keys = match_form_to_entry(pokedex, base_name, form_name, pokedex_index)
            if matched_keys == ['SKIP']:
                continue
            if matched_keys:
                for mk in matched_keys:
                    assigned[mk] = abilities_list
            else:
                unmatched_csv.append((pokedex, base_name, form_name))
        else:
            # Base form
            matched_key = match_base_to_entry(pokedex, base_name, pokedex_index, pokemons)
            if matched_key:
                assigned[matched_key] = abilities_list
                # For pokemon like Deoxys, Rotom where a single CSV row
                # should apply to all forms with the same pokedex
                entries = pokedex_index.get(pokedex, [])
                entries_without_abilities = [
                    (k, ja) for k, ja in entries
                    if k not in assigned and k != matched_key
                ]
                # Only auto-apply if there are multiple entries and
                # no form-specific CSV rows will follow
                # We check this by seeing if any form variants exist in CSV for this pokedex
                has_form_rows = any(
                    p == pokedex and f is not None
                    for p, _, f, _ in csv_rows
                )
                if not has_form_rows and len(entries) > 1:
                    for k, ja in entries_without_abilities:
                        assigned[k] = abilities_list
                        all_forms_apply.append((k, ja))
            else:
                unmatched_csv.append((pokedex, base_name, None))

    # Force empty abilities for ZA/M次元ラッシュ megas (abilities not yet announced)
    for key in FORCE_EMPTY_ABILITIES:
        if key in pokemons:
            assigned[key] = []

    # Apply abilities to pokemons.json
    new_pokemons = {}
    no_abilities = []
    for key, val in pokemons.items():
        if key in assigned:
            new_pokemons[key] = insert_abilities(val, assigned[key])
        else:
            new_pokemons[key] = insert_abilities(val, [])
            no_abilities.append(key)

    save_json(POKEMONS_PATH, new_pokemons)

    # Report
    print(f"\n=== Results ===")
    print(f"Total pokemon entries: {len(pokemons)}")
    print(f"Matched with abilities: {len(assigned)}")
    print(f"No abilities (empty array): {len(no_abilities)}")

    if all_forms_apply:
        print(f"\n=== Auto-applied to all forms ({len(all_forms_apply)}) ===")
        for k, ja in all_forms_apply:
            print(f"  {k} ({ja})")

    if unmatched_csv:
        print(f"\n=== Unmatched CSV rows ({len(unmatched_csv)}) ===")
        for pdx, name, form in unmatched_csv:
            form_str = f" ({form})" if form else ""
            print(f"  #{pdx} {name}{form_str}")

    if unknown_abilities:
        print(f"\n=== Unknown abilities ({len(unknown_abilities)}) ===")
        for pdx, name, form, ability in unknown_abilities:
            form_str = f" ({form})" if form else ""
            print(f"  #{pdx} {name}{form_str}: {ability}")

    if no_abilities:
        print(f"\n=== Pokemon with empty abilities ({len(no_abilities)}) ===")
        for k in no_abilities:
            ja = pokemons[k].get('ja', '')
            print(f"  {k} ({ja})")

    # Sample verification
    print("\n=== Verification samples ===")
    samples = ['Bulbasaur', 'Venusaur-Mega', 'Raichu-Alola', 'Deoxys', 'Deoxys-Attack',
               'Rotom', 'Rotom-Heat', 'Ogerpon', 'Terapagos', 'Zygarde']
    for k in samples:
        if k in new_pokemons:
            ab = new_pokemons[k].get('abilities', [])
            print(f"  {k}: {ab}")

    # Field order check
    print("\n=== Field order check (Bulbasaur) ===")
    if 'Bulbasaur' in new_pokemons:
        for k in new_pokemons['Bulbasaur'].keys():
            print(f"  {k}")


if __name__ == '__main__':
    main()
