import os
import json
import random

# JSON File for Saving Categories
CATEGORIES_FILE = "pokemon_categories.json"

# Default Pokémon Categories
DEFAULT_CATEGORIES = {
    "safari": [],
    "nest_ball": [],
    "ultra_ball": [],
    "great_ball": ["Abra"],
    "regular_ball": [],
    "repeat_ball": [
        "Venusaur", "Charizard", "Blastoise", "Beedrill", "Alakazam", "Slowbro",
        "Mewtwo", "Aerodactyl", "Ampharos", "Steelix", "Scizor",
        "Sceptile", "Blaziken", "Swampert", "Gardevoir", "Sableye", "Mawile",
        "Aggron", "Medicham", "Manectric", "Sharpedo", "Camerupt", "Altaria", "Banette", "Absol", "Glalie",
        "Metagross", "Lucario", "Abomasnow", "Gallade", "Audino",
        "Blacephalon", "Buzzwole", "Cobalion", "Cosmog", "Cosmoem", "Deoxys", "Diancie", "Dialga",
        "Eternatus", "Genesect", "Giratina", "Glastrier", "Groudon", "Ho-oh", "Hoopa", "Jirachi",
        "Kartana", "Keldeo", "Kubfu", "Kyogre", "Kyurem", "Landorus", "Lugia", "Magearna", "Marshadow",
        "Mewtwo", "Necrozma", "Palkia", "Pheromosa", "Rayquaza", "Regieleki", "Regigigas", "Reshiram",
        "Shaymin", "Spectrier", "Terrakion", "Victini", "Virizion", "Xerneas", "Yveltal", "Zacian",
        "Zamazenta", "Zekrom", "Zeraora", "Zygarde"
    ]
}

# Load Pokémon Categories from JSON File (if exists)
if os.path.exists(CATEGORIES_FILE):
    with open(CATEGORIES_FILE, "r") as f:
        try:
            loaded_data = json.load(f)
            POKEMON_CATEGORIES = {k: set(v) for k, v in loaded_data.items()}
        except json.JSONDecodeError:
            POKEMON_CATEGORIES = {k: set(v) for k, v in DEFAULT_CATEGORIES.items()}
else:
    POKEMON_CATEGORIES = {k: set(v) for k, v in DEFAULT_CATEGORIES.items()}

def save_pokemon_categories():
    """Saves the updated Pokémon categories to a JSON file."""
    with open(CATEGORIES_FILE, "w") as f:
        json.dump({k: list(v) for k, v in POKEMON_CATEGORIES.items()}, f, indent=4)

# Owner and Bot Information
OWNER_NAME = "Enryu"
BOT_VERSION = "1.0"

# Commands
PING_COMMAND_REGEX = r'^\.ping$'
ALIVE_COMMAND_REGEX = r'^\.alive$'
HELP_COMMAND_REGEX = r'^\.help$'
EVAL_COMMAND_REGEX = r'^\.eval (.+)'
GUESSER_COMMAND_REGEX = r'^\.guess (on|off|stats)$'
HUNTER_COMMAND_REGEX = r'^\.hunt (on|off|stats)$'
LIST_COMMAND_REGEX = r'^\.list(?:\s+(\w+))?$'  # Now supports `.list <category>`

# AFK Commands
AFK_COMMAND_REGEX = r'^\.afk(?: |$)(.*)'  # Matches `.afk` or `.afk <message>`
UNAFK_COMMAND_REGEX = r'^\.unafk$'  # Matches `.unafk`

# Timing and Limits
COOLDOWN = lambda: random.randint(3, 6)
PERIODICALLY_GUESS_SECONDS = 120
PERIODICALLY_HUNT_SECONDS = 300
HEXA_BOT_ID = 572621020

# API Credentials
API_ID = int(os.getenv('API_ID'))
API_HASH = os.getenv('API_HASH')
SESSION = os.getenv('SESSION')

# Chat ID
CHAT_ID = int(os.getenv('CHAT_ID'))

# Load Pokémon Data
with open('pokemon.json', 'r') as f:
    POKEMON = json.load(f)

__version__ = '1.0.0'
