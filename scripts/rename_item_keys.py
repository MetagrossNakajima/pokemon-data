import sys
import os
from collections import OrderedDict

sys.path.append(os.path.dirname(__file__))
from json_utils import load_json, save_json

DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "data", "v1")

RENAMES = {
    "NeverMeltIce": "Never-MeltIce",
    "HeavyDutyBoots": "Heavy-DutyBoots",
    "FreshStartMochi": "Fresh-StartMochi",
}


def main():
    items = load_json(os.path.join(DATA_DIR, "items.json"))
    new_items = OrderedDict()
    for key, value in items.items():
        new_key = RENAMES.get(key, key)
        if new_key != key:
            print(f"{key} -> {new_key}")
        new_items[new_key] = value
    save_json(os.path.join(DATA_DIR, "items.json"), new_items)
    print("完了")


if __name__ == "__main__":
    main()
