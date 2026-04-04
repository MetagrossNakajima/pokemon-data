"""
ポケモンの高さ・重さデータを pokemons.json に追加するスクリプト。

データソース:
  1. /tmp/claude/wiki_full.html (wiki.pokemonwiki.com) - 全ポケモンの高さ・重さ
  2. pokemon_weight.txt (yakkun.com) - SVポケモンの重さ（フォーム違い補完）

使い方:
  python scripts/scrape_weight_height.py
"""

import os
import re
import sys

sys.path.append(os.path.dirname(__file__))
from json_utils import load_json, save_json

DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "data", "v1")
WIKI_HTML_PATH = "/tmp/claude/wiki_full.html"
YAKKUN_TXT_PATH = os.path.join(os.path.dirname(__file__), "..", "pokemon_weight.txt")

# Wikiのフォーム名が括弧なしの場合のデフォルトフォーム
# (ベース名がそのまま ja に存在しない場合の割り当て)
BASE_TO_DEFAULT_FORM = {
    "デオキシス": "デオキシス(ノーマル)",
    "ミノマダム": "ミノマダム(くさき)",
    "バスラオ": "バスラオ(赤)",
    "メロエッタ": "メロエッタ(ボイス)",
    "ニャオニクス": "ニャオニクス♂",
    "バケッチャ": "バケッチャ(普通)",
    "パンプジン": "パンプジン(普通)",
    "オドリドリ": "オドリドリ(めらめら)",
    "ルガルガン": "ルガルガン(昼)",
    "ヨワシ": "ヨワシ(群れ)",
    "コレクレー": "コレクレー",
    "ストリンダー": "ストリンダー(ハイ)",
    "イエッサン": "イエッサン♂",
    "イダイトウ": "イダイトウ♂",
    "ラブトロス": "ラブトロス(化身)",
    "パフュートン": "パフュートン♂",
    "オーガポン": "オーガポン(草)",
}

# 特殊文字の正規化
CHAR_NORMALIZE = {
    ":": "\uff1a",  # 半角コロン → 全角コロン (タイプ:ヌル → タイプ：ヌル)
}

