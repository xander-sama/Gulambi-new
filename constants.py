import os
import json
import random

# Pokémon Categories
SAFARI = set([])
NEST_BALL = set([])
ULTRA_BALL = set([])
GREAT_BALL = set([])
REGULAR_BALL = set([
    "Magikarp", "Darumaka", "Darmanitan", "Wishiwashi", "Drakloak", "Duraludon", "Rotom", 
    "Tentacruel", "Snorlax", "Overqwil", "Munchlax", "Kleavor", "Fennekin", "Delphox", "Braixen", 
    "Axew", "Fraxure", "Haxorus", "Floette", "Flabebe", "Rufflet", "Porygon", "Porygon2", "Mankey", 
    "Primeape", "Dratini", "Shellder", "Gible", "Gabite", "Dragonair", "Golett", "Goomy", "Vikavolt", 
    "Vullaby", "Litwick", "Lampent", "Wimpod", "Buneary", "Ursaring", "Teddiursa", "Hawlucha", "Abra", 
    "Kadabra", "Turtonator", "Jolteon", "Dwebble", "Crustle", "Starly", "Stantler", "Rhyhorn", "Staryu", 
    "Starmie", "Tauros", "Lapras", "Vaporeon", "Cyndaquil", "Quilava", "Typhlosion", "Totodile", "Croconaw", 
    "Feraligatr", "Espeon", "Slakoth", "Vigoroth", "Lotad", "Lombre", "Ludicolo", "Treecko", "Grovyle", 
    "Electrike", "Growlithe", "Monferno", "Piplup", "Prinplup", "Chimchar", "Sirfetch'd", 
    "Staravia", "Bagon", "Shelgon", "Salamence", "Tepig", "Pignite", "Spiritomb", "Togekiss", "Skorupi", 
    "Drilbur", "Timburr", "Gurdurr", "Scraggy", "Scrafty", "Cofagrigus", "Zorua", "Zoroark", "Cinccino", 
    "Frillish", "Jellicent", "Karrablast", "Escavalier", "Ferroseed", "Mienfoo", "Mienshao", "Cryogonal", 
    "Shelmet", "Accelgor", "Helioptile", "Heliolisk", "Tyrunt", "Tyrantrum", "Sylveon", "Litleo", "Pyroar", 
    "Chespin", "Quilladin", "Chesnaught", "Durant", "Deino", "Phantump", "Trevenant", "Pumpkaboo", "Gourgeist", 
    "Popplio", "Brionne", "Litten", "Torracat", "Rowlet", "Dartrix", "Grookey", "Thwackey", "Rillaboom", 
    "Scorbunny", "Raboot", "Orbeetle", "Rookidee", "Corvisquire", "Sobble", "Drizzile", "Inteleon", "Dracozolt", 
    "Dracovish", "Morpeko", "Sneasler", "Toxapex", "Mareanie", "Volcarona", "Tentacool", "Larvesta", 
    "Charmeleon", "Charmander", "Togetic", "Togepi", "Druddigon", "Dhelmise", "Runerigus", "Lucario", 
    "Unfezant", "Tranquill", "Pidove", "Barraskewda", "Arrokuda", "Zubat", "Golbat", "Gastly", "Haunter", 
    "Clauncher", "Clawitzer", "Froslass", "Cutiefly", "Ribombee", "Arctozolt", "Arctovish", "Chewtle", 
    "Cufant", "Impidimp", "Morgrem", "Hatenna", "Hattrem", "Trumbeak", "Charjabug", "Rockruff", "Mudbray", 
    "Bounsweet", "Steenee", "Sliggoo", "Squirtle", "Wartortle", "Mantine", "Mantyke", "Gligar", "Gliscor", "Abra"
])

REPEAT_BALL = set([])

# Hunting Team
POKEMON_TEAM = [
    "Applin", "Abomasnow", "Golurk",
    "Gardevoir", "Arceus", "Xerneas"
]   # Add your preferred Pokémon for hunting here

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

MAX_RETRIES = 5  # Number of times to retry clicking
RETRY_COOLDOWN = 3  # Cooldown (in seconds) between retries
COOLDOWN = lambda: random.randint(2, 3)  # Random cooldown between 3 and 6 seconds
PERIODICALLY_GUESS_SECONDS = 120  # Guess cooldown
PERIODICALLY_HUNT_SECONDS = 300  # Hunt cooldown (5 minutes)
HEXA_BOT_ID = 572621020  # ID of the Hexa bot

# Auto-Battle Constants
HUNT_DAILY_LIMIT_REACHED = "Daily hunt limit reached. Auto-battle stopped."
SHINY_FOUND = "Shiny Pokémon found! Auto-battle stopped for {0}."

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
