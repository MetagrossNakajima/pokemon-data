import json
import sys
import os

sys.path.append(os.path.dirname(__file__))
from json_utils import load_json, save_json

DATA_PATH = os.path.join(os.path.dirname(__file__), '..', 'data', 'v1', 'pokemons.json')

# Japanese type -> English type mapping
TYPE_MAP = {
    '草': 'Grass', '毒': 'Poison', '炎': 'Fire', 'ドラゴン': 'Dragon',
    '飛行': 'Flying', '水': 'Water', '虫': 'Bug', 'ノーマル': 'Normal',
    'エスパー': 'Psychic', 'ゴースト': 'Ghost', '岩': 'Rock', '格闘': 'Fighting',
    '電気': 'Electric', '鋼': 'Steel', '悪': 'Dark', '地面': 'Ground',
    'フェアリー': 'Fairy', '氷': 'Ice',
    # Hiragana variants (used in M次元ラッシュ section)
    'でんき': 'Electric', 'かくとう': 'Fighting', 'はがね': 'Steel',
    'あく': 'Dark', 'みず': 'Water',
}


def parse_types(type_str):
    """Parse Japanese type string like '草・毒' into English type list."""
    if not type_str or type_str == '-':
        return None
    parts = type_str.replace('・', '／').replace('/', '／').split('／')
    return [TYPE_MAP[t.strip()] for t in parts if t.strip() in TYPE_MAP]


