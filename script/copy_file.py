import shutil


def copy_file(src_file_path, dest_file_path):
    try:
        shutil.copy(src_file_path, dest_file_path)
    except FileNotFoundError:
        print(f"{src_file_path} が見つかりません。")
    except Exception as e:
        print(f"エラーが発生しました: {e}")
