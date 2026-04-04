"""
sv.pokedb.tokyo からランクバトル使用率データをスクレイピングするスクリプト。

使い方:
  python scripts/scrape_usage.py --season 41 --rule 1
  python scripts/scrape_usage.py --season 41 --rule 1 --headed  # ブラウザ表示
  python scripts/scrape_usage.py --season 41 --rule 1 --top 10  # 上位10匹のみ
"""

import argparse
import asyncio
import json
import os
import re
import sys
from datetime import datetime, timezone

sys.path.append(os.path.dirname(__file__))
from json_utils import load_json, save_json

BASE_URL = "https://sv.pokedb.tokyo"
DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "data", "v1")
OUTPUT_DIR = os.path.join(DATA_DIR, "usage")
DELAY_BETWEEN_REQUESTS = 1.0


def build_ja_to_key_map(json_data):
    """日本語名 → 英語キーのマッピングを構築"""
    mapping = {}
    for key, value in json_data.items():
        ja = value.get("ja", "")
        if ja:
            mapping[ja] = key
    return mapping


def build_pokedb_id_to_key_map(pokemons):
    """pokedb ID（例: "0898-02"）→ ポケモンキーのマッピングを構築"""
    from collections import defaultdict
    pokedex_groups = defaultdict(list)
    for key, value in pokemons.items():
        pokedex_groups[value["pokedex"]].append(key)

    mapping = {}
    for pokedex, keys in pokedex_groups.items():
        for form_idx, key in enumerate(keys):
            pokedb_id = f"{pokedex:04d}-{form_idx:02d}"
            mapping[pokedb_id] = key
    return mapping


def normalize_name(name):
    """全角英数字を半角に変換"""
    result = []
    for c in name:
        cp = ord(c)
        if 0xFF10 <= cp <= 0xFF19:  # ０-９
            result.append(chr(cp - 0xFF10 + ord('0')))
        elif 0xFF21 <= cp <= 0xFF3A:  # Ａ-Ｚ
            result.append(chr(cp - 0xFF21 + ord('A')))
        elif 0xFF41 <= cp <= 0xFF5A:  # ａ-ｚ
            result.append(chr(cp - 0xFF41 + ord('a')))
        else:
            result.append(c)
    return ''.join(result)


def resolve_name(ja_name, ja_to_key, category=""):
    """日本語名を英語キーに変換。見つからない場合はNoneを返す"""
    key = ja_to_key.get(ja_name)
    if key:
        return key
    # 全角→半角変換して再試行
    normalized = normalize_name(ja_name)
    if normalized != ja_name:
        key = ja_to_key.get(normalized)
        if key:
            return key
    # 性格の括弧付き補正を除去して再試行（例: "ひかえめ (C↑A↓)" -> "ひかえめ"）
    cleaned = re.sub(r'\s*\(.*?\)', '', normalized).strip()
    if cleaned != normalized:
        key = ja_to_key.get(cleaned)
        if key:
            return key
    return None


async def scrape_ranking_list(page, season, rule, top_n):
    """一覧ページから上位N匹のポケモン情報を取得"""
    url = f"{BASE_URL}/pokemon/list?season={season}&rule={rule}"
    print(f"一覧ページを取得中: {url}")
    await page.goto(url, wait_until="networkidle")
    await asyncio.sleep(2)

    links = await page.query_selector_all("a[href*='/pokemon/show/']")
    ranking = []
    seen = set()

    for link in links:
        if len(ranking) >= top_n:
            break
        href = await link.get_attribute("href")
        text = await link.inner_text()
        lines = [l.strip() for l in text.strip().split("\n") if l.strip()]
        if len(lines) >= 2:
            rank = int(lines[0])
            ja_name = lines[1]
            # pokedb ID を URL から抽出
            match = re.search(r'/pokemon/show/(\d{4}-\d{2})', href)
            if match:
                pokedb_id = match.group(1)
                if pokedb_id not in seen:
                    seen.add(pokedb_id)
                    ranking.append((rank, pokedb_id, ja_name))

    print(f"  {len(ranking)}匹取得")
    return ranking


