import argparse
import sys
from pathlib import Path
from typing import Iterable, Iterator, Optional, Tuple

try:
    from PIL import Image
except ImportError as exc:
    raise SystemExit(
        "Pillow is required. Install it with `pip install Pillow`."
    ) from exc


PNG_SUFFIX = ".png"
WEBP_SUFFIX = ".webp"


def iter_png_files(roots: Iterable[Path], recursive: bool) -> Iterator[Tuple[Path, Path]]:
    """
    Yield (png_file, root_dir) pairs for every PNG discovered in the provided roots.
    The root_dir entry is used to compute relative paths when an output directory is supplied.
    """
    for root in roots:
        if not root.exists():
            print(f"[warn] path not found: {root}", file=sys.stderr)
            continue

        if root.is_file():
            if root.suffix.lower() == PNG_SUFFIX:
                yield root, root.parent
            else:
                print(f"[warn] not a PNG file, skipping: {root}", file=sys.stderr)
            continue

        pattern = "**/*.png" if recursive else "*.png"
        for png in sorted(root.glob(pattern)):
            if png.is_file():
                yield png, root


def compute_output_path(
    png_path: Path, root_dir: Path, output_dir: Optional[Path]
) -> Path:
    """Return the destination path for the WebP image."""
    target_base = output_dir if output_dir else png_path.parent

    if output_dir:
        try:
            relative = png_path.relative_to(root_dir)
        except ValueError:
            relative = png_path.name
        else:
            relative = relative.as_posix()
        target_path = target_base / Path(relative).with_suffix(WEBP_SUFFIX)
    else:
        target_path = target_base / png_path.with_suffix(WEBP_SUFFIX).name

    return target_path


def convert_png_to_webp(
    png_path: Path, webp_path: Path, overwrite: bool, delete_original: bool
) -> bool:
    """Convert a single PNG to WebP losslessly. Returns True on success."""
    if webp_path.exists() and not overwrite:
        print(f"[skip] {webp_path} already exists")
        return False

    webp_path.parent.mkdir(parents=True, exist_ok=True)

    try:
        with Image.open(png_path) as image:
            image.load()  # ensure image data is read before closing file

            if image.mode in ("RGBA", "RGB"):
                converted = image
            else:
                has_alpha = "transparency" in image.info
                converted = image.convert("RGBA" if has_alpha else "RGB")

            converted.save(
                webp_path,
                format="WEBP",
                lossless=True,
                quality=100,
                method=6,
            )
    except Exception as exc:  # noqa: BLE001 - surface failure to caller
        print(f"[error] failed to convert {png_path}: {exc}", file=sys.stderr)
        return False

    if delete_original:
        try:
            png_path.unlink()
        except OSError as exc:
            print(
                f"[warn] converted but failed to delete original {png_path}: {exc}",
                file=sys.stderr,
            )

    print(f"[ok] {png_path} -> {webp_path}")
    return True


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Convert PNG files to lossless WebP images."
    )
    parser.add_argument(
        "paths",
        nargs="+",
        type=Path,
        help="PNG files or directories containing PNGs.",
    )
    parser.add_argument(
        "-o",
        "--output-dir",
        type=Path,
        help="Directory to mirror the converted files into (preserves relative layout).",
    )
    parser.add_argument(
        "--recursive",
        action="store_true",
        help="Recurse into directories when searching for PNG files.",
    )
    parser.add_argument(
        "--overwrite",
        action="store_true",
        help="Overwrite existing WebP files if they already exist.",
    )
    parser.add_argument(
        "--delete-original",
        action="store_true",
        help="Delete the PNG after a successful conversion.",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()

    output_dir = args.output_dir.resolve() if args.output_dir else None
    if output_dir:
        output_dir.mkdir(parents=True, exist_ok=True)

    converted_count = 0
    seen_any = False

    for png_path, root_dir in iter_png_files(args.paths, args.recursive):
        seen_any = True
        webp_path = compute_output_path(png_path, root_dir, output_dir)
        if convert_png_to_webp(
            png_path, webp_path, args.overwrite, args.delete_original
        ):
            converted_count += 1

    if not seen_any:
        print("[info] no PNG files found.", file=sys.stderr)
        return 1

    print(f"[done] Converted {converted_count} file(s).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
