"""連番付きスプライトファイルをpokemons.jsonのフォルム名にリネームする."""

import json
import os
import re
from collections import defaultdict

SPRITES_DIR = os.path.join(os.path.dirname(__file__), "..", "icons", "v2")
POKEMONS_JSON = os.path.join(os.path.dirname(__file__), "..", "data", "v1", "pokemons.json")


def rename():
    with open(POKEMONS_JSON) as f:
        data = json.load(f)

    pokedex_groups = defaultdict(list)
    for name, info in data.items():
        pokedex_groups[info["pokedex"]].append(name)

    existing = set(os.listdir(SPRITES_DIR))
    numbered = sorted(f for f in existing if re.search(r"_\d+\.webp$", f))

    rename_map = []
    skipped = []
    conflicts = []

    for f in numbered:
        m = re.match(r"(.+)_(\d+)\.webp$", f)
        base_name = m.group(1)
        idx = int(m.group(2))

        if base_name not in data:
            skipped.append((f, "base not in JSON"))
            continue

        pdex = data[base_name]["pokedex"]
        forms = pokedex_groups[pdex]

        if idx >= len(forms):
            skipped.append((f, f"no form at index {idx}"))
            continue

        target_name = forms[idx]
        if target_name == base_name:
            skipped.append((f, "maps to base itself"))
            continue

        new_filename = f"{target_name}.webp"
        if new_filename in existing:
            conflicts.append((f, new_filename))
        else:
            rename_map.append((f, new_filename))

    # Report conflicts
    if conflicts:
        print("=== 衝突あり（スキップ） ===")
        for old, new in conflicts:
            print(f"  {old} -> {new} (既に存在)")
        print()

    # Execute renames
    for old, new in rename_map:
        os.rename(
            os.path.join(SPRITES_DIR, old),
            os.path.join(SPRITES_DIR, new),
        )

    print(f"リネーム完了: {len(rename_map)}件")
    print(f"衝突スキップ: {len(conflicts)}件")
    print(f"対応なし: {len(skipped)}件")

    remaining = sorted(f for f in os.listdir(SPRITES_DIR) if re.search(r"_\d+\.webp$", f))
    print(f"残り連番ファイル: {len(remaining)}件")
    print(f"総ファイル数: {len(os.listdir(SPRITES_DIR))}件")

    if rename_map:
        print("\n=== リネーム一覧 ===")
        for old, new in rename_map:
            print(f"  {old} -> {new}")


if __name__ == "__main__":
    rename()