async def scrape_pokemon_detail(page, season, rule, pokedb_id):
    """詳細ページから使用率データを取得"""
    url = f"{BASE_URL}/pokemon/show/{pokedb_id}?season={season}&rule={rule}"
    await page.goto(url, wait_until="networkidle")
    await asyncio.sleep(1)

    data = await page.evaluate("""
        () => {
            const result = {};

            // わざ: #chart-trend-moves .pokemon-move-list-item
            const moves = [];
            for (const item of document.querySelectorAll('#chart-trend-moves .pokemon-move-list-item')) {
                const name = item.querySelector('.pokemon-move-name')?.textContent?.trim();
                const rateEl = item.querySelector('.pokemon-move-rate');
                const rate = rateEl ? parseFloat(rateEl.textContent) : null;
                if (name && rate !== null) moves.push({ name, rate });
            }
            result.moves = moves;

            // テーブル系データ（とくせい、せいかく、もちもの、テラスタイプ）
            // h3を探して、同じcolumn内のテーブルを取得する
            const allH3 = document.querySelectorAll('h3');
            const categoryMap = {
                'とくせい': 'abilities',
                'せいかく': 'natures',
                'もちもの': 'items',
                'テラスタイプ': 'teraTypes',
            };
            for (const h3 of allH3) {
                const title = h3.textContent.trim();
                const key = categoryMap[title];
                if (!key) continue;

                // h3の最も近い .column コンテナ内のテーブルを探す
                const column = h3.closest('.column, .card, .card-content');
                if (!column) continue;
                const table = column.querySelector('table');
                if (!table) continue;

                // このテーブルが別のh3カテゴリに属していないか確認
                const tableH3s = column.querySelectorAll('h3');
                let belongsToThis = false;
                for (const th of tableH3s) {
                    if (th.textContent.trim() === title) {
                        belongsToThis = true;
                        break;
                    }
                }
                if (!belongsToThis) continue;

                const items = [];
                for (const tr of table.querySelectorAll('tr')) {
                    const cells = Array.from(tr.querySelectorAll('td'));
                    if (cells.length >= 3) {
                        const name = cells[1]?.textContent?.trim();
                        const rateText = cells[2]?.textContent?.trim();
                        const rate = parseFloat(rateText);
                        if (name && !isNaN(rate)) items.push({ name, rate });
                    }
                }
                result[key] = items;
            }

            return result;
        }
    """)
    return data


