"""複数フォルム・メガ進化レポート生成スクリプト"""

import json
from collections import defaultdict
from pathlib import Path

DATA_PATH = Path(__file__).parent.parent / "data" / "v1" / "pokemons.json"
OUTPUT_PATH = Path(__file__).parent.parent / "docs" / "report_multi_forms.md"

with open(DATA_PATH, encoding="utf-8") as f:
    pokemons = json.load(f)

# formType別カウント
form_type_counts = defaultdict(int)
# pokedex番号でグルーピング
by_pokedex = defaultdict(list)

for key, poke in pokemons.items():
    ft = poke["formType"]
    form_type_counts[ft] += 1
    by_pokedex[poke["pokedex"]].append({"key": key, **poke})

# 複数エントリを持つポケモン
multi = {dex: entries for dex, entries in by_pokedex.items() if len(entries) > 1}

# formType別にエントリを分類（baseを除く）
FORM_TYPE_SECTIONS = {
    "mega": ("メガ進化", "Mega Evolution"),
    "alola": ("アローラのすがた", "Alolan Form"),
    "galar": ("ガラルのすがた", "Galarian Form"),
    "hisui": ("ヒスイのすがた", "Hisuian Form"),
    "paldea": ("パルデアのすがた", "Paldean Form"),
    "form": ("その他フォルム", "Other Forms"),
    "fusion": ("フュージョン", "Fusion"),
    "primal": ("ゲンシカイキ", "Primal Reversion"),
    "crowned": ("けんのおう/たてのおう", "Crowned Form"),
}

# formType別のエントリ収集
entries_by_ft = defaultdict(list)
for dex, entries in sorted(multi.items()):
    for e in entries:
        if e["formType"] != "base":
            entries_by_ft[e["formType"]].append(e)


def type_str(types):
    return " / ".join(types)


lines = []
lines.append("# 複数フォルム・メガ進化 レポート\n")
lines.append("## 概要\n")
lines.append(f"`data/v1/pokemons.json` の全 {len(pokemons)} エントリから、")
lines.append(f"複数フォルムやメガ進化を持つポケモンを集計した。\n")
lines.append(f"- **複数エントリを持つポケモン**: {len(multi)} 種")
lines.append(f"- **base以外のエントリ数**: {len(pokemons) - form_type_counts['base']}\n")

# サマリーテーブル
lines.append("## formType サマリー\n")
lines.append("| formType | 件数 |")
lines.append("|----------|------|")
for ft in ["base"] + list(FORM_TYPE_SECTIONS.keys()):
    lines.append(f"| {ft} | {form_type_counts.get(ft, 0)} |")
lines.append(f"| **合計** | **{len(pokemons)}** |\n")

# 各セクション
for ft, (ja_name, en_name) in FORM_TYPE_SECTIONS.items():
    entries = entries_by_ft.get(ft, [])
    if not entries:
        continue
    lines.append(f"## {ja_name}（{en_name}）— {len(entries)}件\n")
    lines.append("| 図鑑No | キー | 日本語名 | 英語名 | タイプ |")
    lines.append("|--------|------|---------|--------|--------|")
    for e in sorted(entries, key=lambda x: x["pokedex"]):
        lines.append(
            f"| {e['pokedex']:04d} | {e['key']} | {e['ja']} | {e['en']} | {type_str(e['types'])} |"
        )
    lines.append("")

# 複数エントリ持ちの全一覧
lines.append("## 複数エントリを持つポケモン一覧\n")
lines.append(
    f"以下の {len(multi)} 種が複数エントリを持つ。\n"
)
for dex, entries in sorted(multi.items()):
    base = next((e for e in entries if e["formType"] == "base"), entries[0])
    lines.append(f"### No.{dex:04d} {base['ja']}（{base['en']}）\n")
    lines.append("| キー | formType | タイプ |")
    lines.append("|------|----------|--------|")
    for e in entries:
        lines.append(f"| {e['key']} | {e['formType']} | {type_str(e['types'])} |")
    lines.append("")

lines.append("---\n")
lines.append("生成スクリプト: `scripts/report_multi_forms.py`\n")

OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
OUTPUT_PATH.write_text("\n".join(lines), encoding="utf-8")
print(f"レポートを生成しました: {OUTPUT_PATH}")
print(f"  総エントリ数: {len(pokemons)}")
print(f"  複数エントリ持ち: {len(multi)} 種")
print(f"  formType種別数: {len(form_type_counts)}")
