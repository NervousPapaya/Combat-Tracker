from PySide6.QtWidgets import QDialog, QVBoxLayout, QLineEdit, QSpinBox, QLabel, QDialogButtonBox, QPushButton, QListWidget, QMessageBox
from ui.styling.dialog_buttons_style import dialog_button_style
from models.combatant import Ability
import copy

class AbilityDialog(QDialog):
    def __init__(self,abilities: list,parent=None):
        super().__init__(parent)
        self.abilities = abilities

        # Set the title
        self.setWindowTitle("Edit Abilities")

        # Set the layout of the box
        dlg_layout = QVBoxLayout(self)

        #A list view intended to show the current conditions
        self.list_widget = QListWidget()
        dlg_layout.addWidget(self.list_widget)

        self.refresh_list()

        #Input for the name of the ability
        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("Ability")
        dlg_layout.addWidget(QLabel("Ability Name"))
        dlg_layout.addWidget(self.name_input)

        #Input for the maximum uses
        self.maximum_uses_input = QSpinBox()
        self.maximum_uses_input.setRange(1, 10)
        dlg_layout.addWidget(QLabel("Maximum Uses"))
        dlg_layout.addWidget(self.maximum_uses_input)

        # ADD BUTTON
        add_btn = QPushButton("Add Ability")
        add_btn.clicked.connect(self.add_ability)
        dlg_layout.addWidget(add_btn)

        #REMOVE BUTTON
        remove_btn = QPushButton("Remove Ability")
        remove_btn.clicked.connect(self.remove_ability)
        dlg_layout.addWidget(remove_btn)


        # Adds an okay and cancel button
        # The left input will respond to button.accepted, and the right to button.rejected
        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.setStyleSheet(dialog_button_style)

        dlg_layout.addWidget(buttons)


        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)

    def refresh_list(self):
        self.list_widget.clear()

        for a in self.abilities:
            self.list_widget.addItem(f"name: {a.name} - max uses: {a.max}")


    def add_ability(self):
        name = self.name_input.text().strip()
        maximum_uses = self.maximum_uses_input.value()
        if not name:
            return

        if any(a.name == name for a in self.abilities):
            QMessageBox.warning(self, "Duplicate Ability", f"An ability named '{name}' already exists.")
            return

        ability = Ability(name=name,left=maximum_uses,max=maximum_uses)
        self.abilities.append(ability)
        self.abilities.sort(key = lambda a: a.name)

        self.refresh_list()

        #Resetting input
        self.name_input.clear()
        self.maximum_uses_input.setValue(1)

    def remove_ability(self):
        selected = self.list_widget.currentRow()
        if selected < 0:
            return

        self.abilities.pop(selected)
        self.refresh_list()

    def get_data(self):
        return copy.deepcopy(self.abilities)



# def open_abilities_dialogue(self, clicked_row):
#     # Open dialog to add ability
#     # First we create a dialogue box
#     dialog = QDialog(self)
#     # Set the title
#     dialog.setWindowTitle("Define Ability")
#     # Set the layout of the box
#     dlg_layout = QVBoxLayout(dialog)
#
#     ability_name_input = QLineEdit()
#     ability_name_input.setPlaceholderText("Ability")
#     dlg_layout.addWidget(QLabel("Ability Name"))
#     dlg_layout.addWidget(ability_name_input)
#
#     maximum_uses_input = QSpinBox()
#     maximum_uses_input.setRange(1, 10)
#
#     dlg_layout.addWidget(QLabel("Maximum Uses"))
#     dlg_layout.addWidget(maximum_uses_input)
#
#     # Adds an okay and cancel button
#     # The left input will respond to button.accepted, and the right to button.rejected
#     buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
#     dlg_layout.addWidget(buttons)
#
#     def on_accept():
#         # First we ensure there is actually a spell slot column
#         self.ensure_abilities_column()
#
#         combatant_id = self.fetch_combatant_id(clicked_row)
#         # Then we update the combatant based on the input
#         ability_name = ability_name_input.text()
#         maximum_uses = maximum_uses_input.value()
#         self.comb_manager.add_ability(combatant_id, ability_name, maximum_uses)
#
#         # Now we render the abilities based on the data in the combat manager
#         combatant = self.comb_manager.get_combatant_by_id(combatant_id)
#         abilities = sorted(self.abilities_to_list(combatant.ability_dict))
#
#         col = self.col_index["Abilities"]
#         self.set_ability_widget(clicked_row, col, combatant_id, abilities)
#         # Closes the dialogue and returns a successful result
#         dialog.accept()
#
#     buttons.accepted.connect(on_accept)
#     buttons.rejected.connect(dialog.reject)
#
#     dialog.exec()