# All mega evolution data: (base_ja, mega_ja, suffix, type_str, HP, Atk, Def, Spa, Spd, Spe)
# suffix: '-Mega', '-Mega-X', '-Mega-Y', '-Mega-Z'
MEGA_DATA = [
    # === Gen 1 (15) ===
    ('フシギバナ', 'メガフシギバナ', '-Mega', '草・毒', 80, 100, 123, 122, 120, 80),
    ('リザードン', 'メガリザードンX', '-Mega-X', '炎・ドラゴン', 78, 130, 111, 130, 85, 100),
    ('リザードン', 'メガリザードンY', '-Mega-Y', '炎・飛行', 78, 104, 78, 159, 115, 100),
    ('カメックス', 'メガカメックス', '-Mega', '水', 79, 103, 120, 135, 115, 78),
    ('スピアー', 'メガスピアー', '-Mega', '虫・毒', 65, 150, 40, 15, 80, 145),
    ('ピジョット', 'メガピジョット', '-Mega', 'ノーマル・飛行', 83, 80, 80, 135, 80, 121),
    ('フーディン', 'メガフーディン', '-Mega', 'エスパー', 55, 50, 65, 175, 105, 150),
    ('ヤドラン', 'メガヤドラン', '-Mega', '水・エスパー', 95, 75, 180, 130, 80, 30),
    ('ゲンガー', 'メガゲンガー', '-Mega', 'ゴースト・毒', 60, 65, 80, 170, 95, 130),
    ('ガルーラ', 'メガガルーラ', '-Mega', 'ノーマル', 105, 125, 100, 60, 100, 100),
    ('カイロス', 'メガカイロス', '-Mega', '虫・飛行', 65, 155, 120, 65, 90, 105),
    ('ギャラドス', 'メガギャラドス', '-Mega', '水・悪', 95, 155, 109, 70, 130, 81),
    ('プテラ', 'メガプテラ', '-Mega', '岩・飛行', 80, 135, 85, 70, 95, 150),
    ('ミュウツー', 'メガミュウツーX', '-Mega-X', 'エスパー・格闘', 106, 190, 100, 154, 100, 130),
    ('ミュウツー', 'メガミュウツーY', '-Mega-Y', 'エスパー', 106, 150, 70, 194, 120, 140),
    # === Gen 2 (6) ===
    ('デンリュウ', 'メガデンリュウ', '-Mega', '電気・ドラゴン', 90, 95, 105, 165, 110, 45),
    ('ハガネール', 'メガハガネール', '-Mega', '鋼・地面', 75, 125, 230, 55, 95, 30),
    ('ハッサム', 'メガハッサム', '-Mega', '虫・鋼', 70, 150, 140, 65, 100, 75),
    ('ヘラクロス', 'メガヘラクロス', '-Mega', '虫・格闘', 80, 185, 115, 40, 105, 75),
    ('ヘルガー', 'メガヘルガー', '-Mega', '悪・炎', 75, 90, 90, 140, 90, 115),
    ('バンギラス', 'メガバンギラス', '-Mega', '岩・悪', 100, 164, 150, 95, 120, 71),
    # === Gen 3 (20) ===
    ('ジュカイン', 'メガジュカイン', '-Mega', '草・ドラゴン', 70, 110, 75, 145, 85, 145),
    ('バシャーモ', 'メガバシャーモ', '-Mega', '炎・格闘', 80, 160, 80, 130, 80, 100),
    ('ラグラージ', 'メガラグラージ', '-Mega', '水・地面', 100, 150, 110, 95, 110, 70),
    ('サーナイト', 'メガサーナイト', '-Mega', 'エスパー・フェアリー', 68, 85, 65, 165, 135, 100),
    ('ヤミラミ', 'メガヤミラミ', '-Mega', '悪・ゴースト', 50, 85, 125, 85, 115, 20),
    ('クチート', 'メガクチート', '-Mega', '鋼・フェアリー', 50, 105, 125, 55, 95, 50),
    ('ボスゴドラ', 'メガボスゴドラ', '-Mega', '鋼', 70, 140, 230, 60, 80, 50),
    ('チャーレム', 'メガチャーレム', '-Mega', '格闘・エスパー', 60, 100, 85, 80, 85, 100),
    ('ライボルト', 'メガライボルト', '-Mega', '電気', 70, 75, 80, 135, 80, 135),
    ('サメハダー', 'メガサメハダー', '-Mega', '水・悪', 70, 140, 70, 110, 65, 105),
    ('バクーダ', 'メガバクーダ', '-Mega', '炎・地面', 70, 120, 100, 145, 105, 20),
    ('チルタリス', 'メガチルタリス', '-Mega', 'ドラゴン・フェアリー', 75, 110, 110, 110, 105, 80),
    ('ジュペッタ', 'メガジュペッタ', '-Mega', 'ゴースト', 64, 165, 75, 93, 83, 75),
    ('アブソル', 'メガアブソル', '-Mega', '悪', 65, 150, 60, 115, 60, 115),
    ('オニゴーリ', 'メガオニゴーリ', '-Mega', '氷', 80, 120, 80, 120, 80, 100),
    ('ボーマンダ', 'メガボーマンダ', '-Mega', 'ドラゴン・飛行', 95, 145, 130, 120, 90, 120),
    ('メタグロス', 'メガメタグロス', '-Mega', '鋼・エスパー', 80, 145, 150, 105, 110, 110),
    ('ラティアス', 'メガラティアス', '-Mega', 'ドラゴン・エスパー', 80, 100, 120, 140, 150, 110),
    ('ラティオス', 'メガラティオス', '-Mega', 'ドラゴン・エスパー', 80, 130, 100, 160, 120, 110),
    ('レックウザ', 'メガレックウザ', '-Mega', 'ドラゴン・飛行', 105, 180, 100, 180, 100, 115),
    # === Gen 4 (5) ===
    ('ミミロップ', 'メガミミロップ', '-Mega', 'ノーマル・格闘', 65, 136, 94, 54, 96, 135),
    ('ガブリアス', 'メガガブリアス', '-Mega', 'ドラゴン・地面', 108, 170, 115, 120, 95, 92),
    ('ルカリオ', 'メガルカリオ', '-Mega', '格闘・鋼', 70, 145, 88, 140, 70, 112),
    ('ユキノオー', 'メガユキノオー', '-Mega', '草・氷', 90, 132, 105, 132, 105, 30),
    ('エルレイド', 'メガエルレイド', '-Mega', 'エスパー・格闘', 68, 165, 95, 65, 115, 110),
    # === Gen 5 (1) ===
    ('タブンネ', 'メガタブンネ', '-Mega', 'ノーマル・フェアリー', 103, 60, 126, 80, 126, 50),
    # === Gen 6 (1) ===
    ('ディアンシー', 'メガディアンシー', '-Mega', '岩・フェアリー', 50, 160, 110, 160, 110, 110),
    # === Pokemon ZA (25) ===
    ('ピクシー', 'メガピクシー', '-Mega', 'フェアリー・飛行', 95, 80, 93, 135, 110, 70),
    ('ウツボット', 'メガウツボット', '-Mega', '草・毒', 80, 125, 85, 135, 95, 70),
    ('スターミー', 'メガスターミー', '-Mega', '水・エスパー', 60, 140, 105, 130, 105, 120),
    ('カイリュー', 'メガカイリュー', '-Mega', 'ドラゴン・飛行', 91, 124, 115, 145, 125, 100),
    ('メガニウム', 'メガメガニウム', '-Mega', '草・フェアリー', 80, 92, 115, 143, 115, 80),
    ('オーダイル', 'メガオーダイル', '-Mega', '水・ドラゴン', 85, 160, 125, 89, 93, 78),
    ('エアームド', 'メガエアームド', '-Mega', '鋼・飛行', 65, 140, 110, 40, 100, 110),
    ('ユキメノコ', 'メガユキメノコ', '-Mega', '氷・ゴースト', 70, 80, 70, 140, 100, 120),
    ('エンブオー', 'メガエンブオー', '-Mega', '炎・格闘', 110, 148, 75, 110, 110, 75),
    ('ドリュウズ', 'メガドリュウズ', '-Mega', '地面・鋼', 110, 165, 100, 65, 65, 103),
    ('ペンドラー', 'メガペンドラー', '-Mega', '虫・毒', 60, 140, 149, 75, 99, 62),
    ('ズルズキン', 'メガズルズキン', '-Mega', '悪・格闘', 65, 130, 135, 55, 135, 68),
    ('シビルドン', 'メガシビルドン', '-Mega', '電気', 85, 145, 80, 135, 90, 80),
    ('シャンデラ', 'メガシャンデラ', '-Mega', 'ゴースト・炎', 60, 75, 110, 175, 110, 90),
    ('ブリガロン', 'メガブリガロン', '-Mega', '草・格闘', 88, 137, 172, 74, 115, 44),
    ('マフォクシー', 'メガマフォクシー', '-Mega', '炎・エスパー', 75, 69, 72, 159, 125, 134),
    ('ゲッコウガ', 'メガゲッコウガ', '-Mega', '水・悪', 72, 125, 77, 133, 81, 142),
    ('カエンジシ', 'メガカエンジシ', '-Mega', '炎・ノーマル', 86, 88, 92, 129, 86, 126),
    ('フラエッテ', 'メガフラエッテ', '-Mega', 'フェアリー', 74, 85, 87, 155, 148, 102),
    ('カラマネロ', 'メガカラマネロ', '-Mega', '悪・エスパー', 86, 102, 88, 98, 120, 88),
    ('ガメノデス', 'メガガメノデス', '-Mega', '岩・格闘', 72, 140, 130, 64, 106, 88),
    ('ドラミドロ', 'メガドラミドロ', '-Mega', '毒・ドラゴン', 65, 85, 105, 132, 163, 44),
    ('ルチャブル', 'メガルチャブル', '-Mega', '格闘・飛行', 78, 137, 100, 74, 93, 118),
    ('ジガルデ', 'メガジガルデ', '-Mega', 'ドラゴン・地面', 216, 70, 91, 216, 85, 100),
    ('ジジーロン', 'メガジジーロン', '-Mega', 'ノーマル・ドラゴン', 78, 85, 110, 160, 116, 36),
    ('タイレーツ', 'メガタイレーツ', '-Mega', '格闘', 65, 135, 135, 70, 65, 100),
    # === M次元ラッシュ (18) ===
    ('ライチュウ', 'メガライチュウX', '-Mega-X', 'でんき', 60, 135, 95, 90, 95, 110),
    ('ライチュウ', 'メガライチュウY', '-Mega-Y', 'でんき', 60, 100, 55, 160, 80, 130),
    ('チリーン', 'メガチリーン', '-Mega', 'エスパー・鋼', 75, 50, 110, 135, 120, 65),
    ('ルカリオ', 'メガルカリオZ', '-Mega-Z', 'かくとう・はがね', 70, 100, 70, 164, 70, 151),
    ('アブソル', 'メガアブソルZ', '-Mega-Z', 'あく・ゴースト', 65, 154, 60, 75, 60, 151),
    ('ムクホーク', 'メガムクホーク', '-Mega', '飛行', 85, 140, 100, 60, 90, 110),
    ('シャリタツ', 'メガシャリタツ', '-Mega', 'ドラゴン・みず', 68, 65, 90, 135, 125, 92),
    ('ニャオニクス', 'メガニャオニクス', '-Mega', 'エスパー', 74, 48, 76, 143, 101, 124),
    ('ヒードラン', 'メガヒードラン', '-Mega', '炎・鋼', 91, 120, 106, 175, 141, 67),
    ('ゴルーグ', 'メガゴルーグ', '-Mega', '地面・ゴースト', 89, 159, 105, 70, 105, 55),
    ('ケケンカニ', 'メガケケンカニ', '-Mega', '格闘・氷', 97, 157, 122, 62, 107, 33),
    ('グソクムシャ', 'メガグソクムシャ', '-Mega', '虫・鋼', 75, 150, 175, 70, 120, 40),
    ('スコヴィラン', 'メガスコヴィラン', '-Mega', '草・炎', 65, 138, 85, 138, 85, 75),
    ('キラフロル', 'メガキラフロル', '-Mega', '岩・毒', 83, 90, 105, 150, 96, 101),
    ('ダークライ', 'メガダークライ', '-Mega', '悪', 70, 120, 130, 165, 130, 85),
    ('マギアナ', 'メガマギアナ', '-Mega', '鋼・フェアリー', 80, 125, 115, 170, 115, 95),
    ('ゼラオラ', 'メガゼラオラ', '-Mega', 'でんき', 88, 157, 75, 147, 80, 153),
    ('セグレイブ', 'メガセグレイブ', '-Mega', 'ドラゴン・氷', 115, 175, 117, 105, 101, 87),
]

