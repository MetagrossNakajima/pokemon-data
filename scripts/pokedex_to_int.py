import os
import sys

sys.path.append(os.path.dirname(__file__))
from json_utils import load_json, save_json

DATA_PATH = os.path.join(os.path.dirname(__file__), '..', 'data', 'v1', 'pokemons.json')
pokemons = load_json(DATA_PATH)
result = {}


for key, value in pokemons.items():
    result[key] = value
    result[key]["pokedex"] = int(value["pokedex"])

save_json(DATA_PATH, result)
