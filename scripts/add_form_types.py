import json
import os
import sys
from collections import Counter

sys.path.append(os.path.dirname(__file__))
from json_utils import load_json, save_json

DATA_PATH = os.path.join(os.path.dirname(__file__), '..', 'data', 'v1', 'pokemons.json')

# Keys that have hyphens but are base pokemon (not forms)
HYPHEN_BASE_NAMES = {
    'Ho-Oh', 'Porygon-Z',
    'Jangmo-o', 'Hakamo-o', 'Kommo-o',
    'Wo-Chien', 'Chien-Pao', 'Ting-Lu', 'Chi-Yu',
}

# Primal forms: key -> base_form
PRIMAL_FORMS = {
    'Groudon-Primal': 'Groudon',
    'Kyogre-Primal': 'Kyogre',
}

# Crowned forms: key -> base_form
CROWNED_FORMS = {
    'Zacian-Crowned': 'Zacian',
    'Zamazenta-Crowned': 'Zamazenta',
}

# Fusion forms: key -> base_form
FUSION_FORMS = {
    'Kyurem-White': 'Kyurem',
    'Kyurem-Black': 'Kyurem',
    'Necrozma-Dusk-Mane': 'Necrozma',
    'Necrozma-Dawn-Wings': 'Necrozma',
    'Calyrex-Ice': 'Calyrex',
    'Calyrex-Shadow': 'Calyrex',
}


def classify_form(key):
    """Returns (form_type, base_form) for a given key."""
    if key in HYPHEN_BASE_NAMES:
        return 'base', None

    if '-Mega' in key:
        base = key.split('-Mega')[0]
        return 'mega', base

    if key in PRIMAL_FORMS:
        return 'primal', PRIMAL_FORMS[key]

    if key in CROWNED_FORMS:
        return 'crowned', CROWNED_FORMS[key]

    if key in FUSION_FORMS:
        return 'fusion', FUSION_FORMS[key]

    if '-' not in key:
        return 'base', None

    # Check regional suffixes
    for suffix, region in [
        ('-Alola', 'alola'),
        ('-Galar', 'galar'),
        ('-Hisui', 'hisui'),
        ('-Paldea', 'paldea'),
    ]:
        if suffix in key:
            base = key.split(suffix)[0]
            return region, base

    # Everything else with a hyphen is a form variant
    parts = key.split('-')
    base = parts[0]
    return 'form', base


def insert_form_fields(entry, form_type, base_form):
    """Rebuild dict with formType/baseForm inserted right after pokedex."""
    new_entry = {}
    for k, v in entry.items():
        new_entry[k] = v
        if k == 'pokedex':
            new_entry['formType'] = form_type
            if base_form is not None:
                new_entry['baseForm'] = base_form
    return new_entry


def main():
    data = load_json(DATA_PATH)

    missing_bases = []
    new_data = {}

    for key, val in data.items():
        form_type, base_form = classify_form(key)
        new_entry = insert_form_fields(val, form_type, base_form)
        new_data[key] = new_entry

        if base_form is not None and base_form not in data:
            missing_bases.append((key, base_form))

    save_json(DATA_PATH, new_data)

    # Stats
    counts = Counter(v['formType'] for v in new_data.values())
    print("=== formType counts ===")
    for ft, c in sorted(counts.items(), key=lambda x: -x[1]):
        print(f"  {ft}: {c}")
    print(f"  Total: {sum(counts.values())}")

    if missing_bases:
        print(f"\nWARNING: {len(missing_bases)} entries reference missing baseForm:")
        for key, base in missing_bases:
            print(f"  {key} -> {base}")

    # Verify field order for a sample entry
    print("\n=== Field order check (Venusaur-Mega) ===")
    if 'Venusaur-Mega' in new_data:
        for k in new_data['Venusaur-Mega'].keys():
            print(f"  {k}")

    # Show examples
    print("\n=== Examples ===")
    examples = [
        'Venusaur', 'Venusaur-Mega', 'Raichu-Alola',
        'Rotom-Heat', 'Ponyta-Galar', 'Growlithe-Hisui',
        'Kyurem-White', 'Ho-Oh', 'Porygon-Z', 'Tauros-Paldea-Combat',
        'Meowstic-F', 'Calyrex-Shadow', 'Charizard-Mega-X',
    ]
    for k in examples:
        if k in new_data:
            v = new_data[k]
            base = v.get('baseForm', '-')
            print(f"  {k}: formType={v['formType']}, baseForm={base}")


if __name__ == '__main__':
    main()
