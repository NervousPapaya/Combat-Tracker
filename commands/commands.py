from commands.base import Command
import copy


#This first block of commands deals with modifying combatants in one way or another

class SetNameCommand(Command):
    def __init__(self, manager, cid, new_name):
        self.manager = manager
        self.cid = cid
        self.new_name = new_name
        self.old_name = None

    def execute(self):
        self.old_name = self.manager.get_combatant_name(self.cid)
        self.manager.set_combatant_name(self.cid,self.new_name)

    def undo(self):
        self.manager.set_combatant_name(self.cid,self.old_name)

class SetInitiativeCommand(Command):
    def __init__(self, manager, cid, new_initiative):
        self.manager = manager
        self.cid = cid
        self.new_initiative = new_initiative
        self.old_initiative = None

    def execute(self):
        self.old_initiative = self.manager.get_combatant_initiative(self.cid)
        self.manager.set_combatant_initiative(self.cid,self.new_initiative)

    def undo(self):
        self.manager.set_combatant_initiative(self.cid,self.old_initiative)

class SetACCommand(Command):
    def __init__(self, manager, cid, new_ac):
        self.manager = manager
        self.cid = cid
        self.new_ac = new_ac
        self.old_ac = None

    def execute(self):
        self.old_ac = self.manager.get_combatant_ac(self.cid)
        self.manager.set_combatant_ac(self.cid,self.new_ac)

    def undo(self):
        self.manager.set_combatant_ac(self.cid,self.old_ac)

class SetHPTotCommand(Command):
    def __init__(self, manager, cid, new_hp):
        self.manager = manager
        self.cid = cid
        self.new_hp = new_hp
        self.old_hp = None

    def execute(self):
        self.old_hp = self.manager.get_combatant_hp_tot(self.cid)
        self.manager.set_combatant_hp_tot(self.cid,self.new_hp)

    def undo(self):
        self.manager.set_combatant_hp_tot(self.cid,self.old_hp)


class SetDamageCommand(Command):
    def __init__(self, manager, cid, new_dmg, new_dmg_expr):
        self.manager = manager
        self.cid = cid
        self.new_dmg = new_dmg
        self.old_dmg = None
        self.new_dmg_expr = new_dmg_expr
        self.old_dmg_expr = None

    def execute(self):
        self.old_dmg = self.manager.get_combatant_damage(self.cid)
        self.old_dmg_expr = self.manager.get_combatant_damage_expr(self.cid)
        self.manager.set_combatant_damage(self.cid,self.new_dmg)
        self.manager.set_combatant_damage_expr(self.cid, self.new_dmg_expr)

    def undo(self):
        self.manager.set_combatant_damage(self.cid,self.old_dmg)
        self.manager.set_combatant_damage_expr(self.cid, self.old_dmg_expr)

class SetStatusCommand(Command):
    def __init__(self, manager, cid, new_status):
        self.manager = manager
        self.cid = cid
        self.new_status = new_status
        self.old_status = None

    def execute(self):
        self.old_status = self.manager.get_combatant_status(self.cid)
        self.manager.set_combatant_status(self.cid,self.new_status)

    def undo(self):
        self.manager.set_combatant_status(self.cid,self.old_status)

class SetSpellSlotsCommand(Command):
    def __init__(self, manager, cid, new_caster_level):
        self.manager = manager
        self.cid = cid
        self.new_caster_level = new_caster_level
        self.old_caster_level = None

    def execute(self):
        self.old_caster_level = self.manager.get_combatant_caster_level(self.cid)
        self.manager.set_caster_level(self.cid,caster_level=self.new_caster_level)

    def undo(self):
        self.manager.set_caster_level(self.cid,caster_level=self.old_caster_level)

class SetAbilitiesCommand(Command):
    def __init__(self, manager, cid, new_ability_name, new_ability_uses):
        self.manager = manager
        self.cid = cid
        self.new_ability_name = new_ability_name
        self.new_ability_uses = new_ability_uses

    def execute(self):
        self.manager.add_ability(self.cid,ability_name=self.new_ability_name,maximum_uses=self.new_ability_uses)

    def undo(self):
        self.manager.remove_ability(self.cid,ability_name=self.new_ability_name)

class SetConditionsCommand(Command):
    def __init__(self, manager, cid, new_conditions):
        self.manager = manager
        self.cid = cid
        self.new_conditions = new_conditions
        self.old_conditions = None

    def execute(self):
        self.old_conditions = self.manager.get_combatant_conditions(self.cid)
        self.manager.set_combatant_conditions(self.cid,self.new_conditions)

    def undo(self):
        self.manager.set_combatant_conditions(self.cid,self.old_conditions)

class SetPermanentCommand(Command):
    def __init__(self, manager, cid):
        self.manager = manager
        self.cid = cid


    def execute(self):
        self.manager.toggle_combatant_permanent(self.cid)

    def undo(self):
        self.manager.toggle_combatant_permanent(self.cid)



class AdvanceRoundCommand(Command):
    def __init__(self, manager):
        self.manager = manager
        self.old_round = None
        self.old_combatants = None

    def execute(self):
        self.old_round = self.manager.round
        self.old_combatants = copy.deepcopy(self.manager.combatants)
        self.manager.advance_round()

    def undo(self):
        self.manager.restore_state(self.old_round,self.old_combatants)

class ResetRoundCommand(Command):
    def __init__(self, manager):
        self.manager = manager
        self.old_round = None

    def execute(self):
        self.old_round = self.manager.round
        self.manager.reset_round()

    def undo(self):
        self.manager.set_round(self.old_round)

class ClearTrackerCommand(Command):
    def __init__(self, manager):
        self.manager = manager
        self.old_combatants = None
        self.old_round = None
        self.old_title = None

    def execute(self):
        self.old_round = self.manager.round
        self.old_combatants = copy.deepcopy(self.manager.combatants)
        self.old_title = self.manager.encounter_title
        self.manager.clear_encounter()

    def undo(self):
        self.manager.restore_encounter(self.old_round,self.old_combatants,self.old_title)

class ClearTrackerCompletelyCommand(Command):
    def __init__(self, manager):
        self.manager = manager
        self.old_combatants = None
        self.old_round = None
        self.old_title = None

    def execute(self):
        self.old_round = self.manager.round
        self.old_combatants = copy.deepcopy(self.manager.combatants)
        self.old_title = self.manager.encounter_title
        self.manager.clear_encounter_completely()

    def undo(self):
        self.manager.restore_encounter(self.old_round,self.old_combatants,self.old_title)

class SetEncounterTitleCommand(Command):
    def __init__(self, manager, title):
        self.manager = manager
        self.new_title = title
        self.old_title = None

    def execute(self):
        self.old_title = self.manager.encounter_title
        self.manager.set_encounter_title(self.new_title)

    def undo(self):
        self.manager.set_encounter_title(self.old_title)

