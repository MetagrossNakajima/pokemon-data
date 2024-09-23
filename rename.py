from utils.json_utils import load_json, save_json
from utils.rename_file import rename_file

pokemons = load_json("./v1/pokemons.json")
result = {}

for key, value in pokemons.items():
    newKey = value["en"].replace(" ", "")
    pokedex = key if "_" not in key else key.split("_")[0]

    result[newKey] = value
    result[newKey]["pokedex"] = pokedex

    rename_file(f"icons/sv/pokeicon/{key}.png", f"pokeicon/{newKey}.png")

save_json("pokemons.json", result)
