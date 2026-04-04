"""
usage データから、ポケモンごとの技候補JSONを生成するスクリプト。

data/v1/usage/ 内の全ファイルをマージし、使用率順で最大10件の技を出力する。

使い方:
  python scripts/generate_suggested_moves.py
"""

import glob
import os
import sys

sys.path.append(os.path.dirname(__file__))
from json_utils import load_json, save_json

DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "data", "v1")
USAGE_DIR = os.path.join(DATA_DIR, "usage")
OUTPUT_PATH = os.path.join(DATA_DIR, "suggested_moves.json")
MAX_MOVES = 10


def main():
    usage_files = sorted(glob.glob(os.path.join(USAGE_DIR, "*.json")))
    if not usage_files:
        print("usage データが見つかりません")
        return

    print(f"読み込むファイル: {len(usage_files)}件")
    for f in usage_files:
        print(f"  {os.path.basename(f)}")

    # 全ファイルから技の使用率を集約（ポケモンごとに最大値を採用）
    pokemon_moves = {}  # {pokemon_key: {move_key: max_rate}}

    for path in usage_files:
        data = load_json(path)
        for pokemon_key, info in data.get("pokemon", {}).items():
            if pokemon_key not in pokemon_moves:
                pokemon_moves[pokemon_key] = {}
            for move_key, rate in info.get("moves", {}).items():
                current = pokemon_moves[pokemon_key].get(move_key, 0)
                pokemon_moves[pokemon_key][move_key] = max(current, rate)

    # 使用率順で上位N件の技名リストに変換
    result = {}
    for pokemon_key, moves in sorted(pokemon_moves.items()):
        sorted_moves = sorted(moves.items(), key=lambda x: x[1], reverse=True)
        result[pokemon_key] = [move for move, _ in sorted_moves[:MAX_MOVES]]

    save_json(OUTPUT_PATH, result)
    print(f"\n{len(result)}匹の技候補を {OUTPUT_PATH} に保存���ました")


if __name__ == "__main__":
    main()