# テキストの括弧内フォーム表記 → pokemons.json の括弧内テキストへのマッピング
FORM_NAME_MAP = {
    # 地方フォーム
    "アローラのすがた": "アローラ",
    "ガラルのすがた": "ガラル",
    "ヒスイのすがた": "ヒスイ",
    "パルデアのすがた": "パルデア",
    # ケンタロス
    "パルデアのすがた炎": "パルデア炎",
    "パルデアのすがた水": "パルデア水",
    "パルデアのすがた単": "パルデア単",
    # ロトム
    "ヒートロトム": "ヒート",
    "ウォッシュロトム": "ウォッシュ",
    "フロストロトム": "フロスト",
    "スピンロトム": "スピン",
    "カットロトム": "カット",
    # デオキシス
    "ノーマルフォルム": "ノーマル",
    "アタックフォルム": "アタック",
    "ディフェンスフォルム": "ディフェンス",
    "スピードフォルム": "スピード",
    # カラナクシ/トリトドン
    "にしのうみ": None,
    "ひがしのうみ": "東",
    # ディアルガ/パルキア
    "オリジンフォルム": "オリジン",
    # ギラティナ
    "アナザーフォルム": "アナザー",
    # シェイミ
    "ランドフォルム": "ランド",
    "スカイフォルム": "スカイ",
    # バスラオ
    "あかすじ": "赤",
    "あおすじ": "青",
    "しろすじ": "白",
    # トルネロス/ボルトロス/ランドロス/ラブトロス
    "けしんフォルム": "化身",
    "れいじゅうフォルム": "霊獣",
    # ケルディオ
    "いつものすがた": None,
    "かくごのすがた": "かくごのすがた",
    # メロエッタ
    "ボイスフォルム": "ボイス",
    "ステップフォルム": "ステップ",
    # フーパ
    "いましめられしフーパ": "解放",
    "ときはなたれしフーパ": "ときはなたれし",
    # オドリドリ
    "めらめらスタイル": "めらめら",
    "ぱちぱちスタイル": "ぱちぱち",
    "ふらふらスタイル": "ふらふら",
    "まいまいスタイル": "まいまい",
    # ルガルガン
    "まひるのすがた": "昼",
    "まよなかのすがた": "夜",
    "たそがれのすがた": "黄昏",
    # メテノ
    "コア": None,
    "りゅうせいのすがた": None,
    # ストリンダー
    "ハイなすがた": "ハイ",
    "ローなすがた": "ロー",
    # コオリッポ
    "アイスフェイス": None,
    "ナイスフェイス": "ナイス",
    # ザシアン/ザマゼンタ
    "れきせんのゆうしゃ": None,
    # ウーラオス
    "いちげきのかた": "一撃",
    "れんげきのかた": "連撃",
    # イルカマン
    "ナイーブフォルム": None,
    "マイティフォルム": "マイティ",
    # ノココッチ
    "ふたふしフォルム": None,
    "みつふしフォルム": None,
    # コレクレー
    "はこフォルム": None,
    "とほフォルム": "とほフォルム",
    # キュレム
    "ブラックキュレム": "__SPECIAL__ブラックキュレム",
    "ホワイトキュレム": "__SPECIAL__ホワイトキュレム",
    "キュレムのすがた": "通常",
    # ネクロズマ
    "たそがれのたてがみ": "日食",
    "あかつきのつばさ": "月食",
    # バドレックス
    "はくばじょうのすがた": "白",
    "こくばじょうのすがた": "黒",
    # ガチグマ
    "アカツキ": "アカツキ",
    # オーガポン
    "みどりのめん": "草",
    "いしずえのめん": "岩",
    "かまどのめん": "炎",
    "いどのめん": "水",
    # テラパゴス
    "ノーマルフォルム": "ノーマル",
    "テラスタルフォルム": "ノーマル",
    "ステラフォルム": "ステラ",
    # 性別フォーム
    "オスの姿": "__SUFFIX__\u2642",
    "メスの姿": "__SUFFIX__\u2640",
    "オスのすがた": "__SUFFIX__\u2642",
    "メスのすがた": "__SUFFIX__\u2640",
    # イッカネズミ
    "4ひきかぞく": None,
    "3びきかぞく": None,
    # イキリンコ
    "グリーンフェザー": None,
    "ブルーフェザー": None,
    "イエローフェザー": None,
    "ホワイトフェザー": None,
    # ヨワシ
    "たんどくのすがた": "群れ",
    "むれたすがた": "群れ",
    # バケッチャ/パンプジン
    "ちいさいサイズ": "小",
    "ふつうのサイズ": "普通",
    "おおきいサイズ": "大",
    "とくだいサイズ": "特大",
    # ジガルデ
    "50%フォルム": None,
    "10%フォルム": None,
    "パーフェクトフォルム": "パーフェクト",
    # カイオーガ/グラードン
    "カイオーガのすがた": None,
    "グラードンのすがた": None,
    # ゲンシカイキ
    "ゲンシカイキのすがた": "__PRIMAL__",
    # ザシアン/ザマゼンタ (おうの装備)
    "けんのおう": "けんのおう",
    "たてのおう": "たてのおう",
    # ケンタロス パルデア (Wiki形式)
    "パルデアのすがた・コンバット種": "パルデア単",
    "パルデアのすがた・ブレイズ種": "パルデア炎",
    "パルデアのすがた・ウォーター種": "パルデア水",
    # ネクロズマ (Wiki形式)
    "ウルトラネクロズマ": "__SPECIAL__ウルトラネクロズマ",
    # メテ���
    "コアのすがた": None,
    # ムゲンダイナ
    "ムゲンダイマックス": "__SPECIAL__ムゲンダイマックス",
    # ゲッコウガ
    "サトシゲッコウガ": None,  # skip, not in json
    # みつふし
    "みつふしフォルム": None,
    # 4ひきかぞく
    "4ひきかぞく": None,
}


def build_ja_to_keys_map(pokemons):
    """日本語名 -> 英語キーのマッピングを構築"""
    mapping = {}
    for key, value in pokemons.items():
        ja = value.get("ja", "")
        if ja:
            mapping[ja] = key
    return mapping


def normalize_name(name):
    """特殊文字を正規化"""
    for old, new in CHAR_NORMALIZE.items():
        name = name.replace(old, new)
    return name


