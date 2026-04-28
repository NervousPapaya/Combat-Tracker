from PySide6.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QLabel, QDialogButtonBox, QSpinBox
from ui.styling.dialog_buttons_style import dialog_button_style
import copy

class DuplicateDialog(QDialog):
    def __init__(self,parent=None):
        super().__init__(parent)

        # Set the title
        self.setWindowTitle("Duplicate Combatant")


        dlg_layout = QVBoxLayout(self)

        input_layout = QHBoxLayout(self)

        self.copies_input = QSpinBox()
        self.copies_input.setRange(1, 50)

        input_layout.addWidget(QLabel("Number of duplicates (max 50):"))
        input_layout.addWidget(self.copies_input)

        dlg_layout.addLayout(input_layout)
        dlg_layout.addSpacing(10)
        # OK / Cancel
        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.setStyleSheet(dialog_button_style)
        dlg_layout.addWidget(buttons)

        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)

    def get_data(self):
        return copy.deepcopy(self.copies_input.value())