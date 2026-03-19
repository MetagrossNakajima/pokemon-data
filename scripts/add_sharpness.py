import sys
import os

sys.path.append(os.path.dirname(__file__))
from json_utils import load_json, save_json

DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "data", "v1")
REFERENCE_PATH = os.path.join(os.path.dirname(__file__), "..", "reference", "sharpness.txt")


def load_sharpness_names(path):
    with open(path, "r", encoding="utf-8") as f:
        return [line.strip() for line in f if line.strip()]


def main():
    moves = load_json(os.path.join(DATA_DIR, "moves.json"))
    sharpness_names = load_sharpness_names(REFERENCE_PATH)

    # ja名 → キー の逆引きマップ
    ja_to_key = {}
    for key, move in moves.items():
        ja_to_key[move["ja"]] = key

    count = 0
    not_found = []
    for ja_name in sharpness_names:
        if ja_name in ja_to_key:
            key = ja_to_key[ja_name]
            moves[key]["sharpness"] = True
            count += 1
        else:
            not_found.append(ja_name)

    if not_found:
        print(f"見つからなかった技: {not_found}")

    save_json(os.path.join(DATA_DIR, "moves.json"), moves)
    print(f"sharpness を {count} 件追加しました")


if __name__ == "__main__":
    main()
