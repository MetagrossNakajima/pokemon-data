"""data/v1 の各JSONファイルのキーからTypeScriptユニオン型を生成する"""

import os
import sys

sys.path.append(os.path.dirname(__file__))
from json_utils import load_json

DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "data", "v1")
OUTPUT_DIR = os.path.join(os.path.dirname(__file__), "..", "generated-keys")

HEADER = (
    "// このファイルは scripts/generate_union_types.py により自動生成されています\n"
    "// 手動で編集しないでください\n"
)

MAPPINGS = [
    ("types.json", "TypeName"),
    ("abilities.json", "AbilityName"),
    ("items.json", "ItemName"),
    ("natures.json", "NatureName"),
    ("moves.json", "MoveName"),
    ("pokemons.json", "PokemonName"),
]


def generate_union_type(type_name: str, keys: list[str]) -> str:
    lines = [f"export type {type_name} ="]
    for key in keys:
        lines.append(f'  | "{key}"')
    return "\n".join(lines)


def main():
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    for filename, type_name in MAPPINGS:
        filepath = os.path.join(DATA_DIR, filename)
        data = load_json(filepath)
        keys = list(data.keys())

        ts_filename = filename.replace(".json", ".ts")
        output_path = os.path.join(OUTPUT_DIR, ts_filename)

        content = HEADER + "\n" + generate_union_type(type_name, keys) + "\n"
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(content)

        print(f"Generated {output_path}")


if __name__ == "__main__":
    main()
