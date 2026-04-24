from dataclasses import dataclass, field
import uuid

@dataclass
class Ability:
    left: int
    max: int

@dataclass(frozen=True)
class Condition:
    name: str
    rounds_left: int
    indefinite: bool = False

    def advance_condition(self) -> Condition:
        if self.indefinite:
            return self

        return Condition(
            name=self.name,
            rounds_left=self.rounds_left - 1,
            indefinite=False
        )

    def regress_condition(self) -> Condition:
        if self.indefinite:
            return self

        return Condition(
            name=self.name,
            rounds_left=self.rounds_left + 1,
            indefinite=False
        )

@dataclass
class Combatant:
    name: str
    initiative: float
    ac: int
    hp_total: int
    #Setting up an id to use for identification.
    # field and default_factory needs to be used, to ensure each instance has a distinct id.
    id: uuid.UUID = field(default_factory=uuid.uuid4)

    damage_taken: int = 0
    damage_expr: str = "0"
    conditions: list = field(default_factory = list)
    status: str = ""
    caster_level: int = 0
    #We set up a dictionary to store spell slots if necessary.
    #As before field and default_factory must be used
    spell_slot_dict: dict = field(default_factory = lambda: {i: 0 for i in range(1,10)})

    #We set up a dictionary to store ability slots if necessary.
    #As before field and default_factory must be used
    ability_dict: dict = field(default_factory = dict)

    def __post_init__(self):
        if not 0 <= self.caster_level <= 20:
            raise ValueError("Caster_level must be between 0 and 20")

    def change_damage(self, amount: int):
        self.damage_taken = max(self.damage_taken + amount,0)

    #@property ensures that the next method does not need () when called
    @property
    def hp_remaining(self):
        return self.hp_total - self.damage_taken

    def heal(self, amount):
        self.damage_taken = max(self.damage_taken - amount, 0)

    def __str__(self):
        return f"{self.name} | HP: {self.hp_remaining}/{self.hp_total} | AC: {self.ac} | Initiative: {self.initiative}"

    def compute_spell_slots(self,spell_slot_table):
        """This method simply computes the spell slots based off the caster level and edits the spell slot dict as necessary."""
        self.spell_slot_dict = spell_slot_table[self.caster_level].copy()

