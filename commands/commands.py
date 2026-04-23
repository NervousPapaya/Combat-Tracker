from commands.base import Command

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
    def __init__(self, manager, cid, new_dmg):
        self.manager = manager
        self.cid = cid
        self.new_dmg = new_dmg
        self.old_dmg = None

    def execute(self):
        self.old_dmg = self.manager.get_combatant_damage(self.cid)
        self.manager.set_combatant_damage(self.cid,self.new_dmg)

    def undo(self):
        self.manager.set_combatant_damage(self.cid,self.old_dmg)

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
