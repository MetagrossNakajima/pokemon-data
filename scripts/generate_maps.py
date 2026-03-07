import csv

def generate_ts_maps_from_csv(csv_path, output_path):
    """CSVファイルを読み込んで各言語から英語へのTSのMapコードを生成する"""
    
    # 言語マッピング (CSVの列順)
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
    
    # 各言語から英語へのマップを準備
    maps = {}
    for i, (lang_code, _) in enumerate(languages):
        if lang_code != 'en':  # 英語以外の言語のみ
            map_name = f"{lang_code}ToEn"
            maps[map_name] = []
    
    # 各行を処理
    for row in rows:
        if len(row) == 9:  # 9列すべてがある行のみ処理
            en_text = row[1].strip()  # 英語は2列目 (index 1)
            
            for i, (lang_code, _) in enumerate(languages):
                if lang_code != 'en':  # 英語以外の言語
                    source_text = row[i].strip()
                    
                    if source_text and en_text:
                        map_name = f"{lang_code}ToEn"
                        # エスケープ処理
                        source_escaped = source_text.replace('\\', '\\\\').replace('"', '\\"')
                        en_escaped = en_text.replace('\\', '\\\\').replace('"', '\\"')
                        maps[map_name].append(f'  ["{source_escaped}", "{en_escaped}"]')
    
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
    
    print(f"TypeScript maps generated: {output_path}")
    print(f"Generated {len([m for m in maps.values() if m])} maps")

def main():
    # move.csvからmapsを生成
    generate_ts_maps_from_csv("i18n/move.csv", "generated_move_maps.ts")

if __name__ == "__main__":
    main()