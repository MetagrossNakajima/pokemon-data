from script.json_utils import load_json, save_json

pokemons = load_json("./v1/pokemons.json")
result = {}


for key, value in pokemons.items():
    result[key] = value
    result[key]["pokedex"] = int(value["pokedex"])

save_json("./v1/pokemons.json", result)