def resolve_ja_name(base_name, form_text, ja_to_key):
    """ベース名とフォームテキストから pokemons.json の ja 名を解決"""
    base_name = normalize_name(base_name)

    if form_text:
        mapped = FORM_NAME_MAP.get(form_text, form_text)

        if isinstance(mapped, str) and mapped.startswith("__SPECIAL__"):
            return mapped.replace("__SPECIAL__", "")

        if isinstance(mapped, str) and mapped.startswith("__SUFFIX__"):
            suffix = mapped.replace("__SUFFIX__", "")
            return f"{base_name}{suffix}"

        # ゲンシカイキ: カイオーガ → ゲンシカイオーガ
        if mapped == "__PRIMAL__":
            primal_name = f"ゲンシ{base_name}"
            if primal_name in ja_to_key:
                return primal_name
            return base_name

        # メガ進化: form_textがそのままja名の場�� (メガフシギバナ等)
        if form_text.startswith("メガ") and form_text in ja_to_key:
            return form_text

        if mapped is None:
            ja_name = base_name
        else:
            ja_name = f"{base_name}({mapped})"

        if ja_name in ja_to_key:
            return ja_name

        ja_name_raw = f"{base_name}({form_text})"
        if ja_name_raw in ja_to_key:
            return ja_name_raw

        return ja_name
    else:
        if base_name in ja_to_key:
            return base_name

        # デフォルトフォームマッピング
        if base_name in BASE_TO_DEFAULT_FORM:
            return BASE_TO_DEFAULT_FORM[base_name]

        for suffix in ["(通常)", "(単体)", "(オレンジ)"]:
            candidate = base_name + suffix
            if candidate in ja_to_key:
                return candidate

        return base_name


def parse_wiki_html(html_path, ja_to_key):
    """wiki HTMLからポケモンの高さ・重さを抽出"""
    with open(html_path, "r", encoding="utf-8") as f:
        html = f.read()

    table_match = re.search(
        r'<table class="graytable r sortable">(.*?)</table>', html, re.DOTALL
    )
    if not table_match:
        print("ERROR: テーブルが見つかりません")
        return []

    table_html = table_match.group(1)
    rows = re.findall(r"<tr[^>]*>(.*?)</tr>", table_html, re.DOTALL)

    entries = []
    for row in rows:
        cells = re.findall(r"<td[^>]*>(.*?)</td>", row, re.DOTALL)

        # 11セル: [dex, name, height, ..., weight, ...]
        # 10セル: [name, height, ..., weight, ...] (rowspanで図鑑番号省略)
        if len(cells) == 11:
            name_idx, height_idx, weight_idx = 1, 2, 6
        elif len(cells) == 10:
            name_idx, height_idx, weight_idx = 0, 1, 5
        else:
            continue

        name_raw = re.sub(r"<[^>]+>", "", cells[name_idx]).strip()
        height_str = re.sub(r"<[^>]+>", "", cells[height_idx]).strip()
        weight_str = re.sub(r"<[^>]+>", "", cells[weight_idx]).strip()

        # HTML entities
        for s in [height_str, weight_str]:
            s = s.replace("\u2212", "").replace("\u2014", "").strip()
        height_str = height_str.replace("\u2212", "").replace("\u2014", "").strip()
        weight_str = weight_str.replace("\u2212", "").replace("\u2014", "").strip()
        # &#8211; &#8212; &#91; etc
        height_str = re.sub(r"&#\d+;", "", height_str).strip()
        weight_str = re.sub(r"&#\d+;", "", weight_str).strip()

        if not name_raw:
            continue

        try:
            height = float(height_str)
            weight = float(weight_str)
        except ValueError:
            continue

        form_match = re.match(r"^(.+?)[\(\uff08](.+?)[\)\uff09]$", name_raw)
        if form_match:
            base_name = form_match.group(1).strip()
            form_text = form_match.group(2).strip()
            ja_name = resolve_ja_name(base_name, form_text, ja_to_key)
        else:
            ja_name = resolve_ja_name(name_raw, None, ja_to_key)

        entries.append((ja_name, height, weight))

    return entries


def parse_yakkun_txt(txt_path, ja_to_key):
    """yakkun の pokemon_weight.txt から重さデータを抽出"""
    with open(txt_path, "r", encoding="utf-8") as f:
        content = f.read()

    content = re.sub(r"\n(\([^)]+\))\t", r"\1\t", content)

    entries = []
    for line in content.split("\n"):
        if not line.strip() or ("ポケモン" in line and "重さ" in line):
            continue

        parts = line.split("\t")
        if len(parts) < 5:
            continue

        name_raw = parts[2].strip()
        weight_str = parts[4].strip()

        try:
            weight = float(weight_str)
        except ValueError:
            continue

        form_match = re.match(r"^(.+?)\((.+)\)$", name_raw)
        if form_match:
            base_name = form_match.group(1).strip()
            form_text = form_match.group(2).strip()
            ja_name = resolve_ja_name(base_name, form_text, ja_to_key)
        else:
            ja_name = resolve_ja_name(name_raw, None, ja_to_key)

        entries.append((ja_name, weight))

    return entries


