

from PySide6.QtWidgets import QDialog, QVBoxLayout, QLineEdit, QSpinBox, QLabel, QDialogButtonBox


class SpellDialog(QDialog):
    def __init__(self,parent=None):
        super().__init__(parent)

        # Set the title
        self.setWindowTitle("Choose Caster Level")

        self.caster_level_input = QSpinBox()
        self.caster_level_input.setRange(0, 20)

        # Set the layout of the box
        dlg_layout = QVBoxLayout(self)

        dlg_layout.addWidget(QLabel("Caster Level"))
        dlg_layout.addWidget(self.caster_level_input)

        # Adds an okay and cancel button
        # The left input will respond to button.accepted, and the right to button.rejected
        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        dlg_layout.addWidget(buttons)

        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)

    def get_data(self):
        return self.caster_level_input.value()



    # def open_spell_slots_dialogue(self, clicked_row):
    #     # Open dialog to add ability
    #     # First we create a dialogue box
    #     dialog = QDialog(self)
    #     # Set the title
    #     dialog.setWindowTitle("Choose Caster Level")
    #     # Set the layout of the box
    #     dlg_layout = QVBoxLayout(dialog)
    #
    #     caster_level_input = QSpinBox()
    #     caster_level_input.setRange(0, 20)
    #
    #     dlg_layout.addWidget(QLabel("Caster Level"))
    #     dlg_layout.addWidget(caster_level_input)
    #
    #     # Adds an okay and cancel button
    #     # The left input will respond to button.accepted, and the right to button.rejected
    #     buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
    #     dlg_layout.addWidget(buttons)
    #
    #     def on_accept():
    #         # First we ensure there is actually a spell slot column
    #         self.ensure_spell_slots_column()
    #
    #         # Then we update the combatant based on the input
    #         level = caster_level_input.value()
    #         combatant_id = self.fetch_combatant_id(clicked_row)
    #         self.comb_manager.add_caster_level(combatant_id, caster_level=level)
    #
    #         # Then we render the spell slots based on the combat manager
    #         combatant = self.comb_manager.get_combatant_by_id(combatant_id)
    #         spell_slots = self.spell_slots_to_list(combatant.spell_slot_dict)
    #         col = self.col_index["Spell Slots"]
    #         self.set_ability_widget(clicked_row, col, combatant_id, spell_slots, True)
    #         # Closes the dialogue and returns a successful result
    #         dialog.accept()
    #
    #     buttons.accepted.connect(on_accept)
    #     buttons.rejected.connect(dialog.reject)
    #
    #     dialog.exec()