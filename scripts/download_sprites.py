"""projectpokemon.org から SV HOME スプライト画像をダウンロードするスクリプト"""

import os
import sys
import time
import urllib.request
import urllib.error

sys.path.append(os.path.dirname(__file__))
from json_utils import load_json

BASE_URL = "https://projectpokemon.org/images/sprites-models/sv-sprites-home"
SAVE_DIR = os.path.join(os.path.dirname(__file__), "..", "icons", "v2")
POKEMONS_JSON = os.path.join(os.path.dirname(__file__), "..", "data", "v1", "pokemons.json")
DELAY = 0.3
USER_AGENT = "Mozilla/5.0 (compatible; PokemonDataBot/1.0)"


def build_pokedex_map(data):
    """pokedex番号 → ベースポケモン名のマッピングを構築する。
    各pokedex番号について、JSONで最初に登場するエントリの名前をベース名とする。
    """
    pokedex_map = {}
    for name, info in data.items():
        pdex = info["pokedex"]
        if pdex not in pokedex_map:
            pokedex_map[pdex] = name
    return pokedex_map


def download_file(url, save_path):
    """URLからファイルをダウンロードする。成功時True、404時False、その他エラー時は例外。"""
    req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    try:
        with urllib.request.urlopen(req) as resp:
            with open(save_path, "wb") as f:
                f.write(resp.read())
        return True
    except urllib.error.HTTPError as e:
        if e.code == 404:
            return False
        raise


def download_sprites(gen_start=1, gen_end=151, skip_existing=True):
    data = load_json(POKEMONS_JSON)
    pokedex_map = build_pokedex_map(data)
    os.makedirs(SAVE_DIR, exist_ok=True)

    targets = sorted(pdex for pdex in pokedex_map if gen_start <= pdex <= gen_end)
    total = len(targets)
    downloaded = 0
    skipped = 0

    for i, pdex in enumerate(targets, 1):
        base_name = pokedex_map[pdex]
        num_str = f"{pdex:04d}"

        # ベース画像のダウンロード
        url = f"{BASE_URL}/{num_str}.png"
        save_path = os.path.join(SAVE_DIR, f"{base_name}.png")

        if skip_existing and os.path.exists(save_path):
            print(f"[{i}/{total}] {base_name}.png skipped (exists)")
            skipped += 1
        else:
            if download_file(url, save_path):
                print(f"[{i}/{total}] {base_name}.png downloaded")
                downloaded += 1
            else:
                print(f"[{i}/{total}] {base_name}.png not found (404)")
            time.sleep(DELAY)

        # バリアント画像のダウンロード (_01, _02, ...)
        variant = 1
        while True:
            variant_str = f"{variant:02d}"
            url = f"{BASE_URL}/{num_str}_{variant_str}.png"
            save_path = os.path.join(SAVE_DIR, f"{base_name}_{variant_str}.png")

            if skip_existing and os.path.exists(save_path):
                print(f"[{i}/{total}] {base_name}_{variant_str}.png skipped (exists)")
                skipped += 1
                variant += 1
                continue

            time.sleep(DELAY)
            if download_file(url, save_path):
                print(f"[{i}/{total}] {base_name}_{variant_str}.png downloaded")
                downloaded += 1
                variant += 1
            else:
                break

    print(f"\nDone! Downloaded: {downloaded}, Skipped: {skipped}")


if __name__ == "__main__":
    download_sprites()
