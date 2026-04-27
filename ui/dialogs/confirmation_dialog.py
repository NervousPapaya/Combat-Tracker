from PySide6.QtWidgets import QDialog, QVBoxLayout, QLabel, QDialogButtonBox
from ui.styling.dialog_buttons_style import dialog_button_style

class ConfirmationDialog(QDialog):
    def __init__(self,parent=None,warning_text = None):
        super().__init__(parent)
        self.warning_text = warning_text

        # Set the title
        self.setWindowTitle("Edit Conditions")


        dlg_layout = QVBoxLayout(self)


        dlg_layout.addWidget(QLabel(self.warning_text))
        dlg_layout.addWidget(QLabel("Are you sure?"))

        dlg_layout.addSpacing(10)
        # OK / Cancel
        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.setStyleSheet(dialog_button_style)
        dlg_layout.addWidget(buttons)

        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