def main():
    pokemons_path = os.path.join(DATA_DIR, "pokemons.json")
    pokemons = load_json(pokemons_path)
    ja_to_key = build_ja_to_keys_map(pokemons)

    # 全エントリから weight/height を削除してやり直す
    for v in pokemons.values():
        v.pop("weight", None)
        v.pop("height", None)

    # 1. Wiki データ（高さ・重さ）
    wiki_entries = parse_wiki_html(WIKI_HTML_PATH, ja_to_key)
    print(f"[Wiki] 抽出エントリ数: {len(wiki_entries)}")

    wiki_matched = 0
    wiki_unmatched = []
    for ja_name, height, weight in wiki_entries:
        key = ja_to_key.get(ja_name)
        if key:
            pokemons[key]["height"] = height
            pokemons[key]["weight"] = weight
            wiki_matched += 1
        else:
            wiki_unmatched.append((ja_name, height, weight))

    print(f"[Wiki] マッチ成功: {wiki_matched}")
    print(f"[Wiki] マッチ失敗: {len(wiki_unmatched)}")
    if wiki_unmatched:
        for name, h, w in wiki_unmatched:
            print(f"  {name} (h={h}, w={w})")

    # 2. Yakkun データ（重さのみ、フォーム違い補完）
    if os.path.exists(YAKKUN_TXT_PATH):
        yakkun_entries = parse_yakkun_txt(YAKKUN_TXT_PATH, ja_to_key)
        print(f"\n[Yakkun] 抽出エントリ数: {len(yakkun_entries)}")

        yakkun_new = 0
        for ja_name, weight in yakkun_entries:
            key = ja_to_key.get(ja_name)
            if key and "weight" not in pokemons[key]:
                pokemons[key]["weight"] = weight
                yakkun_new += 1

        print(f"[Yakkun] 新規追加: {yakkun_new}")

    # 3. 同じ図鑑番号のベースフォームから高さ・重さを補完
    # pokedex → ベースフォームのキーを構築
    from collections import defaultdict

    pokedex_to_base = {}
    for key, v in pokemons.items():
        dex = v["pokedex"]
        # 最初に見つかった height/weight 持ちをベースとする
        if dex not in pokedex_to_base and "height" in v and "weight" in v:
            pokedex_to_base[dex] = key

    copied = 0
    for key, v in pokemons.items():
        if "height" in v and "weight" in v:
            continue
        base_key = pokedex_to_base.get(v["pokedex"])
        if not base_key:
            continue
        base = pokemons[base_key]
        if "height" not in v and "height" in base:
            v["height"] = base["height"]
        if "weight" not in v and "weight" in base:
            v["weight"] = base["weight"]
        copied += 1

    print(f"\n[補完] ベースフォームからコピー: {copied}")

    # 未設定の確認
    from collections import Counter

    missing_both = [
        (k, v["ja"], v["formType"])
        for k, v in pokemons.items()
        if "weight" not in v and "height" not in v
    ]
    missing_height = [
        (k, v["ja"], v["formType"])
        for k, v in pokemons.items()
        if "height" not in v and "weight" in v
    ]
    missing_weight = [
        (k, v["ja"], v["formType"])
        for k, v in pokemons.items()
        if "weight" not in v and "height" in v
    ]

    print(f"\n高さ・重さ両方未設定: {len(missing_both)}")
    if missing_both:
        both_types = Counter(ft for _, _, ft in missing_both)
        print(f"  formType別: {dict(both_types)}")
        for k, ja, ft in missing_both:
            print(f"  {k}: {ja} ({ft})")

    print(f"高さのみ未設定: {len(missing_height)}")
    if missing_height:
        for k, ja, ft in missing_height:
            print(f"  {k}: {ja} ({ft})")

    print(f"重さのみ未設定: {len(missing_weight)}")
    if missing_weight:
        for k, ja, ft in missing_weight:
            print(f"  {k}: {ja} ({ft})")

    save_json(pokemons_path, pokemons)
    print(f"\n保存完了: {pokemons_path}")


if __name__ == "__main__":
    main()
