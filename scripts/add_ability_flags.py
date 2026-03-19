import sys
import os

sys.path.append(os.path.dirname(__file__))
from json_utils import load_json, save_json

DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "data", "v1")
REFERENCE_DIR = os.path.join(os.path.dirname(__file__), "..", "reference")


def load_names(path):
    with open(path, "r", encoding="utf-8") as f:
        return [line.strip() for line in f if line.strip()]


def add_flag(moves, ja_to_key, names, flag):
    count = 0
    not_found = []
    for ja_name in names:
        if ja_name in ja_to_key:
            moves[ja_to_key[ja_name]][flag] = True
            count += 1
        else:
            not_found.append(ja_name)
    if not_found:
        print(f"  見つからなかった技: {not_found}")
    print(f"  {flag} を {count} 件追加しました")


def main():
    moves = load_json(os.path.join(DATA_DIR, "moves.json"))

    ja_to_key = {}
    for key, move in moves.items():
        ja_to_key[move["ja"]] = key

    flags = {
        "bite": os.path.join(REFERENCE_DIR, "bite.txt"),
        "pulse": os.path.join(REFERENCE_DIR, "pulse.txt"),
    }

    for flag, path in flags.items():
        print(f"[{flag}]")
        names = load_names(path)
        add_flag(moves, ja_to_key, names, flag)

    save_json(os.path.join(DATA_DIR, "moves.json"), moves)


if __name__ == "__main__":
    main()
