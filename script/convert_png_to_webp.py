"""icons/v2/ の PNG を WebP (q90) に一括変換し、元 PNG を削除するスクリプト."""

import os
import glob
from PIL import Image

ICONS_DIR = os.path.join(os.path.dirname(__file__), "..", "icons", "v2")


def convert():
    png_files = sorted(glob.glob(os.path.join(ICONS_DIR, "*.png")))
    total = len(png_files)
    print(f"対象ファイル数: {total}")

    if total == 0:
        print("PNGファイルが見つかりません")
        return

    total_png_size = 0
    total_webp_size = 0
    fallback_count = 0

    for i, png_path in enumerate(png_files, 1):
        webp_path = png_path.rsplit(".", 1)[0] + ".webp"
        png_size = os.path.getsize(png_path)

        img = Image.open(png_path)
        # lossy q90
        img.save(webp_path, "WEBP", quality=90)
        webp_size = os.path.getsize(webp_path)

        # PNGより大きくなったらlosslessにフォールバック
        if webp_size >= png_size:
            img.save(webp_path, "WEBP", lossless=True)
            webp_size = os.path.getsize(webp_path)
            fallback_count += 1

            # それでもまだ大きい場合は警告（削除はしない）
            if webp_size >= png_size:
                print(f"  WARNING: {os.path.basename(png_path)} losslessでも大きい "
                      f"(PNG={png_size}, WebP={webp_size})")

        total_png_size += png_size
        total_webp_size += webp_size

        # 元PNGを削除
        os.remove(png_path)

        if i % 200 == 0 or i == total:
            print(f"  {i}/{total} 完了")

    # 検証
    webp_files = glob.glob(os.path.join(ICONS_DIR, "*.webp"))
    remaining_png = glob.glob(os.path.join(ICONS_DIR, "*.png"))

    print(f"\n=== 結果サマリ ===")
    print(f"変換数: {total}")
    print(f"WebPファイル数: {len(webp_files)}")
    print(f"残存PNG数: {len(remaining_png)}")
    print(f"losslessフォールバック: {fallback_count}件")
    print(f"変換前合計: {total_png_size / 1024 / 1024:.2f} MB")
    print(f"変換後合計: {total_webp_size / 1024 / 1024:.2f} MB")
    ratio = (1 - total_webp_size / total_png_size) * 100
    print(f"圧縮率: {ratio:.1f}% 削減")


if __name__ == "__main__":
    convert()
