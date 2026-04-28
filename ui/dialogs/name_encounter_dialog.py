from PySide6.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QLineEdit, QSpinBox, QLabel, QDialogButtonBox
from ui.styling.dialog_buttons_style import dialog_button_style
import copy

class NameEncounterDialog(QDialog):
    def __init__(self,parent=None,current_name=None):
        super().__init__(parent)
        self.current_name = current_name

        # Set the title
        self.setWindowTitle("Give Encounter Name")


        # Set the layout of the box
        dlg_layout = QVBoxLayout(self)

        name_layout = QHBoxLayout(self)
        self.name_input = QLineEdit()
        self.name_input.setMinimumWidth(300)
        if current_name:
            self.name_input.setText(current_name)
        else:
            self.name_input.setPlaceholderText("Encounter Name")

        name_layout.addWidget(QLabel("Encounter Title:"))
        name_layout.addWidget(self.name_input)

        dlg_layout.addLayout(name_layout)

        # Adds an okay and cancel button
        # The left input will respond to button.accepted, and the right to button.rejected
        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.setStyleSheet(dialog_button_style)

        dlg_layout.addWidget(buttons)


        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)

    def get_data(self):
        return copy.deepcopy(self.name_input.text())