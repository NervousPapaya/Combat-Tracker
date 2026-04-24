from services.maths import is_whole_number
from models.combatant import Combatant

def abilities_to_list(ab_dict):
    return [(ability_name, ab_dict[ability_name].max, None) for ability_name in ab_dict]

def spell_slots_to_list(spell_dict):
    return [(f"Level {lvl}", count, lvl) for lvl, count in spell_dict.items() if count > 0]

def format_conditions(combatant: Combatant):
    if not combatant.conditions:
        return ""
    return ", ".join(f"{c.name} ({c.rounds_left})" for c in combatant.conditions)

def format_initiative(x):
    return str(int(x)) if is_whole_number(x) else str(x)