# Special ja name -> (en_base_name, pokedex) for pokemon not directly found by ja name
SPECIAL_NAME_MAP = {
    'シャリタツ': ('Tatsugiri', 978),
    'ニャオニクス': ('Meowstic', 678),
}


def main():
    data = load_json(DATA_PATH)

    # Build ja -> (en_base_name, pokedex) mapping from existing data
    ja_to_base = {}
    for key, val in data.items():
        ja = val.get('ja', '')
        if ja and ja not in ja_to_base:
            # Use the base form name (first key with '-' removed isn't reliable, use key directly)
            base_name = key.split('-')[0] if '-' in key else key
            ja_to_base[ja] = (base_name, val['pokedex'])

    # Add special mappings
    ja_to_base.update(SPECIAL_NAME_MAP)

    # Build mega entries keyed by pokedex number for insertion
    # mega_by_pokedex[pokedex] = [(en_key, entry_dict), ...]
    mega_by_pokedex = {}
    for base_ja, mega_ja, suffix, type_str, hp, atk, def_, spa, spd, spe in MEGA_DATA:
        if base_ja not in ja_to_base:
            print(f"WARNING: Base pokemon '{base_ja}' not found in pokemons.json!")
            continue

        base_en, pokedex = ja_to_base[base_ja]
        en_key = base_en + suffix
        types = parse_types(type_str)
        if types is None:
            print(f"WARNING: Could not parse types '{type_str}' for {en_key}, using base types")
            continue

        entry = {
            'pokedex': pokedex,
            'ja': mega_ja,
            'en': en_key,
            'HP': hp,
            'Atk': atk,
            'Def': def_,
            'Spa': spa,
            'Spd': spd,
            'Spe': spe,
            'types': types,
        }

        if pokedex not in mega_by_pokedex:
            mega_by_pokedex[pokedex] = []
        mega_by_pokedex[pokedex].append((en_key, entry))

    # Build new ordered dict, inserting megas after all forms of same pokedex
    new_data = {}
    prev_pokedex = None
    pending_megas = None

    for key, val in data.items():
        current_pokedex = val['pokedex']

        # If pokedex changed, flush pending megas from previous pokedex
        if current_pokedex != prev_pokedex and pending_megas is not None:
            for mega_key, mega_entry in pending_megas:
                new_data[mega_key] = mega_entry
            pending_megas = None

        # Check if we need to set up pending megas for current pokedex
        if current_pokedex != prev_pokedex and current_pokedex in mega_by_pokedex:
            pending_megas = mega_by_pokedex[current_pokedex]

        new_data[key] = val
        prev_pokedex = current_pokedex

    # Flush any remaining pending megas (for the last pokedex group)
    if pending_megas is not None:
        for mega_key, mega_entry in pending_megas:
            new_data[mega_key] = mega_entry

    added = len(new_data) - len(data)
    print(f"Original entries: {len(data)}")
    print(f"New entries: {len(new_data)}")
    print(f"Added: {added}")

    save_json(DATA_PATH, new_data)
    print(f"Saved to {DATA_PATH}")

    # Verification: check sprite coverage for Gen 1-6 megas
    sprite_dir = os.path.join(os.path.dirname(__file__), '..', 'icons', 'v2')
    gen16_count = 48  # First 48 entries in MEGA_DATA
    missing_sprites = []
    for i, (base_ja, mega_ja, suffix, type_str, *stats) in enumerate(MEGA_DATA[:gen16_count]):
        if base_ja not in ja_to_base:
            continue
        base_en, _ = ja_to_base[base_ja]
        en_key = base_en + suffix
        sprite_path = os.path.join(sprite_dir, f"{en_key}.webp")
        if not os.path.exists(sprite_path):
            missing_sprites.append(en_key)

    if missing_sprites:
        print(f"\nMissing sprites ({len(missing_sprites)}):")
        for name in missing_sprites:
            print(f"  {name}")
    else:
        print(f"\nAll {gen16_count} Gen 1-6 mega sprites found!")


if __name__ == '__main__':
    main()
