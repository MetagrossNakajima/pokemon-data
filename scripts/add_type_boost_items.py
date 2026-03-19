import sys
import os

sys.path.append(os.path.dirname(__file__))
from json_utils import load_json, save_json

DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "data", "v1")
REFERENCE_PATH = os.path.join(os.path.dirname(__file__), "..", "reference", "plate.txt")

TYPE_JA_TO_EN = {
    "ノーマル": "Normal",
    "ほのお": "Fire",
    "みず": "Water",
    "くさ": "Grass",
    "でんき": "Electric",
    "こおり": "Ice",
    "かくとう": "Fighting",
    "どく": "Poison",
    "じめん": "Ground",
    "ひこう": "Flying",
    "エスパー": "Psychic",
    "むし": "Bug",
    "いわ": "Rock",
    "ゴースト": "Ghost",
    "ドラゴン": "Dragon",
    "あく": "Dark",
    "はがね": "Steel",
    "フェアリー": "Fairy",
}

# reference/plate.txt の表記 → items.json の ja 名
NAME_FIXES = {
    "きせきのたね": "きせきのタネ",
    "くろいめがね": "くろいメガネ",
    "しるくのスカーフ": "シルクのスカーフ",
    "どくばり": "どくバリ",
    "くろおび": "くろおび",
}


def load_entries(path):
    entries = []
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            if "\t" in line:
                parts = line.split("\t")
            else:
                parts = line.rsplit(None, 1)
            if len(parts) == 2:
                name, type_ja = parts[0].strip(), parts[1].strip()
                is_plate = "プレート" in name
                entries.append((name, type_ja, is_plate))
    return entries


def main():
    items = load_json(os.path.join(DATA_DIR, "items.json"))

    # まっさらプレートを追加
    if "BlankPlate" not in items:
        # 50音順で正しい位置に挿入するため、一旦全件処理後にソートされる
        items["BlankPlate"] = {
            "category": "item",
            "ja": "まっさらプレート",
            "en": "Blank Plate",
        }
        print("まっさらプレート を items.json に追加しました")

    entries = load_entries(REFERENCE_PATH)

    ja_to_key = {}
    for key, item in items.items():
        ja_to_key[item["ja"]] = key

    count = 0
    not_found = []
    for name, type_ja, is_plate in entries:
        type_en = TYPE_JA_TO_EN.get(type_ja)
        if not type_en:
            not_found.append(f"{name} (unknown type: {type_ja})")
            continue
        # 表記揺れを補正
        lookup_name = NAME_FIXES.get(name, name)
        if lookup_name not in ja_to_key:
            not_found.append(f"{name} (not in items.json)")
            continue
        key = ja_to_key[lookup_name]
        items[key]["typeBoostItem"] = {"plate": is_plate, "type": type_en}
        count += 1

    if not_found:
        print(f"スキップ: {not_found}")

    save_json(os.path.join(DATA_DIR, "items.json"), items)
    print(f"typeBoostItem を {count} 件追加しました")


if __name__ == "__main__":
    main()
