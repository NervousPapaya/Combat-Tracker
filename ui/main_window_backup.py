import sys
import copy
from services.combat_manager import CombatManager
from services.maths import safe_eval, is_whole_number
from services.undo_manager import UndoManager
from commands.commands import SetNameCommand, SetACCommand, SetDamageCommand, SetInitiativeCommand, SetHPTotCommand, \
    SetStatusCommand
from models.combatant import Combatant
from ui.abilitywidget import AbilityTrackerWidget
from PySide6.QtCore import Qt

from PySide6.QtWidgets import (QMainWindow, QApplication, QWidget, QTableWidget,
                               QTableWidgetItem, QVBoxLayout, QLineEdit, QPushButton, QHBoxLayout,
                               QSpinBox, QMenu, QLabel, QDialog, QDialogButtonBox, QMenuBar, QFileDialog, QMessageBox)

from PySide6.QtGui import QAction
from functools import partial


def format_initiative(x):
    return str(int(x)) if is_whole_number(x) else str(x)

# Helper function to create labeled input
def labeled_input(label_text, widget):
    layout = QVBoxLayout()
    layout.setAlignment(Qt.AlignTop)  # Align label + input to the top
    label = QLabel(label_text)
    layout.addWidget(label)
    layout.addWidget(widget)
    return layout

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("D&D Combat Tracker")
        self.setGeometry(100,100,900,600)

        self.comb_manager = CombatManager()
        self.undo_manager = UndoManager()

        self.rebuilding = False
        # Menu Bar
        self.menu_bar = self.menuBar()  # QMainWindow already provides menuBar()
        self.file_menu = self.menu_bar.addMenu("File")  # Creates 'File' dropdown

        # Open Encounter
        open_action = QAction("Open Encounter...", self)
        open_action.triggered.connect(self.open_encounter)
        self.file_menu.addAction(open_action)

        # Save Encounter
        save_action = QAction("Save Encounter", self)
        save_action.triggered.connect(self.save_encounter)
        self.file_menu.addAction(save_action)

        # Save As Encounter
        save_as_action = QAction("Save Encounter As...", self)
        save_as_action.triggered.connect(self.save_encounter_as)
        self.file_menu.addAction(save_as_action)


        #Setting Up the Table
        self.table = QTableWidget()
        self.table.setColumnCount(6)
        self.table.setHorizontalHeaderLabels(["Name", "Initiative", "AC", "Damage Taken", "Total HP", "Status"])

        #Keeping a column mapping
        self.columns ={"Name": 0 , "Initiative": 1, "AC": 2, "Damage Taken": 3, "Total HP": 4, "Status": 5}

        #This dictionary keeps a master list of all possible columns and their relative positions
        self.column_priority = {
            "Name": 0,
            "Initiative": 1,
            "AC": 2,
            "Damage": 3,
            "HP": 4,
            "Status": 5,
            "Comment": 6,
            "Spell Slots": 7,
            "Abilities": 10,
        }

        #This list is the master of which columns are currently displayed
        self.active_columns = ["Name", "Initiative", "AC", "Damage", "HP", "Status"]

        ordered_columns = sorted(
            self.active_columns,
            key=lambda name: self.column_priority[name]
        )

        self.col_index = {name: i for i, name in enumerate(ordered_columns)}

        #setting up a variable to check if we want a spell slot column
        self.spell_slots_column = False

        #Setting up a variable to check if we want an abilities column
        self.abilities_column = False

        #Setting up a signal for when cells are changed.
        # This automatically sends row and column to the on_cell_changed method
        self.table.cellChanged.connect(self.on_cell_changed)

        # Input Widgets
        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("Creature Name")
        name_layout = labeled_input("Combatant Name:", self.name_input)

        self.initiative_input = QSpinBox()
        self.initiative_input.setRange(0, 50)
        initiative_layout = labeled_input("Initiative:", self.initiative_input)

        self.ac_input = QSpinBox()
        self.ac_input.setRange(0, 50)
        ac_layout = labeled_input("AC:", self.ac_input)

        self.hp_total_input = QSpinBox()
        self.hp_total_input.setRange(0, 5000)
        hp_layout = labeled_input("Total HP:", self.hp_total_input)

        #Creating a button for adding combatants
        self.add_button = QPushButton("Add Combatant")
        self.add_button.clicked.connect(self.on_add_combatant_clicked)
        add_button_layout = QVBoxLayout()
        add_button_layout.addWidget(QLabel(""))  # empty space above the button
        add_button_layout.setAlignment(Qt.AlignTop)
        add_button_layout.addWidget(self.add_button)

        #Set custom context menu
        self.table.setContextMenuPolicy(Qt.CustomContextMenu)
        self.table.customContextMenuRequested.connect(self.show_context_menu)

        # Allow selecting whole rows
        self.table.setSelectionBehavior(QTableWidget.SelectRows)

        # Allow multiple rows to be selected
        self.table.setSelectionMode(QTableWidget.ExtendedSelection)

        #Input Layout
        input_layout = QHBoxLayout()
        input_layout.addLayout(name_layout)
        input_layout.addLayout(initiative_layout)
        input_layout.addLayout(ac_layout)
        input_layout.addLayout(hp_layout)
        input_layout.addLayout(add_button_layout)
        input_layout.addStretch()

        #Main Layout
        main_layout = QVBoxLayout() #Tells the Qwidget to use a vertical box layout
        main_layout.addLayout(input_layout) #Adds the input layout on top
        main_layout.addWidget(self.table) #Adds the table to the layout


        #The central widget
        central = QWidget()  # Telling the window that the central part is
        central.setLayout(main_layout)  # Tells the window to use the named layout
        self.setCentralWidget(central)


    def save_encounter(self):
        # Open a file dialog
        filename, _ = QFileDialog.getSaveFileName(
            self,
            "Save Encounter",
            "",  # default directory
            "JSON Files (*.json);;All Files (*)"
        )

        if not filename:
            return  # user canceled

        encounter_name = None

        # Call the CombatManager method
        self.comb_manager.save_encounter(filename, encounter_name)

    def save_encounter_as(self):
        pass

    def open_encounter(self):
        # Open a file dialog to let the user choose a file
        filename, _ = QFileDialog.getOpenFileName(
            self,
            "Open Encounter",
            "",  # default directory
            "JSON Files (*.json);;All Files (*)"
        )

        if filename:  # Only proceed if the user picked a file
            try:
                # Tell the combat manager to load the encounter from this file
                self.comb_manager.load_encounter(filename)

                # After loading, rebuild the table UI
                self.sort_table_initiative()

            except Exception as e:
                # If there’s an error (e.g., invalid file), show a message box
                QMessageBox.critical(
                    self,
                    "Error Loading Encounter",
                    f"Could not load encounter from file:\n{str(e)}"
                )


    #This method handles the right click context menu !!!
    def show_context_menu(self, pos):
        clicked_row = self.table.rowAt(pos.y())
        #First we set a flag based on whether the user actually clicked a row
        has_row = clicked_row != -1 and self.table.item(clicked_row,0) is not None

        menu = QMenu(self.table) #Note to self: Ensure stuff like QMenu has a parent i.e. includes self.table. Otherwise, we risk weird floating box errors or rendering behind table.

        undo_action = menu.addAction("Undo")
        undo_action.triggered.connect(self.handle_undo)

        redo_action = menu.addAction("Redo")
        redo_action.triggered.connect(self.handle_redo)

        if not self.undo_manager.undo_stack:
            undo_action.setEnabled(False)

        if not self.undo_manager.redo_stack:
            redo_action.setEnabled(False)

        #Position sensitive part of menu.
        #Only rendered if a row is clicked.
        if has_row:
            menu.addSeparator()
            remove_action = menu.addAction("Remove Combatant")
            remove_action.triggered.connect(partial(self.handle_remove_combatant,clicked_row))

            duplicate_action = menu.addAction("Duplicate Combatant")
            duplicate_action.triggered.connect(partial(self.duplicate_combatant_in_table,clicked_row))
            sort_action = menu.addAction("Sort By Initiative")
            sort_action.triggered.connect(self.sort_table_initiative)
            spells_action = menu.addAction("Add/Remove Spell Slots")
            spells_action.triggered.connect(partial(self.open_spell_slots_dialogue,clicked_row))

            abilities_action = menu.addAction("Add Ability")
            abilities_action.triggered.connect(partial(self.open_abilities_dialogue,clicked_row))

        menu.exec(self.table.viewport().mapToGlobal(pos))

    def handle_undo(self):
        self.undo_manager.undo()
        self.sort_table_initiative()

    def handle_redo(self):
        self.undo_manager.redo()
        self.sort_table_initiative()

    def handle_remove_combatant(self,clicked_row):
        selected_indices = self.table.selectionModel().selectedRows()  # Setting up a collection of selected rows to possibly delete multiple combatants
        # We check if the user has selected multiple rows, and if so we remove those
        if selected_indices:
            for index in sorted(selected_indices, key=lambda x: x.row(), reverse=True):
                self.remove_combatant_from_table(index.row())
        else:  # Else we simply delete the clicked row
            self.remove_combatant_from_table(clicked_row)

    # this helper method holds the spell slots dialogue
    def open_spell_slots_dialogue(self,clicked_row):
        # Open dialog to add ability
        # First we create a dialogue box
        dialog = QDialog(self)
        # Set the title
        dialog.setWindowTitle("Choose Caster Level")
        # Set the layout of the box
        dlg_layout = QVBoxLayout(dialog)

        caster_level_input = QSpinBox()
        caster_level_input.setRange(0, 20)

        dlg_layout.addWidget(QLabel("Caster Level"))
        dlg_layout.addWidget(caster_level_input)

        # Adds an okay and cancel button
        # The left input will respond to button.accepted, and the right to button.rejected
        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        dlg_layout.addWidget(buttons)

        def on_accept():
            # First we ensure there is actually a spell slot column
            self.ensure_spell_slots_column()

            # Then we update the combatant based on the input
            level = caster_level_input.value()
            combatant_id = self.fetch_combatant_id(clicked_row)
            self.comb_manager.add_caster_level(combatant_id, caster_level=level)

            # Then we render the spell slots based on the combat manager
            combatant = self.comb_manager.get_combatant_by_id(combatant_id)
            spell_slots = self.spell_slots_to_list(combatant.spell_slot_dict)
            col = self.columns["Spell Slots"]
            self.set_ability_widget(clicked_row, col, combatant_id, spell_slots,True)
            # Closes the dialogue and returns a successful result
            dialog.accept()

        buttons.accepted.connect(on_accept)
        buttons.rejected.connect(dialog.reject)

        dialog.exec()

    def open_abilities_dialogue(self,clicked_row):
        # Open dialog to add ability
        # First we create a dialogue box
        dialog = QDialog(self)
        # Set the title
        dialog.setWindowTitle("Define Ability")
        # Set the layout of the box
        dlg_layout = QVBoxLayout(dialog)

        ability_name_input = QLineEdit()
        ability_name_input.setPlaceholderText("Ability")
        dlg_layout.addWidget(QLabel("Ability Name"))
        dlg_layout.addWidget(ability_name_input)

        maximum_uses_input = QSpinBox()
        maximum_uses_input.setRange(1, 10)

        dlg_layout.addWidget(QLabel("Maximum Uses"))
        dlg_layout.addWidget(maximum_uses_input)

        # Adds an okay and cancel button
        # The left input will respond to button.accepted, and the right to button.rejected
        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        dlg_layout.addWidget(buttons)

        def on_accept():
            # First we ensure there is actually a spell slot column
            self.ensure_abilities_column()

            combatant_id = self.fetch_combatant_id(clicked_row)
            # Then we update the combatant based on the input
            ability_name = ability_name_input.text()
            maximum_uses = maximum_uses_input.value()
            self.comb_manager.add_ability(combatant_id, ability_name,maximum_uses)

            # Now we render the abilities based on the data in the combat manager
            combatant = self.comb_manager.get_combatant_by_id(combatant_id)
            abilities = sorted(self.abilities_to_list(combatant.ability_dict))

            col = self.columns["Abilities"]
            self.set_ability_widget(clicked_row,col,combatant_id,abilities)
            # Closes the dialogue and returns a successful result
            dialog.accept()

        buttons.accepted.connect(on_accept)
        buttons.rejected.connect(dialog.reject)

        dialog.exec()

    def set_ability_widget(self,row: int,col: int ,combatant_id ,abilities,is_spells=False):
        widget = AbilityTrackerWidget(
            self.comb_manager,
            combatant_id,
            abilities,
            is_spells
        )
        self.table.setCellWidget(row, col, widget)
        self.table.resizeRowToContents(row)  # Now the row we modified is resized to fit the content
        self.table.resizeColumnToContents(col)  # Now the column is resized to fit the content

    def add_combatant_to_table(self, combatant: Combatant):
        row_index = self.table.rowCount()
        # We set up the items to be added to the sheet. For now, everything is enabled, selectable and editable.
        # Consider if hp total should not be editable
        name_item = QTableWidgetItem(combatant.name)
        name_item.setFlags(Qt.ItemIsSelectable | Qt.ItemIsEnabled | Qt.ItemIsEditable)

        # We add the combatant ID to the item in the table.
        # This can then be accessed by calling self.table.item(row,0).data(Qt.UserRole) where row needs to be the relevant row number.
        name_item.setData(Qt.UserRole, combatant.id)

        ac_item = QTableWidgetItem(str(combatant.ac))
        ac_item.setFlags(Qt.ItemIsSelectable | Qt.ItemIsEnabled | Qt.ItemIsEditable)

        initiative = format_initiative(combatant.initiative)
        initiative_item = QTableWidgetItem(initiative)
        initiative_item.setFlags(Qt.ItemIsSelectable | Qt.ItemIsEnabled | Qt.ItemIsEditable)

        damage_item = QTableWidgetItem(str(combatant.damage_taken))
        damage_item.setFlags(Qt.ItemIsSelectable | Qt.ItemIsEnabled | Qt.ItemIsEditable)

        hp_item = QTableWidgetItem(str(combatant.hp_total))
        hp_item.setFlags(Qt.ItemIsSelectable | Qt.ItemIsEnabled | Qt.ItemIsEditable)

        status_item =QTableWidgetItem(str(combatant.status))
        status_item.setFlags(Qt.ItemIsSelectable | Qt.ItemIsEnabled | Qt.ItemIsEditable)


        self.table.insertRow(row_index)
        self.table.setItem(row_index, 0 , name_item)
        self.table.setItem(row_index, 1 , initiative_item)
        self.table.setItem(row_index, 2 , ac_item)
        self.table.setItem(row_index, 3 , damage_item)
        self.table.setItem(row_index, 4 , hp_item)
        self.table.setItem(row_index, 5 , status_item)

        caster_level = combatant.caster_level
        if caster_level >= 1:
            self.ensure_spell_slots_column()
            spell_slots = self.spell_slots_to_list(self.comb_manager.full_caster_progression[caster_level])
            col = self.columns["Spell Slots"]
            self.set_ability_widget(row_index,col, combatant.id, spell_slots,True)

        if combatant.ability_dict:
            self.ensure_abilities_column()
            abilities = sorted(self.abilities_to_list(combatant.ability_dict))
            col = self.columns["Abilities"]
            self.set_ability_widget(row_index, col,combatant.id, abilities)


    def remove_combatant_from_table(self,row):
        combatant_id = self.fetch_combatant_id(row)
        self.comb_manager.remove_combatant_by_id(combatant_id)
        self.table.removeRow(row)


    def duplicate_combatant_in_table(self,row):
        combatant_id = self.fetch_combatant_id(row)
        self.comb_manager.duplicate_combatant(combatant_id)
        # original = self.comb_manager.get_combatant_by_id(combatant_id)
        #
        # #setting up a duplicate
        # duplicate = Combatant(original.name,original.initiative,original.ac,original.hp_total)
        #
        # self.comb_manager.add_combatant(duplicate)
        self.sort_table_initiative()

    def update_combatant_row(self, row: int, combatant: Combatant):
        """
        Update all cells in table for a specific row from the combatant object.
        This avoids searching by name and prevents NoneType errors
        """
        if not self.table.item(row, 0):
            self.table.setItem(row,0,QTableWidgetItem())
        if not self.table.item(row,1):
            self.table.setItem(row, 1, QTableWidgetItem())
        if not self.table.item(row, 2):
            self.table.setItem(row,2,QTableWidgetItem())
        if not self.table.item(row, 3):
            self.table.setItem(row, 3, QTableWidgetItem())
        if not self.table.item(row, 4):
            self.table.setItem(row, 4, QTableWidgetItem())

        self.table.item(row,0).setText(combatant.name)
        self.table.item(row, 0).setData(Qt.UserRole, combatant.id)
        initiative = format_initiative(combatant.initiative)
        self.table.item(row,1).setText(initiative)
        self.table.item(row,2).setText(str(combatant.ac))
        self.table.item(row,3).setText(str(combatant.damage_taken))
        self.table.item(row,4).setText(str(combatant.hp_total))

    def give_combatant_spell_slots(self, row: int, level: int):
        """This method exists to give a combatant in a certain row spell slots."""
        #Checking that the row does not have an empty name
        combatant_id = self.fetch_combatant_id(row)
        self.comb_manager.add_caster_level(combatant_id,caster_level = level)

    def give_combatant_ability(self, row: int, ability_name: str, maximum_uses: int):
        """This method exists to give a combatant in a certain row an ability."""
        #Checking that the row does not have an empty name
        combatant_id = self.fetch_combatant_id(row)
        self.comb_manager.add_ability(combatant_id,ability_name,maximum_uses)

    def fetch_combatant_id(self,row):
        name_item = self.table.item(row,0)
        if not name_item:
            return
        #Fetching the combatant id from the table
        combatant_id = name_item.data(Qt.UserRole)
        return combatant_id

    def ensure_spell_slots_column(self):
        """This little method is just to create a spell slots column if none exists"""
        if self.spell_slots_column == False:
            # We automatically get the current number of columns
            current_cols = self.table.columnCount()

            #We check to see if there is already an abilities column
            if self.abilities_column:
                #We update the columns dictionary
                self.columns["Abilities"] +=1
                spell_col_index = current_cols - 1
                self.table.insertColumn(current_cols-1)
            else:
                spell_col_index = current_cols
                # We increase the number of columns by one
                self.table.setColumnCount(current_cols + 1)

            # Finally, we place a label at the top of the column, and update the columns dictionary
            self.table.setHorizontalHeaderItem(spell_col_index, QTableWidgetItem("Spell Slots"))
            self.columns["Spell Slots"] = spell_col_index

            self.spell_slots_column = True

    def ensure_abilities_column(self):
        """This method is similar to the above, in that its job is to ensure there is an 'abilities' column."""
        if self.abilities_column == False:
            # We automatically get the current number of columns
            current_cols = self.table.columnCount()
            #We then increase the number of columns by one
            self.table.setColumnCount(current_cols + 1)
            # Finally, we place a label at the top of the column and update the columns dictionary
            self.table.setHorizontalHeaderItem(current_cols, QTableWidgetItem("Abilities"))
            self.columns["Abilities"] = current_cols
            self.abilities_column = True

    #This little helper method converts spell slots dictionaries to a format suitable for the add_ability_slots_cell method.
    def spell_slots_to_list(self,dict):
        return [(f"Level {lvl}",count, lvl) for lvl, count in dict.items() if count >0]

    def abilities_to_list(self,dict):
        return [(ability_name, dict[ability_name].max,None) for ability_name in dict]

    #This method handles what happens when the add combatant button is clicked
    def on_add_combatant_clicked(self):
        name = self.name_input.text()
        initiative = self.initiative_input.value()
        ac = self.ac_input.value()
        hp = self.hp_total_input.value()
        if name:
            combatant = Combatant(name,initiative,ac,hp)
            self.comb_manager.add_combatant(combatant)

            #After adding, clears input
            self.name_input.clear()
            self.initiative_input.setValue(0)
            self.ac_input.setValue(0)
            self.hp_total_input.setValue(0)
            self.sort_table_initiative()
            return


    #This is the "handler method" which handles cells being changed
    def on_cell_changed(self,row,column):
        if self.rebuilding:
            return
        # Get the name of the combatant in this row

        combatant_id = self.fetch_combatant_id(row)
        #We copy the combatant for back-up purposes in case a roll-back is needed
        combatant = copy.deepcopy(self.comb_manager.get_combatant_by_id(combatant_id))

        # Get the new value typed by the user
        edited_item = self.table.item(row, column)
        if not edited_item:
            return
        edited_text = edited_item.text()

        try:
            if column == 0:
                self.undo_manager.do(SetNameCommand(manager=self.comb_manager,cid=combatant_id,new_name=edited_text))
                #self.comb_manager.set_combatant_name(combatant_id,edited_text)
            elif column == 1: #Checking if the edited column was initiative
                initiative = float(edited_text)
                self.undo_manager.do(SetInitiativeCommand(manager=self.comb_manager,cid=combatant_id,new_initiative=initiative))
                #self.comb_manager.set_combatant_initiative(combatant_id,initiative)
                if any(combatant.initiative >= com.initiative for com in self.comb_manager.combatants.values()):
                    self.sort_table_initiative()
                return
            elif column == 2: #Checking if the edited column was AC
                ac=int(edited_text)
                self.undo_manager.do(SetACCommand(manager=self.comb_manager,cid=combatant_id,new_ac=ac))
                #self.comb_manager.set_combatant_ac(combatant_id,int(edited_text))
            elif column == 3:  # Checking if the edited column was damage taken
                damage_taken = safe_eval(edited_text)
                self.undo_manager.do(SetDamageCommand(manager=self.comb_manager,cid=combatant_id,new_dmg=damage_taken))
                #self.comb_manager.set_combatant_damage(combatant_id,damage_taken)
            elif column == 4:  # Checking if the edited column was Hp total
                hp_tot = int(edited_text)
                self.undo_manager.do(SetHPTotCommand(manager=self.comb_manager,cid=combatant_id,new_hp=hp_tot))
                #self.comb_manager.set_combatant_hp_tot(combatant_id,int(edited_text))
            elif column == 5:
                self.undo_manager.do(SetStatusCommand(manager=self.comb_manager,cid=combatant_id,new_status=edited_text))
                #self.comb_manager.set_combatant_status(combatant_id,edited_text)

        except Exception as e:
            #This is intended to handle invalid inputs, such as writing abc in the damage taken column.
            #In case of an error, just returns the original value in the UI and ensures the combat manage is reset
            print(f"Error: {e}. Rolling back UI and combat manager.")
            self.comb_manager.update_combatant_by_id(combatant_id, combatant)
            self.rebuilding = True
            try:
                self.update_combatant_row(row,combatant)
            finally:
                self.rebuilding = False
            return

        finally:
            # This part refreshes the ui with the information from the combat manager
            if column != 1:
                combatant = self.comb_manager.get_combatant_by_id(combatant_id)
                self.rebuilding = True
                try:
                    self.update_combatant_row(row, combatant)
                finally:
                    self.rebuilding = False


    def sort_table_initiative(self):
        """This method will sort the table by initiative.
        The way it does so, is by first deleting everything in the ui, and then re-adding from the combat manager.
        This is a key method, as it is called whenever a new combatant is added."""
        # We first block the signals that could trigger Qt cells changed, as this may cause an infinite loop
        self.rebuilding = True
        self.table.blockSignals(True)
        try:
            self.table.setRowCount(0)
            for comb_id in self.comb_manager.turn_order:
                self.add_combatant_to_table(self.comb_manager.get_combatant_by_id(comb_id))

        finally:
            # At the end, we unblock the signals
            self.table.blockSignals(False)
            self.rebuilding = False



def run_app():
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())