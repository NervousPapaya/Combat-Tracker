import sys
import copy
from commands.commands import SetNameCommand, SetACCommand, SetInitiativeCommand, SetHPTotCommand, \
    SetStatusCommand
from models.combatant import Combatant

from services.combat_manager import CombatManager
from services.maths import is_whole_number
from services.undo_manager import UndoManager

from ui.delegates.damage_delegate import DamageDelegate
from ui.styling.themes import apply_theme,DARK_THEME,LIGHT_THEME
from ui.abilitywidget import AbilityTrackerWidget
from ui.dialogs.ability_dialog import AbilityDialog
from ui.dialogs.spell_dialog import SpellDialog

from PySide6.QtCore import Qt

from PySide6.QtWidgets import (QMainWindow, QApplication, QWidget, QTableWidget,
                               QTableWidgetItem, QVBoxLayout, QLineEdit, QPushButton, QHBoxLayout,
                               QSpinBox, QMenu, QLabel, QFileDialog, QMessageBox)

from PySide6.QtGui import QAction, QColor
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

        # Adding a settings menu to the menu bar
        self.settings_menu = self.menu_bar.addMenu("Settings")
        theme_menu = self.settings_menu.addMenu("Theme")

        light_action = QAction("Light", self)
        dark_action = QAction("Dark", self)

        light_action.triggered.connect(self.apply_light_theme)
        dark_action.triggered.connect(self.apply_dark_theme)

        theme_menu.addAction(light_action)
        theme_menu.addAction(dark_action)



        #Setting Up the Table
        self.table = QTableWidget()
        self.table.setColumnCount(6)
        self.table.setHorizontalHeaderLabels(["Name", "Initiative", "AC", "Damage Taken", "Total HP", "Status"])

        #This dictionary keeps a master list of all possible columns and their relative positions
        self.column_priority = {
            "Name": 0,
            "Initiative": 1,
            "AC": 2,
            "Damage": 3,
            "HP": 4,
            "Condition": 5,
            "Status": 6,
            "Spell Slots": 7,
            "Abilities": 10,
        }

        #This list is the master of which columns are currently displayed
        self.active_columns = ["Name", "Initiative", "AC", "Damage", "HP", "Status"]
        self.active_columns = set(self.active_columns)
        ordered_columns = sorted(
            self.active_columns,
            key=lambda name: self.column_priority[name]
        )
        #The following dictionary allows us to get a columns index by its name
        #Note: This is NOT dynamic and must be updated after each creation of a column. The method for creating columns has this resorting built in.
        self.col_index = {name: i for i, name in enumerate(ordered_columns)}

        #setting up a variable to check if we want a spell slot column
        self.spell_slots_column = False

        #Setting up a variable to check if we want an abilities column
        self.abilities_column = False

        #Setting up a signal for when cells are double-clicked.
        self.table.itemDoubleClicked.connect(self.on_item_double_clicked)

        #Setting up a signal for when cells are changed.
        # This automatically sends row and column to the on_cell_changed method
        self.table.cellChanged.connect(self.on_cell_changed)

        #Setting a separate delegate for handling edits in the damage column
        self.table.setItemDelegateForColumn(
            self.col_index["Damage"],
            DamageDelegate(self, self.comb_manager)
        )

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

    #These three handler methods handle parts of the context menu
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

    def open_spell_slots_dialogue(self,clicked_row):
        dialog = SpellDialog(self)

        if dialog.exec():
            #First we ensure there is actually a spell slot column
            self.ensure_spell_slots_column()

            # Then we update the combatant based on the input
            level = dialog.get_data()
            combatant_id = self.fetch_combatant_id(clicked_row)
            self.comb_manager.add_caster_level(combatant_id, caster_level=level)

            # Then we render the spell slots based on the combat manager
            combatant = self.comb_manager.get_combatant_by_id(combatant_id)
            spell_slots = self.spell_slots_to_list(combatant.spell_slot_dict)
            col = self.col_index["Spell Slots"]
            self.set_ability_widget(clicked_row, col, combatant_id, spell_slots,True)

    def open_abilities_dialogue(self,clicked_row):
        dialog = AbilityDialog(self)

        if dialog.exec():
            # First we ensure there is actually a spell slot column
            self.ensure_abilities_column()

            #Then we update the combat manager with the data
            ability_name, max_uses = dialog.get_data()
            combatant_id = self.fetch_combatant_id(clicked_row)
            self.comb_manager.add_ability(combatant_id, ability_name, max_uses)


            # Now we render the abilities based on the data in the combat manager
            combatant = self.comb_manager.get_combatant_by_id(combatant_id)
            abilities = sorted(self.abilities_to_list(combatant.ability_dict))
            col = self.col_index["Abilities"]
            self.set_ability_widget(clicked_row,col,combatant_id,abilities)

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
        self.table.setItem(row_index, self.col_index["Name"] , name_item)
        self.table.setItem(row_index, self.col_index["Initiative"] , initiative_item)
        self.table.setItem(row_index, self.col_index["AC"] , ac_item)
        self.table.setItem(row_index, self.col_index["Damage"] , damage_item)
        self.table.setItem(row_index, self.col_index["HP"] , hp_item)
        self.table.setItem(row_index, self.col_index["Status"] , status_item)

        caster_level = combatant.caster_level
        if caster_level >= 1:
            self.ensure_spell_slots_column()
            spell_slots = self.spell_slots_to_list(self.comb_manager.full_caster_progression[caster_level])
            col = self.col_index["Spell Slots"]
            self.set_ability_widget(row_index,col, combatant.id, spell_slots,True)

        if combatant.ability_dict:
            self.ensure_abilities_column()
            abilities = sorted(self.abilities_to_list(combatant.ability_dict))
            col = self.col_index["Abilities"]
            self.set_ability_widget(row_index, col,combatant.id, abilities)

        self.update_row_color(row_index)


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
        if not self.table.item(row, self.col_index["Name"]):
            self.table.setItem(row,self.col_index["Name"],QTableWidgetItem())
        if not self.table.item(row,self.col_index["Initiative"]):
            self.table.setItem(row, self.col_index["Initiative"], QTableWidgetItem())
        if not self.table.item(row, self.col_index["AC"]):
            self.table.setItem(row,self.col_index["AC"],QTableWidgetItem())
        if not self.table.item(row, self.col_index["Damage"]):
            self.table.setItem(row, self.col_index["Damage"], QTableWidgetItem())
        if not self.table.item(row, self.col_index["HP"]):
            self.table.setItem(row, self.col_index["HP"], QTableWidgetItem())

        self.table.item(row,self.col_index["Name"]).setText(combatant.name)
        self.table.item(row, self.col_index["Name"]).setData(Qt.UserRole, combatant.id)
        initiative = format_initiative(combatant.initiative)
        self.table.item(row,self.col_index["Initiative"]).setText(initiative)
        self.table.item(row,self.col_index["AC"]).setText(str(combatant.ac))
        self.table.item(row,self.col_index["Damage"]).setText(str(combatant.damage_taken))
        self.table.item(row,self.col_index["HP"]).setText(str(combatant.hp_total))

        self.update_row_color(row)

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


    #This little helper method converts spell slots dictionaries to a format suitable for the add_ability_slots_cell method.
    def spell_slots_to_list(self,spell_dict):
        return [(f"Level {lvl}",count, lvl) for lvl, count in spell_dict.items() if count >0]

    def abilities_to_list(self,ab_dict):
        return [(ability_name, ab_dict[ability_name].max,None) for ability_name in ab_dict]

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
        if column == self.col_index["Damage"]:  # Checking if the edited column was damage taken
                #This just returns, as the damage delegate takes care of these edits
                return


        # Get the id of the combatant in this row
        combatant_id = self.fetch_combatant_id(row)
        #We copy the combatant for back-up purposes in case a roll-back is needed
        combatant = copy.deepcopy(self.comb_manager.get_combatant_by_id(combatant_id))

        # Get the new value typed by the user
        edited_item = self.table.item(row, column)
        if not edited_item:
            return
        edited_text = edited_item.text()

        try:
            if column == self.col_index["Name"]:
                self.undo_manager.do(SetNameCommand(manager=self.comb_manager,cid=combatant_id,new_name=edited_text))
            elif column == self.col_index["Initiative"]: #Checking if the edited column was initiative
                initiative = float(edited_text)
                self.undo_manager.do(SetInitiativeCommand(manager=self.comb_manager,cid=combatant_id,new_initiative=initiative))
                if any(combatant.initiative >= com.initiative for com in self.comb_manager.combatants.values()):
                    self.sort_table_initiative()
                return
            elif column == self.col_index["AC"]: #Checking if the edited column was AC
                ac=int(edited_text)
                self.undo_manager.do(SetACCommand(manager=self.comb_manager,cid=combatant_id,new_ac=ac))
            # elif column == self.col_index["Damage"]:  # Checking if the edited column was damage taken
            #     damage_taken = safe_eval(edited_text)
            #     self.undo_manager.do(SetDamageCommand(manager=self.comb_manager,cid=combatant_id,new_dmg=damage_taken,new_dmg_expr=edited_text))
            elif column == self.col_index["HP"]:  # Checking if the edited column was Hp total
                hp_tot = int(edited_text)
                self.undo_manager.do(SetHPTotCommand(manager=self.comb_manager,cid=combatant_id,new_hp=hp_tot))
            elif column == self.col_index["Status"]:
                self.undo_manager.do(SetStatusCommand(manager=self.comb_manager,cid=combatant_id,new_status=edited_text))

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
            if column != self.col_index["Initiative"]:
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

    def on_item_double_clicked(self, item):
        row = item.row()
        column = item.column()

        # only apply to Damage Taken column
        if column != self.col_index["Damage"]:
            return

        combatant_id = self.fetch_combatant_id(row)
        combatant = self.comb_manager.get_combatant_by_id(combatant_id)

        # prevent signal loop while we modify UI
        self.rebuilding = True
        try:
            item.setText(combatant.damage_expr)
        finally:
            self.rebuilding = False

    def ordered_columns(self):
        return sorted(
            self.active_columns,
            key=lambda name: self.column_priority[name]
        )

    def rebuild_columns_index(self):
        ordered_columns = self.ordered_columns()
        self.col_index = {name: i for i, name in enumerate(ordered_columns)}

    def create_column(self,column_name: str):
        if column_name in self.active_columns:
            raise Exception(f"Column with name {column_name} already exists")
        if column_name not in self.column_priority:
            raise Exception(f"Column name must be in the pre-defined list")
        else:

            self.active_columns.add(column_name)

            self.rebuild_columns_index()

            column_index = self.col_index[column_name]

            self.table.insertColumn(column_index)
            self.table.setHorizontalHeaderItem(column_index, QTableWidgetItem(column_name))

    def get_insert_position(self, column_name):
        priority = self.column_priority[column_name]

        for i, name in enumerate(self.ordered_columns()):
            if self.column_priority[name] > priority:
                return i

        return len(self.active_columns)

    def ensure_spell_slots_column(self):
        """This little method is just to create a spell slots column if none exists"""
        if self.spell_slots_column:
            return
        else:
            self.create_column("Spell Slots")
            self.spell_slots_column = True

    def ensure_abilities_column(self):
        """This method is similar to the above, in that its job is to ensure there is an 'abilities' column."""
        if self.abilities_column:
            return
        else:
            self.create_column("Abilities")
            self.abilities_column = True

    def update_row_color(self, row):
        combatant_id = self.fetch_combatant_id(row)
        combatant = self.comb_manager.get_combatant_by_id(combatant_id)
        hp_left = combatant.hp_total - combatant.damage_taken

        if hp_left <= 0:
            color = "#ff7a7a"  # dead (dark red)
        elif hp_left <= combatant.hp_total/2:
            color = "#ffcc66"  # danger (orange/yellow)
        else:
            color = None

        for col in range(self.table.columnCount()):
            item = self.table.item(row, col)
            if not item:
                continue

            if color:
                item.setBackground(QColor(color))
            else:
                item.setBackground(QColor(0, 0, 0, 0))  # reset


    # Settings Methods
    def apply_light_theme(self):
        apply_theme(LIGHT_THEME)

    def apply_dark_theme(self):
        apply_theme(DARK_THEME)




def run_app():
    app = QApplication(sys.argv)

    window = MainWindow()
    window.show()
    sys.exit(app.exec())