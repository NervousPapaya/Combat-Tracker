from PySide6.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QLineEdit, QSpinBox, QLabel, QDialogButtonBox, QListWidget, QPushButton, QCheckBox
from models.combatant import Condition
from ui.styling.dialog_buttons_style import dialog_button_style
import copy

class ConditionsDialog(QDialog):
    def __init__(self,conditions, parent=None):
        super().__init__(parent)
        self.conditions = conditions

        # Set the title
        self.setWindowTitle("Edit Conditions")

        dlg_layout = QVBoxLayout(self)

        #A list view intended to show the current conditions
        self.list_widget = QListWidget()
        dlg_layout.addWidget(self.list_widget)

        self.refresh_list()

        #Setting up the inputs
        name_layout = QHBoxLayout(self)

        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("Condition")

        name_layout.addWidget(QLabel("Condition:"))
        name_layout.addWidget(self.name_input)

        duration_layout = QHBoxLayout(self)

        self.duration_input = QSpinBox()
        self.duration_input.setRange(1,99)

        duration_layout.addWidget(QLabel("Duration (rounds):"))
        duration_layout.addWidget(self.duration_input)

        #Setting up a checkbox for handling indefinite conditions
        indefinite_layout = QHBoxLayout(self)
        self.indefinite_checkbox = QCheckBox()
        #When toggled, the checkbox connects to the helper method on_indefinite_toggled
        self.indefinite_checkbox.stateChanged.connect(self.on_indefinite_toggled)
        indefinite_layout.addWidget(QLabel("Indefinite?"))
        indefinite_layout.addWidget(self.indefinite_checkbox)
        #This is for resetting the style of the checkbox, so that it ignores the changes made
        self.indefinite_checkbox.setProperty("checkbox_type", "dialogue")

        dlg_layout.addLayout(name_layout)
        dlg_layout.addLayout(duration_layout)
        dlg_layout.addLayout(indefinite_layout)

        # ADD BUTTON
        add_btn = QPushButton("Add Condition")
        add_btn.clicked.connect(self.add_condition)
        dlg_layout.addWidget(add_btn)

        # REMOVE BUTTON
        remove_btn = QPushButton("Remove Selected")
        remove_btn.clicked.connect(self.remove_selected)
        dlg_layout.addWidget(remove_btn)

        dlg_layout.addSpacing(10)
        # OK / Cancel
        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.setStyleSheet(dialog_button_style)
        dlg_layout.addWidget(buttons)

        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)


    def refresh_list(self):
        self.list_widget.clear()

        for c in self.conditions:
            if c.indefinite:
                self.list_widget.addItem(c.name)
            else:
                self.list_widget.addItem(f"{c.name} ({c.rounds_left})")

    def add_condition(self):
        name = self.name_input.text().strip()
        if not name:
            return

        cond = Condition(name, self.duration_input.value(), indefinite=self.indefinite_checkbox.isChecked())
        self.conditions.append(cond)

        self.refresh_list()

        #Resetting input and checkbox
        self.name_input.clear()
        self.duration_input.setValue(1)
        self.indefinite_checkbox.setChecked(False)

    def remove_selected(self):
        selected = self.list_widget.currentRow()
        if selected < 0:
            return

        self.conditions.pop(selected)
        self.refresh_list()

    def get_data(self):
        return copy.deepcopy(self.conditions)

    def on_indefinite_toggled(self, state):
        #If the checbox is ticked, the duration inputs Enabled variable is set to false. I.e. the input is disabled.
        self.duration_input.setEnabled(not self.indefinite_checkbox.isChecked())