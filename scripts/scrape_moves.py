import re
import sys
import os

sys.path.append(os.path.dirname(__file__))
from json_utils import load_json, save_json

DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "data", "v1")
HTML_PATH = os.path.join(os.path.dirname(__file__), "..", "moves.html")

# タイプクラス(t0-t17) → 日本語名
TYPE_CLASS_TO_JA = {
    "t0": "ノーマル", "t1": "かくとう", "t2": "ひこう", "t3": "どく",
    "t4": "じめん", "t5": "いわ", "t6": "むし", "t7": "ゴースト",
    "t8": "はがね", "t9": "ほのお", "t10": "みず", "t11": "くさ",
    "t12": "でんき", "t13": "エスパー", "t14": "こおり", "t15": "ドラゴン",
    "t16": "あく", "t17": "フェアリー",
}

# 分類マッピング
CATEGORY_MAP = {
    "physics": "physical",
    "special": "special",
    "change": "status",
}

# 対象マッピング
TARGET_MAP = {
    "1体選択": "single",
    "自分": "self",
    "味方1体": "oneAlly",
    "自分か味方": "userOrAlly",
    "相手全体": "allOpponents",
    "味方全体": "allAllies",
    "全体": "all",
    "ランダム1体": "randomOpponent",
    "自分の場": "userField",
    "味方の場": "userField",
    "相手の場": "opponentField",
    "全体の場": "entireField",
    "自分以外全体": "allOther",
    "不定": "varies",
}

# 直接/守るマッピング
CONTACT_MAP = {"直○": True, "直×": False}
PROTECT_MAP = {"守○": True, "守×": False}


def parse_html(html_path):
    with open(html_path, "rb") as f:
        raw = f.read()
    text = raw.decode("euc-jp", errors="replace")

    rows = re.findall(r'<tr class="sort_tr">(.*?)</tr>', text, re.DOTALL)
    nexts = re.findall(r'<tr class="sort_tr_next">(.*?)</tr>', text, re.DOTALL)

    assert len(rows) == len(nexts), f"Row count mismatch: {len(rows)} vs {len(nexts)}"

    moves = []
    for row, nxt in zip(rows, nexts):
        # 技名(日本語) - <a>タグ内の表示名を使用
        name_match = re.search(r'<a href="[^"]*">([^<]+)</a>', row)
        ja_name = name_match.group(1) if name_match else None

        # タイプ(クラスから)
        type_match = re.search(r'class="type (t\d+)"', row)
        type_class = type_match.group(1) if type_match else None

        # 分類
        cat_match = re.search(r'class="(physics|special|change)"', row)
        category = cat_match.group(1) if cat_match else None

        # 威力・命中(data-sort-value)
        sort_values = re.findall(r'<td data-sort-value="(\d+)">', row)
        power_raw = int(sort_values[0]) if len(sort_values) > 0 else None
        accuracy_raw = int(sort_values[1]) if len(sort_values) > 1 else None

        # PP
        tds = re.findall(r"<td>(.*?)</td>", row)
        # tds should contain: PP, 直接, 守る (after the data-sort-value tds)
        pp = None
        contact = None
        protect = None
        if len(tds) >= 3:
            pp = int(tds[-3]) if tds[-3].isdigit() else None
            contact = CONTACT_MAP.get(tds[-2])
            protect = PROTECT_MAP.get(tds[-1])

        # 対象(sort_tr_nextの最初のtd)
        target_match = re.search(r"<td>(.*?)</td>", nxt)
        target_ja = target_match.group(1) if target_match else None

        moves.append({
            "ja_name": ja_name,
            "type_class": type_class,
            "category": category,
            "power": power_raw,
            "accuracy": accuracy_raw,
            "pp": pp,
            "contact": contact,
            "protect": protect,
            "target_ja": target_ja,
        })

    return moves


def main():
    types_json = load_json(os.path.join(DATA_DIR, "types.json"))
    moves_json = load_json(os.path.join(DATA_DIR, "moves.json"))

    # 日本語タイプ名 → 英語タイプ名
    ja_to_en_type = {v["ja"]: k for k, v in types_json.items()}

    # 日本語技名 → 英語キー(moves.json)
    ja_to_key = {}
    for key, val in moves_json.items():
        ja = val.get("ja")
        if ja:
            ja_to_key[ja] = key

    scraped = parse_html(HTML_PATH)
    print(f"Scraped {len(scraped)} moves from HTML")

    matched = 0
    unmatched_moves = []

    for move in scraped:
        ja_name = move["ja_name"]
        if not ja_name:
            continue

        key = ja_to_key.get(ja_name)
        if not key:
            unmatched_moves.append(ja_name)
            continue

        matched += 1

        # タイプ
        type_ja = TYPE_CLASS_TO_JA.get(move["type_class"], "")
        type_en = ja_to_en_type.get(type_ja)

        # 分類
        category = CATEGORY_MAP.get(move["category"])

        # 威力 (0 → null)
        power = move["power"] if move["power"] and move["power"] > 0 else None

        # 命中 (101以上 → null = 必中/-)
        accuracy = move["accuracy"] if move["accuracy"] and move["accuracy"] <= 100 else None

        # 対象
        target = TARGET_MAP.get(move["target_ja"])

        entry = moves_json[key]
        entry["type"] = type_en
        entry["category"] = category
        entry["power"] = power
        entry["accuracy"] = accuracy
        entry["pp"] = move["pp"]
        entry["contact"] = move["contact"]
        entry["protect"] = move["protect"]
        entry["target"] = target

    save_json(os.path.join(DATA_DIR, "moves.json"), moves_json)

    print(f"Matched: {matched}")
    print(f"Unmatched: {len(unmatched_moves)}")
    if unmatched_moves[:20]:
        print(f"Unmatched examples: {unmatched_moves[:20]}")


if __name__ == "__main__":
    main()
