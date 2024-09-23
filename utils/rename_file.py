import os


def rename_file(current_file_path: str, new_file_path: str):
    try:
        os.rename(current_file_path, new_file_path)
    except FileNotFoundError:
        print(f"{current_file_path} が見つかりません。")
    except Exception as e:
        print(f"エラーが発生しました: {e}")