async def main():
    parser = argparse.ArgumentParser(description="sv.pokedb.tokyo 使用率データスクレイピング")
    parser.add_argument("--season", type=int, required=True)
    parser.add_argument("--rule", type=int, default=1)
    parser.add_argument("--top", type=int, default=150)
    parser.add_argument("--headed", action="store_true", help="ブラウザを表示する")
    args = parser.parse_args()

    # 参照データを読み込み
    pokemons = load_json(os.path.join(DATA_DIR, "pokemons.json"))
    moves = load_json(os.path.join(DATA_DIR, "moves.json"))
    items = load_json(os.path.join(DATA_DIR, "items.json"))
    abilities = load_json(os.path.join(DATA_DIR, "abilities.json"))
    natures = load_json(os.path.join(DATA_DIR, "natures.json"))
    types = load_json(os.path.join(DATA_DIR, "types.json"))

    pokemon_ja_to_key = build_ja_to_key_map(pokemons)
    pokedb_id_to_key = build_pokedb_id_to_key_map(pokemons)
    move_ja_to_key = build_ja_to_key_map(moves)
    item_ja_to_key = build_ja_to_key_map(items)
    ability_ja_to_key = build_ja_to_key_map(abilities)
    nature_ja_to_key = build_ja_to_key_map(natures)
    type_ja_to_key = build_ja_to_key_map(types)
    type_ja_to_key["ステラ"] = "Stellar"  # テラスタイプ専用、types.jsonに未登録

    # 既存データがあれば読み込み（再開用）
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    output_path = os.path.join(OUTPUT_DIR, f"season{args.season}-rule{args.rule}.json")
    if os.path.exists(output_path):
        result = load_json(output_path)
        print(f"既存データを読み込みました: {len(result.get('pokemon', {}))}匹")
    else:
        result = {
            "meta": {
                "season": args.season,
                "rule": args.rule,
                "scrapedAt": datetime.now(timezone.utc).isoformat(),
                "source": BASE_URL,
            },
            "pokemon": {},
        }

    unresolved = []

    from playwright.async_api import async_playwright

    async with async_playwright() as pw:
        browser = await pw.chromium.launch(headless=not args.headed)
        page = await browser.new_page()

        # Phase 1: ランキング一覧を取得
        ranking = await scrape_ranking_list(page, args.season, args.rule, args.top)

        # Phase 2: 各ポケモンの詳細ページをスクレイピング
        for i, (rank, pokedb_id, ja_name) in enumerate(ranking):
            # ポケモン名解決: まずpokedb IDで試み、失敗したら日本語名で試みる
            pokemon_key = pokedb_id_to_key.get(pokedb_id) or resolve_name(ja_name, pokemon_ja_to_key, "pokemon")

            # 既にスクレイピング済みならスキップ
            if pokemon_key and pokemon_key in result["pokemon"]:
                print(f"  [{i+1}/{len(ranking)}] {ja_name} -> スキップ（取得済み）")
                continue

            print(f"  [{i+1}/{len(ranking)}] {ja_name} ({pokedb_id}) ...", end="", flush=True)
            raw = await scrape_pokemon_detail(page, args.season, args.rule, pokedb_id)

            # 名前解決
            entry = {"rank": rank, "pokedbId": pokedb_id}

            # わざ
            mapped_moves = {}
            for m in raw.get("moves", []):
                key = resolve_name(m["name"], move_ja_to_key, "move")
                if key:
                    mapped_moves[key] = m["rate"]
                else:
                    unresolved.append(("move", m["name"], ja_name))
                    mapped_moves[m["name"]] = m["rate"]
            entry["moves"] = mapped_moves

            # もちもの
            mapped_items = {}
            for m in raw.get("items", []):
                key = resolve_name(m["name"], item_ja_to_key, "item")
                if key:
                    mapped_items[key] = m["rate"]
                else:
                    unresolved.append(("item", m["name"], ja_name))
                    mapped_items[m["name"]] = m["rate"]
            entry["items"] = mapped_items

            # とくせい
            mapped_abilities = {}
            for m in raw.get("abilities", []):
                key = resolve_name(m["name"], ability_ja_to_key, "ability")
                if key:
                    mapped_abilities[key] = m["rate"]
                else:
                    unresolved.append(("ability", m["name"], ja_name))
                    mapped_abilities[m["name"]] = m["rate"]
            entry["abilities"] = mapped_abilities

            # せいかく
            mapped_natures = {}
            for m in raw.get("natures", []):
                key = resolve_name(m["name"], nature_ja_to_key, "nature")
                if key:
                    mapped_natures[key] = m["rate"]
                else:
                    unresolved.append(("nature", m["name"], ja_name))
                    mapped_natures[m["name"]] = m["rate"]
            entry["natures"] = mapped_natures

            # テラスタイプ
            mapped_tera = {}
            for m in raw.get("teraTypes", []):
                key = resolve_name(m["name"], type_ja_to_key, "type")
                if key:
                    mapped_tera[key] = m["rate"]
                else:
                    unresolved.append(("type", m["name"], ja_name))
                    mapped_tera[m["name"]] = m["rate"]
            entry["teraTypes"] = mapped_tera

            if pokemon_key:
                result["pokemon"][pokemon_key] = entry
            else:
                unresolved.append(("pokemon", ja_name, pokedb_id))
                result["pokemon"][ja_name] = entry

            print(f" わざ{len(mapped_moves)}件")

            # 中間保存（10匹ごと）
            if (i + 1) % 10 == 0:
                save_json(output_path, result)
                print(f"  --- 中間保存 ({i+1}/{len(ranking)}) ---")

            await asyncio.sleep(DELAY_BETWEEN_REQUESTS)

        await browser.close()

    # 最終保存
    result["meta"]["scrapedAt"] = datetime.now(timezone.utc).isoformat()
    save_json(output_path, result)
    print(f"\n完了！ {output_path} に保存しました ({len(result['pokemon'])}匹)")

    if unresolved:
        print(f"\n未解決の名前 ({len(unresolved)}件):")
        for category, name, context in unresolved:
            print(f"  [{category}] {name} (in {context})")


if __name__ == "__main__":
    asyncio.run(main())
