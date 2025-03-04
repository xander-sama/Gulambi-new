from telethon import events
import constants

async def add_pokemon(event):
    """Handles the `.add` command to add a Pokémon to a specific category."""
    args = event.pattern_match.group(1).split()
    
    if len(args) != 2:
        await event.edit("**Usage:** `.add <pokemon> <category>`")
        return

    pokemon, category = args[0].capitalize(), args[1].lower()

    if category not in constants.POKEMON_CATEGORIES:
        await event.edit(f"**Invalid category!**\nAvailable categories: {', '.join(constants.POKEMON_CATEGORIES.keys())}")
        return

    if pokemon in constants.POKEMON_CATEGORIES[category]:
        await event.edit(f"**{pokemon}** is already in the `{category}` category!")
        return

    constants.POKEMON_CATEGORIES[category].append(pokemon)
    constants.save_pokemon_data()  # Save changes

    await event.edit(f"**{pokemon}** has been added to the `{category}` category!")
