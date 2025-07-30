def format_npc(npc_dict):
    """Nicely formats an NPC dictionary into a string for printing."""
    return f"{npc_dict['name']} ({npc_dict['race']}) - {npc_dict['trait']}"