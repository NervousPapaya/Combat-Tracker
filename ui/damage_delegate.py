from PySide6.QtWidgets import QStyledItemDelegate, QLineEdit
from PySide6.QtCore import Qt
from services.maths import safe_eval
from commands.commands import SetDamageCommand

#This delegate handles the damage column
class DamageDelegate(QStyledItemDelegate):
    def __init__(self, parent, manager):
        super().__init__(parent)
        self.manager = manager
        self.parent = parent  # MainWindow

    #How editing works (just uses parent)
    def createEditor(self, parent, option, index):
        return QLineEdit(parent)

    #What happens when editing starts
    def setEditorData(self, editor, index):
        row = index.row()
        combatant_id = self.parent.fetch_combatant_id(row)
        combatant = self.manager.get_combatant_by_id(combatant_id)

        # Show expression when editing
        editor.setText(combatant.damage_expr)

    #What happens when editing is done
    def setModelData(self, editor, model, index):
        text = editor.text()
        row = index.row()

        combatant_id = self.parent.fetch_combatant_id(row)

        try:
            value = safe_eval(text)

            # Update via undo system
            self.parent.undo_manager.do(
                SetDamageCommand(
                    manager=self.manager,
                    cid=combatant_id,
                    new_dmg=value,
                    new_dmg_expr=text
                )
            )

            # IMPORTANT: set evaluated value in UI
            model.setData(index, str(value), Qt.EditRole)
            self.parent.update_row_color(row)

        except Exception:
            # rollback
            combatant = self.manager.get_combatant_by_id(combatant_id)
            model.setData(index, str(combatant.damage_taken), Qt.EditRole)