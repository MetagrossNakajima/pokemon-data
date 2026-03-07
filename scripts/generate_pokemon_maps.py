import csv

def generate_pokemon_maps_from_csv(csv_path, output_path):
    """Pokemon CSVファイルを読み込んでTSのMapコードを生成する（jaToKey, enToKey形式）"""
    
    # 言語マッピング (CSVの列順) - Pokemon CSVは同じ構造
    languages = [
        ('ja', 'Japanese'),
        ('en', 'English'), 
        ('fr', 'French'),
        ('de', 'German'),
        ('it', 'Italian'),
        ('es', 'Spanish'),
        ('ko', 'Korean'),
        ('zhCn', 'Chinese (Simplified)'),
        ('zhTw', 'Chinese (Traditional)')
    ]
    
    # CSVを読み込み
    with open(csv_path, 'r', encoding='utf-8') as file:
        csv_reader = csv.reader(file)
        rows = list(csv_reader)
    
    # マップを準備
    maps = {}
    
    # 各言語からkeyへのマップ（keyは英語名からスペースを除去）
    for i, (lang_code, _) in enumerate(languages):
        map_name = f"{lang_code}ToKey"
        maps[map_name] = []
    
    # 各行を処理
    for row in rows:
        if len(row) == 9:  # 9列すべてがある行のみ処理
            en_text = row[1].strip()  # 英語は2列目 (index 1)
            
            # keyは英語名からスペースを除去
            key = en_text.replace(' ', '')
            
            for i, (lang_code, _) in enumerate(languages):
                source_text = row[i].strip()
                
                if source_text and key:
                    map_name = f"{lang_code}ToKey"
                    # エスケープ処理
                    source_escaped = source_text.replace('\\', '\\\\').replace('"', '\\"')
                    key_escaped = key.replace('\\', '\\\\').replace('"', '\\"')
                    maps[map_name].append(f'  ["{source_escaped}", "{key_escaped}"]')
    
    # TypeScriptコードを生成
    ts_content = ""
    for map_name, entries in maps.items():
        if entries:  # エントリがある場合のみ出力
            ts_content += f"export const {map_name} = new Map([\n"
            ts_content += ",\n".join(entries)
            ts_content += "\n]);\n\n"
    
    # ファイルに書き出し
    with open(output_path, 'w', encoding='utf-8') as file:
        file.write(ts_content)
    
    print(f"TypeScript Pokemon maps generated: {output_path}")
    print(f"Generated {len([m for m in maps.values() if m])} maps")

if __name__ == "__main__":
    # pokemon.csvからmapsを生成
    generate_pokemon_maps_from_csv("i18n/pokemon.csv", "generated_pokemon_maps.ts")