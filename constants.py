import os
import json
import random

# File to store dynamically added Pokémon
POKEMON_DATA_FILE = "pokemon_categories.json"

# Default Pokémon Categories
DEFAULT_CATEGORIES = {
    "safari": [],
    "nest": [],
    "ultra": [],
    "great": [],
    "regular": [],
    "repeat": [
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

# Load Pokémon Categories from file or use default
if os.path.exists(POKEMON_DATA_FILE):
    with open(POKEMON_DATA_FILE, "r") as f:
        POKEMON_CATEGORIES = json.load(f)
else:
    POKEMON_CATEGORIES = DEFAULT_CATEGORIES

# Function to save Pokémon categories to file
def save_pokemon_data():
    with open(POKEMON_DATA_FILE, "w") as f:
        json.dump(POKEMON_CATEGORIES, f, indent=4)

# Owner and Bot Information
OWNER_NAME = "Enryu"
BOT_VERSION = "1.0"

# Command Regex Patterns
PING_COMMAND_REGEX = r'^\.ping$'
ALIVE_COMMAND_REGEX = r'^\.alive$'
HELP_COMMAND_REGEX = r'^\.help$'
EVAL_COMMAND_REGEX = r'^\.eval (.+)'
GUESSER_COMMAND_REGEX = r'^\.guess (on|off|stats)$'
HUNTER_COMMAND_REGEX = r'^\.hunt (on|off|stats)$'
LIST_COMMAND_REGEX = r'^\.list(?:\s+(\w+))?$'  # `.list <category>`
ADD_COMMAND_REGEX = r'^\.add (\w+) (\w+)$'  # `.add <pokemon> <category>`

# AFK Commands
AFK_COMMAND_REGEX = r'^\.afk(?: |$)(.*)'  # Matches `.afk` or `.afk <message>`
UNAFK_COMMAND_REGEX = r'^\.unafk$'  # Matches `.unafk`

# Timing and Limits
COOLDOWN = lambda: random.randint(3, 6)
PERIODICALLY_GUESS_SECONDS = 120
PERIODICALLY_HUNT_SECONDS = 300
HEXA_BOT_ID = 572621020

# API Credentials
API_ID = int(os.getenv('API_ID', 0))
API_HASH = os.getenv('API_HASH', "")
SESSION = os.getenv('SESSION', "")

# Chat ID
CHAT_ID = int(os.getenv('CHAT_ID', 0))

# Load Pokémon Data
with open('pokemon.json', 'r') as f:
    POKEMON = json.load(f)

__version__ = '1.0.0'
