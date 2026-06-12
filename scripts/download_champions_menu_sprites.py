"""Download Pokemon Champions menu sprites into icons/v3/pokemons as WebP."""

from __future__ import annotations

import json
import os
import re
import sys
import time
import urllib.parse
import urllib.request
from io import BytesIO

from PIL import Image


API_URL = "https://archives.bulbagarden.net/w/api.php"
CATEGORY = "Category:Champions_menu_sprites"
SAVE_DIR = os.path.join(os.path.dirname(__file__), "..", "icons", "v3", "pokemons")
POKEMONS_JSON = os.path.join(os.path.dirname(__file__), "..", "data", "v1", "pokemons.json")
USER_AGENT = "PokemonDataBot/1.0 (local asset sync)"
DELAY = 0.2


def request_json(params: dict[str, str]) -> dict:
    url = f"{API_URL}?{urllib.parse.urlencode(params)}"
    req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    with urllib.request.urlopen(req, timeout=30) as resp:
        return json.loads(resp.read())


def fetch_category_titles() -> list[str]:
    params = {
        "action": "query",
        "list": "categorymembers",
        "cmtitle": CATEGORY,
        "cmnamespace": "6",
        "cmlimit": "max",
        "format": "json",
    }
    titles: list[str] = []

    while True:
        data = request_json(params)
        titles.extend(member["title"] for member in data["query"]["categorymembers"])
        if "continue" not in data:
            return sorted(titles)
        params.update(data["continue"])


def fetch_image_urls(titles: list[str]) -> dict[str, str]:
    urls: dict[str, str] = {}

    for i in range(0, len(titles), 50):
        chunk = titles[i : i + 50]
        data = request_json(
            {
                "action": "query",
                "prop": "imageinfo",
                "iiprop": "url",
                "titles": "|".join(chunk),
                "format": "json",
            }
        )

        for page in data["query"]["pages"].values():
            imageinfo = page.get("imageinfo")
            if imageinfo:
                urls[page["title"]] = imageinfo[0]["url"]

    return urls


def load_pokemon_data() -> dict[str, dict]:
    with open(POKEMONS_JSON, encoding="utf-8") as f:
        return json.load(f)


def build_base_name_by_pokedex(data: dict[str, dict]) -> dict[int, str]:
    base_names: dict[int, str] = {}
    for name, info in data.items():
        pdex = info["pokedex"]
        if pdex not in base_names or info.get("formType") == "base":
            base_names[pdex] = name
    return base_names


def normalize_suffix(suffix: str) -> str:
    return suffix.replace(" ", "-")


def resolve_name(title: str, data: dict[str, dict], base_names: dict[int, str]) -> str:
    match = re.fullmatch(r"File:Menu CP (\d{4})(?:-(.+))?\.png", title)
    if not match:
        raise ValueError(f"Unexpected title format: {title}")

    pdex = int(match.group(1))
    suffix = match.group(2)
    base_name = base_names[pdex]

    if suffix is None:
        return base_name

    normalized = normalize_suffix(suffix)
    candidates = [f"{base_name}-{normalized}"]

    if suffix == "Female":
        candidates.append(f"{base_name}-F")
    elif suffix == "Jumbo":
        candidates.append(f"{base_name}-Super")

    for candidate in candidates:
        if candidate in data:
            return candidate

    return candidates[0]


def download_bytes(url: str) -> bytes:
    req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    with urllib.request.urlopen(req, timeout=30) as resp:
        return resp.read()


def save_webp(png_bytes: bytes, save_path: str) -> None:
    png_size = len(png_bytes)
    image = Image.open(BytesIO(png_bytes))
    image.load()

    lossy = BytesIO()
    image.save(lossy, "WEBP", quality=90)
    webp_bytes = lossy.getvalue()

    if len(webp_bytes) >= png_size:
        lossless = BytesIO()
        image.save(lossless, "WEBP", lossless=True)
        webp_bytes = lossless.getvalue()

    with open(save_path, "wb") as f:
        f.write(webp_bytes)


def main() -> int:
    data = load_pokemon_data()
    base_names = build_base_name_by_pokedex(data)
    os.makedirs(SAVE_DIR, exist_ok=True)

    titles = fetch_category_titles()
    urls = fetch_image_urls(titles)

    downloaded = 0
    missing_urls: list[str] = []
    unresolved: list[str] = []

    for i, title in enumerate(titles, 1):
        name = resolve_name(title, data, base_names)
        if name not in data:
            unresolved.append(name)

        url = urls.get(title)
        if not url:
            missing_urls.append(title)
            continue

        save_path = os.path.join(SAVE_DIR, f"{name}.webp")
        png_bytes = download_bytes(url)
        save_webp(png_bytes, save_path)
        downloaded += 1

        if i % 50 == 0 or i == len(titles):
            print(f"{i}/{len(titles)} processed")
        time.sleep(DELAY)

    print(f"Downloaded: {downloaded}")
    print(f"Missing URLs: {len(missing_urls)}")
    print(f"Names not present in data/v1/pokemons.json: {len(unresolved)}")
    for name in unresolved:
        print(f"  {name}")

    return 1 if missing_urls else 0


if __name__ == "__main__":
    sys.exit(main())
