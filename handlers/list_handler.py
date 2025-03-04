from telethon import events
import constants

async def list_pokemon(event):
    """Handles the `.list` command by showing Pokémon based on the specified category."""
    args = event.pattern_match.group(1)

    if not args:
        await event.edit(
            "**Usage:** `.list <category>`\n\n"
            "**Available categories:**\n"
            "- `regular`\n"
            "- `repeat`\n"
            "- `ultra`\n"
            "- `great`\n"
            "- `nest`\n"
            "- `safari`"
        )
        return

    category = args.lower()
    if category not in constants.POKEMON_CATEGORIES:
        await event.edit(f"**Invalid category!**\nUse one of: {', '.join(constants.POKEMON_CATEGORIES.keys())}")
        return

    pokemon_list = constants.POKEMON_CATEGORIES[category]
    if not pokemon_list:
        await event.edit(f"No Pokémon found in `{category}` category.")
        return

    formatted_list = ", ".join(sorted(pokemon_list))  
    await event.edit(f"**{category.capitalize()} Ball Pokémon:**\n{formatted_list}")
