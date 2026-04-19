import uuid
import os
from models.combatant import Combatant, Ability
import json
from filehandling.filehandling import make_output, create_output_path
from dataclasses import asdict

class CombatManager:
    @property
    def turn_order(self):
        """This property stores the turn order.
        It is a list of the combatant ids sorted in descending by initiative."""
        return [c.id for c in sorted(self.combatants.values(), key=lambda c: (-c.initiative, c.id))]

    # Setting up a dictionary of dictionaries which stores spellcaster  based on caster level as keys.
    full_caster_progression = {0: {1: 0, 2: 0, 3: 0, 4: 0, 5: 0, 6: 0, 7: 0, 8: 0, 9: 0},
                               1: {1: 2, 2: 0, 3: 0, 4: 0, 5: 0, 6: 0, 7: 0, 8: 0, 9: 0},
                               2: {1: 3, 2: 0, 3: 0, 4: 0, 5: 0, 6: 0, 7: 0, 8: 0, 9: 0},
                               3: {1: 4, 2: 2, 3: 0, 4: 0, 5: 0, 6: 0, 7: 0, 8: 0, 9: 0},
                               4: {1: 4, 2: 3, 3: 0, 4: 0, 5: 0, 6: 0, 7: 0, 8: 0, 9: 0},
                               5: {1: 4, 2: 3, 3: 2, 4: 0, 5: 0, 6: 0, 7: 0, 8: 0, 9: 0},
                               6: {1: 4, 2: 3, 3: 3, 4: 0, 5: 0, 6: 0, 7: 0, 8: 0, 9: 0},
                               7: {1: 4, 2: 3, 3: 3, 4: 1, 5: 0, 6: 0, 7: 0, 8: 0, 9: 0},
                               8: {1: 4, 2: 3, 3: 3, 4: 2, 5: 0, 6: 0, 7: 0, 8: 0, 9: 0},
                               9: {1: 4, 2: 3, 3: 3, 4: 3, 5: 1, 6: 0, 7: 0, 8: 0, 9: 0},
                               10: {1: 4, 2: 3, 3: 3, 4: 3, 5: 2, 6: 0, 7: 0, 8: 0, 9: 0},
                               11: {1: 4, 2: 3, 3: 3, 4: 3, 5: 2, 6: 1, 7: 0, 8: 0, 9: 0},
                               12: {1: 4, 2: 3, 3: 3, 4: 3, 5: 2, 6: 1, 7: 0, 8: 0, 9: 0},
                               13: {1: 4, 2: 3, 3: 3, 4: 3, 5: 2, 6: 1, 7: 1, 8: 0, 9: 0},
                               14: {1: 4, 2: 3, 3: 3, 4: 3, 5: 2, 6: 1, 7: 1, 8: 0, 9: 0},
                               15: {1: 4, 2: 3, 3: 3, 4: 3, 5: 2, 6: 1, 7: 1, 8: 1, 9: 0},
                               16: {1: 4, 2: 3, 3: 3, 4: 3, 5: 2, 6: 1, 7: 1, 8: 1, 9: 0},
                               17: {1: 4, 2: 3, 3: 3, 4: 3, 5: 2, 6: 1, 7: 1, 8: 1, 9: 1},
                               18: {1: 4, 2: 3, 3: 3, 4: 3, 5: 3, 6: 1, 7: 1, 8: 1, 9: 1},
                               19: {1: 4, 2: 3, 3: 3, 4: 3, 5: 3, 6: 2, 7: 1, 8: 1, 9: 1},
                               20: {1: 4, 2: 3, 3: 3, 4: 3, 5: 3, 6: 2, 7: 2, 8: 1, 9: 1}}
    def __init__(self):
        self.combatants = {}
        self.round = 1
        self.encounter_name = ""

    def add_combatant(self, combatant: Combatant):
        if not isinstance(combatant, Combatant):
            raise TypeError("Must add a Combatant")

        # Normalize combatant name by stripping leading/trailing whitespaces, casefolding and then making first letter of each word capital
        name = combatant.name.strip().casefold().title()

        #Ensuring that the name is not an empty string
        if not name:
            raise ValueError("Combatant name must contain a base name")

        # We separate a name into its base, separator and possible suffix, by partitioning from the right
        base, sep, tail = name.rpartition(" ")

        #Then we make the "base" of the name the "base name", if the tail is a digit. Else, the base name is just the whole name
        base_name = base if sep and tail.isdigit() else name

        # Initialize a set and a list to store used numbers and unnumbered combatants
        used_numbers = set()
        unnumbered = []

        # We run over the combatants in the tracker, and check if
        for c in self.combatants:
            cname = self.combatants[c].name.rstrip()
            b, s, t = cname.rpartition(" ")
            if s and t.isdigit() and b == base_name:
                used_numbers.add(int(t))
            elif cname == base_name:
                unnumbered.append(c)

        # Renumber unnumbered combatants if needed
        # first we check if there are any unnumbered combatants added (which will only be there case, if there was one matching the added combatant).
        # Then we check if there are any used numbers, meaning
        if unnumbered or used_numbers:
            next_number = 1
            for c in unnumbered:
                while next_number in used_numbers:
                    next_number += 1
                self.combatants[c].name = f"{base_name} {next_number}"
                used_numbers.add(next_number)
                next_number += 1

            # Assign number to new combatant
            next_number = 1
            while next_number in used_numbers:
                next_number += 1
            combatant.name = f"{base_name} {next_number}"
        else:
            # No conflict: keep name as-is
            combatant.name = base_name

        self.combatants[combatant.id] = combatant



    def sort_by_initiative(self):
        self.combatants.sort(key=lambda c: (-c.initiative, c.name)) #This sorts by initiative first (the minus is to ensure descending, and then name

    def get_turn_order(self):
        return [c.name for c in self.combatants]


    #Since having moved to storing the combatants as a dictionary, with cid as keys, the following method could probably be replaced
    def get_combatant_by_id(self,cid):
        return self.combatants[cid]

    def remove_combatant_by_id(self, cid):
        return self.combatants.pop(cid, None) is not None




    #The * forces the following arguments to be keyword only
    def add_caster_level(self,comb_id: uuid.UUID,*,caster_level: int=0):
        if not isinstance(caster_level,int):
            raise TypeError("Caster Level must be an integer.")
        if not 0 <= caster_level <= 20:
            raise ValueError("Caster level must be between 0 and 20")
        self.combatants[comb_id].caster_level = caster_level
        self.combatants[comb_id].compute_spell_slots(self.full_caster_progression)

    def regain_spell_slot(self,comb_id: uuid.UUID,level: int):
        combatant = self.combatants[comb_id]
        if combatant.spell_slot_dict[level] < self.full_caster_progression[combatant.caster_level][level]:
            combatant.spell_slot_dict[level] += 1

    def use_spell_slot(self,comb_id: uuid.UUID,level: int):
        combatant = self.combatants[comb_id]
        if combatant.spell_slot_dict[level] >0:
            combatant.spell_slot_dict[level] -= 1

    def add_ability(self,comb_id: uuid.UUID,ability_name: str, maximum_uses: int):
        self.combatants[comb_id].ability_dict[ability_name] = Ability(left=maximum_uses,max=maximum_uses)

    def regain_ability(self,comb_id: uuid.UUID,ability_name:str):
        combatant = self.combatants[comb_id]
        if combatant.ability_dict[ability_name].left < combatant.ability_dict[ability_name].max:
                combatant.ability_dict[ability_name].left += 1

    def use_ability(self,comb_id: uuid.UUID,ability_name:str):
        combatant = self.combatants[comb_id]
        if combatant.ability_dict[ability_name].left >0:
                combatant.ability_dict[ability_name].left -= 1

    def make_encounter_data(self):
        combatants_data = []
        for combatant in self.combatants.values():
            data = asdict(combatant)
            data["id"] = str(combatant.id)
            combatants_data.append(data)
        return combatants_data

    def save_encounter(self,filename,encounter_name = None):
        data = {
            "version": 1,
            "encounter_name": self.encounter_name,
            "round": self.round,
            "combatants": []
        }
        if encounter_name:
            data["encounter_name"] = encounter_name
        data["combatants"] = self.make_encounter_data()
        output_folder = "encounters"
        make_output(output_folder)
        output_path = create_output_path(output_folder,filename)
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4)


    def load_encounter(self,filename):
        with open(filename, "r", encoding="utf-8") as f:
            loaded_data = json.load(f)
        #First, we clear the tracker
        self.combatants.clear()
        self.round = 1
        self.encounter_name = ""

        #This variable is currently not used, but is intended for version control
        version = loaded_data.get("version", 1)

        self.encounter_name = loaded_data["encounter_name"]
        self.round = loaded_data["round"]

        for comb in loaded_data["combatants"]:
            # Restore UUID object
            comb["id"] = uuid.UUID(comb["id"])

            comb["spell_slot_dict"] = {
                int(level): remain for level, remain in comb["spell_slot_dict"].items()
            }

            comb["ability_dict"] = {
                name: Ability(**data)
                for name, data in comb["ability_dict"].items()
            }

            combatant = Combatant(**comb)
            self.combatants[combatant.id] = combatant
        # for comb in loaded_data["combatants"]:
        #     combatant = Combatant(comb["name"], comb["initiative"], comb["ac"], comb["hp_total"])
        #     combatant.damage_taken = comb["damage_taken"]
        #     combatant.id = uuid.UUID(comb["id"])
        #     combatant.caster_level = comb["caster_level"]
        #     if comb["spell_slots"]:
        #         for key in comb["spell_slots"]:
        #             combatant.spell_slot_dict[int(key)] = comb["spell_slots"][key]
        #
        #     for name, ability_data in comb["ability_dict"].items():
        #         combatant.ability_dict[name] = Ability(left=ability_data["left"], max=ability_data["max"])
        #
        #     if comb["abilities"]:
        #         for ability_name in comb["abilities"]:
        #             combatant.ability_dict[ability_name] = Ability(left=comb[ability_name][0], max=comb[ability_name][1])
        #     self.add_combatant(combatant)

