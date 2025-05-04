from script.json_utils import load_json, save_json
from script.copy_file import copy_file
from collections import OrderedDict

pokemons = load_json("./v1/pokemons.json")
result = {}

for key, value in pokemons.items():
    newKey = value["en"].replace(" ", "")
    pokedex = key if "_" not in key else key.split("_")[0]

    ordered_value = OrderedDict()
    ordered_value["pokedex"] = pokedex  # 先にpokedexを追加
    ordered_value.update(value)  # 元のデータを追加

    # 新しいキーでresultに追加
    result[newKey] = ordered_value

    copy_file(f"icons/sv/pokeicon/{key}.png", f"pokeicon/{newKey}.png")

save_json("pokemons.json", result)
