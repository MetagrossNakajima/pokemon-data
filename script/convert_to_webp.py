import sys
import os
from pathlib import Path
from PIL import Image

QUALITY = 70
SUPPORTED_EXTENSIONS = {".png", ".jpg", ".jpeg", ".gif", ".bmp", ".tiff", ".webp"}


def convert_to_webp(input_dir: str) -> None:
    input_path = Path(input_dir)
    if not input_path.is_dir():
        print(f"エラー: ディレクトリが見つかりません: {input_dir}")
        sys.exit(1)

    output_path = input_path.parent / f"{input_path.name}_webp"
    output_path.mkdir(exist_ok=True)

    files = sorted(
        f for f in input_path.iterdir()
        if f.is_file() and f.suffix.lower() in SUPPORTED_EXTENSIONS
    )

    if not files:
        print("対象の画像ファイルが見つかりません")
        sys.exit(1)

    total_original = 0
    total_converted = 0

    print(f"入力: {input_path}")
    print(f"出力: {output_path}")
    print(f"品質: {QUALITY}%")
    print(f"対象: {len(files)} ファイル")
    print("-" * 70)
    print(f"{'ファイル名':<40} {'変換前':>8} {'変換後':>8} {'削減率':>7}")
    print("-" * 70)

    for f in files:
        original_size = f.stat().st_size
        out_file = output_path / f"{f.stem}.webp"

        img = Image.open(f)
        img.save(out_file, "WEBP", quality=QUALITY)

        converted_size = out_file.stat().st_size
        ratio = (1 - converted_size / original_size) * 100 if original_size > 0 else 0

        total_original += original_size
        total_converted += converted_size

        print(
            f"{f.name:<40} "
            f"{format_size(original_size):>8} "
            f"{format_size(converted_size):>8} "
            f"{ratio:>6.1f}%"
        )

    print("-" * 70)
    total_ratio = (1 - total_converted / total_original) * 100 if total_original > 0 else 0
    print(
        f"{'合計':<40} "
        f"{format_size(total_original):>8} "
        f"{format_size(total_converted):>8} "
        f"{total_ratio:>6.1f}%"
    )


def format_size(size: int) -> str:
    if size < 1024:
        return f"{size} B"
    elif size < 1024 * 1024:
        return f"{size / 1024:.1f} KB"
    else:
        return f"{size / (1024 * 1024):.1f} MB"


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print(f"使い方: python {sys.argv[0]} <画像ディレクトリ>")
        sys.exit(1)
    convert_to_webp(sys.argv[1])
