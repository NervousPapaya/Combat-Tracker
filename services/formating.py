from services.maths import is_whole_number
from models.combatant import Combatant

def abilities_to_list(ab_dict):
    return [(ability_name, ab_dict[ability_name].max, None) for ability_name in ab_dict]

def spell_slots_to_list(spell_dict):
    return [(f"Level {lvl}", count, lvl) for lvl, count in spell_dict.items() if count > 0]

def format_conditions(combatant: Combatant):
    if not combatant.conditions:
        return ""
    sorted_cond = sorted( combatant.conditions, key = lambda c : c.name )
    cond_strings = []
    for c in sorted_cond:
        if c.indefinite:
            cond_strings.append(c.name)
        else:
            cond_strings.append(f"{c.name} ({c.rounds_left})")
    return ", ".join(cond_strings)
    #cond_str = ", ".join(f"{c.name} ({c.rounds_left})" for c in combatant.conditions if c.indefinite == False)
    #return ", ".join(f"{c.name} ({c.rounds_left})" for c in combatant.conditions)

def format_initiative(x):
    return str(int(x)) if is_whole_number(x) else str(x)