# Methods past this line are in a holding pattern. They aren't used yet and are up for deletion
# ----------------------------------------------------------------------------------------------

    def change_combatant_name(self, oldname: str, newname: str):
        for combatant in self.combatants:
            if combatant.name == oldname:
                combatant.name = newname
                return True
        return False

    def change_combatant_initiative(self,name: str, amount: int):
        for combatant in self.combatants:
            if combatant.name == name:
                combatant.initiative = amount
                return True
        return False

    def change_combatant_ac(self,name: str, amount: int):
        for combatant in self.combatants:
            if combatant.name == name:
                combatant.ac = amount
                return True
        return False

    def change_combatant_damage(self,name: str, amount: int):
        for combatant in self.combatants:
            if combatant.name == name:
                combatant.change_damage(amount)
                return True
        return False

    def change_combatant_hp(self,name: str, amount: int):
        for combatant in self.combatants:
            if combatant.name == name:
                combatant.hp_total = amount
                return True
        return False

    def remove_combatant(self, name: str):
        for combatant in self.combatants:
            if combatant.name == name:
                self.combatants.remove(combatant)
                return True
        return False

    #The following two methods can be removed as they are old and unused
    def damage_combatant(self,name: str,amount: int):
        for combatant in self.combatants:
            if combatant.name == name:
                    combatant.change_damage(amount)
                    return True
        return False

    def heal_combatant(self,name: str,amount: int):
        for combatant in self.combatants:
            if combatant.name == name:
                    combatant.heal(amount)
                    return True
        return False

