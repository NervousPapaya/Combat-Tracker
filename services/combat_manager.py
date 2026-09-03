import copy
import uuid
import os
from uuid import UUID

from models.combatant import Combatant, Ability
import json
from filehandling.filehandling import make_output, create_output_path
from dataclasses import asdict


class CombatManager:
    @property
    def turn_order(self):
        """This property stores the turn order.
        It is a list of the combatant ids sorted in descending by initiative."""
        return [c.id for c in sorted(self.combatants.values(), key=lambda c: (-c.initiative, c.name))]

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
        self.encounter_title = "Untitled Encounter"

    def set_encounter_title(self, title:str):
        self.encounter_title = title

    def create_and_add_combatant(self,name,initiative,ac,hp):
        combatant = Combatant(name, initiative, ac, hp)
        self.add_combatant(combatant)
        return combatant.id

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

    def duplicate_combatant(self,cid):
        original = self.get_combatant_by_id(cid)
        #setting up a duplicate
        duplicate = copy.deepcopy(original)
        duplicate.id = uuid.uuid4()

        # adds the duplicate to the combat manager
        self.add_combatant(duplicate)

        return duplicate.id

    def duplicate_combatant_n_times(self,cid: uuid.UUID,num_copies:int):
        duplicate_cid_list = []
        for i in range(0,num_copies):
            duplicate_id = self.duplicate_combatant(cid)
            duplicate_cid_list.append(duplicate_id)
        return duplicate_cid_list

    #Since having moved to storing the combatants as a dictionary, with cid as keys, the following method could probably be replaced
    def get_combatant_by_id(self,cid):
        return self.combatants[cid]

    def remove_combatant_by_id(self, cid):
        return self.combatants.pop(cid)

    def remove_combatants_by_id_list(self,cid_list:list):
        for cid in cid_list:
            self.remove_combatant_by_id(cid)

    def update_combatant_by_id(self,cid,combatant):
        self.combatants[cid] = combatant

    def set_combatant_name(self,cid,name):
        combatant = self.get_combatant_by_id(cid)
        combatant.name = name

    def get_combatant_name(self,cid):
        combatant = self.get_combatant_by_id(cid)
        return combatant.name

    def set_combatant_initiative(self,cid,initiative):
        combatant = self.get_combatant_by_id(cid)
        combatant.initiative = initiative

    def get_combatant_initiative(self,cid):
        combatant = self.get_combatant_by_id(cid)
        return combatant.initiative

    def set_combatant_ac(self,cid,ac):
        combatant = self.get_combatant_by_id(cid)
        combatant.ac = ac

    def get_combatant_ac(self,cid):
        combatant = self.get_combatant_by_id(cid)
        return combatant.ac

    def set_combatant_hp_tot(self,cid,hp):
        combatant = self.get_combatant_by_id(cid)
        combatant.hp_total = hp

    def get_combatant_hp_tot(self,cid):
        combatant = self.get_combatant_by_id(cid)
        return combatant.hp_total

    def set_combatant_damage(self,cid,dmg: int):
        combatant = self.get_combatant_by_id(cid)
        combatant.damage_taken = dmg

    def get_combatant_damage(self,cid):
        combatant = self.get_combatant_by_id(cid)
        return combatant.damage_taken

    def set_combatant_damage_expr(self,cid,expr: str):
        combatant = self.get_combatant_by_id(cid)
        combatant.damage_expr = expr

    def get_combatant_damage_expr(self,cid):
        combatant = self.get_combatant_by_id(cid)
        return combatant.damage_expr

    def set_combatant_status(self,cid,status):
        combatant = self.get_combatant_by_id(cid)
        combatant.status = status

    def get_combatant_status(self,cid):
        combatant = self.get_combatant_by_id(cid)
        return combatant.status


    #The * forces the succeeding arguments to be keyword only
    def set_caster_level(self,comb_id: uuid.UUID,*,caster_level: int=0):
        if not isinstance(caster_level,int):
            raise TypeError("Caster Level must be an integer.")
        if not 0 <= caster_level <= 20:
            raise ValueError("Caster level must be between 0 and 20")
        self.combatants[comb_id].caster_level = caster_level
        self.combatants[comb_id].compute_spell_slots(self.full_caster_progression)

    def get_combatant_caster_level(self,cid: uuid.UUID):
        combatant = self.get_combatant_by_id(cid)
        return combatant.caster_level

    def regain_spell_slot(self,comb_id: uuid.UUID,level: int):
        combatant = self.combatants[comb_id]
        if combatant.spell_slot_dict[level] < self.full_caster_progression[combatant.caster_level][level]:
            combatant.spell_slot_dict[level] += 1

    def use_spell_slot(self,comb_id: uuid.UUID,level: int):
        combatant = self.combatants[comb_id]
        if combatant.spell_slot_dict[level] >0:
            combatant.spell_slot_dict[level] -= 1


    def set_combatant_abilities(self,cid: uuid.UUID,ab_list:list):
        combatant = self.get_combatant_by_id(cid)
        combatant.ability_list = ab_list

    def get_combatant_abilities(self,cid: uuid.UUID):
        combatant = self.get_combatant_by_id(cid)
        return combatant.ability_list

    def remove_ability(self, cid, ability_name):
        combatant = self.get_combatant_by_id(cid)
        combatant.ability_list = [a for a in combatant.ability_list if a.name != ability_name]
        #del combatant.ability_dict[ability_name]

    def regain_ability(self,comb_id: uuid.UUID,ability_name:str):
        combatant = self.combatants[comb_id]
        ability = combatant.get_ability(ability_name)
        if ability.left < ability.max:
            ability.left +=1

    def use_ability(self,comb_id: uuid.UUID,ability_name:str):
        combatant = self.combatants[comb_id]
        ability = combatant.get_ability(ability_name)
        if ability.left >0:
            ability.left -= 1


    def set_combatant_conditions(self,comb_id: uuid.UUID, conditions: list):
        combatant = self.get_combatant_by_id(comb_id)
        combatant.conditions = conditions

    def get_combatant_conditions(self,comb_id: uuid.UUID):
        combatant = self.get_combatant_by_id(comb_id)
        return combatant.conditions

    def toggle_combatant_permanent(self,comb_id:uuid.UUID):
        combatant = self.get_combatant_by_id(comb_id)
        combatant.permanent = not combatant.permanent

    def advance_round(self):
        self.round +=1
        for comb in self.combatants.values():
            new_conditions = []
            for c in comb.conditions:
                updated_cond = c.advance_condition()
                if updated_cond.indefinite or updated_cond.rounds_left > 0:
                    new_conditions.append(updated_cond)
            comb.conditions = new_conditions

    def regress_round(self):
        self.round -= 1

    def reset_round(self):
        self.round = 1

    def set_round(self,round):
        self.round = round

    def restore_state(self, round_value, combatants):
        self.round = round_value
        self.combatants = combatants

    def restore_encounter(self,round_value,combatants,title):
        self.round = round_value
        self.combatants = combatants
        self.encounter_title = title

    def clear_encounter(self):
        self.combatants = {
            cid: c for cid, c in self.combatants.items() if c.permanent
        }
        self.round = 1
        self.encounter_title = "Untitled Encounter"

    def clear_encounter_completely(self):
        self.combatants = {}
        self.round = 1
        self.encounter_title = "Untitled Encounter"


    def make_encounter_data(self):
        combatants_data = []
        for combatant in self.combatants.values():
            data = asdict(combatant)
            data["id"] = str(combatant.id)
            combatants_data.append(data)
        return combatants_data





    def save_encounter(self,filename,encounter_title = None):
        data = {
            "version": 1,
            "encounter_title": self.encounter_title,
            "round": self.round,
            "combatants": []
        }
        if encounter_title:
            data["encounter_title"] = encounter_title
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
        self.encounter_title = ""

        #This variable is currently not used, but is intended for version control
        version = loaded_data.get("version", 1)

        self.encounter_title = loaded_data["encounter_title"]
        self.round = loaded_data["round"]

        for comb in loaded_data["combatants"]:
            # Restore UUID object
            comb["id"] = uuid.UUID(comb["id"])

            comb["spell_slot_dict"] = {
                int(level): remain for level, remain in comb["spell_slot_dict"].items()
            }

            comb["ability_dict"] = {
                name: Ability(name=name, **{k: v for k, v in data.items() if k != "name"})
                for name, data in comb["ability_dict"].items()
            }

            combatant = Combatant(**comb)
            self.combatants[combatant.id] = combatant


# Methods past this line are in a holding pattern. They aren't used and are up for deletion
# ----------------------------------------------------------------------------------------------

    def add_ability(self,comb_id: uuid.UUID,ability_name: str, maximum_uses: int):
        self.combatants[comb_id].ability_dict[ability_name] = Ability(name=ability_name,left=maximum_uses,max=maximum_uses)



    def sort_by_initiative(self):
        self.combatants.sort(key=lambda c: (-c.initiative, c.name)) #This sorts by initiative first (the minus is to ensure descending, and then name

    def get_turn_order(self):
        return [c.name for c in self.combatants]