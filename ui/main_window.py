import sys
import copy
from commands.commands import (SetNameCommand, SetACCommand, SetInitiativeCommand, SetHPTotCommand, \
    SetStatusCommand, SetSpellSlotsCommand,SetAbilitiesCommand, SetConditionsCommand)
from models.combatant import Combatant

from services.combat_manager import CombatManager
from services.maths import is_whole_number
from services.undo_manager import UndoManager

from ui.delegates.damage_delegate import DamageDelegate
from ui.themes import apply_theme,DARK_THEME,LIGHT_THEME
from ui.dialogs.ability_dialog import AbilityDialog
from ui.dialogs.spell_dialog import SpellDialog
from ui.dialogs.conditions_dialog import ConditionsDialog
from ui.table_mapper import CombatTableMapper

from PySide6.QtCore import Qt

from PySide6.QtWidgets import (QMainWindow, QApplication, QWidget, QTableWidget,
                               QTableWidgetItem, QVBoxLayout, QLineEdit, QPushButton, QHBoxLayout,
                               QSpinBox, QMenu, QLabel, QFileDialog, QMessageBox)

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
        self.table.setColumnCount(7)
        self.table.setHorizontalHeaderLabels(["Name", "Initiative", "AC", "Damage Taken", "Total HP", "Conditions", "Status"])

        self.table_mapper = CombatTableMapper(self.table,self.comb_manager)

        #Setting up a signal for when cells are double-clicked.
        self.table.itemDoubleClicked.connect(self.on_item_double_clicked)

        #Setting up a signal for when cells are changed.
        # This automatically sends row and column to the on_cell_changed method
        self.table.cellChanged.connect(self.on_cell_changed)

        #Setting a separate delegate for handling edits in the damage column
        self.table.setItemDelegateForColumn(
            self.table_mapper.col_index["Damage"],
            DamageDelegate(parent=self,
                           manager=self.comb_manager,
                           refresh_row_callback=self.table_mapper.update_row_color,
                           fetch_combatant_callback=self.table_mapper.fetch_combatant_id)
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
            duplicate_action.triggered.connect(partial(self.handle_duplicate,clicked_row))
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
                self.table_mapper.remove_combatant_from_table(index.row())
        else:  # Else we simply delete the clicked row
            self.table_mapper.remove_combatant_from_table(clicked_row)

    def handle_duplicate(self,row):
        self.table_mapper.duplicate_combatant_in_table(row)
        self.sort_table_initiative()

    def open_spell_slots_dialogue(self,clicked_row):
        dialog = SpellDialog(self)

        if dialog.exec():
            #First we update the combatant based on the input
            level = dialog.get_data()
            combatant_id = self.table_mapper.fetch_combatant_id(clicked_row)

            self.undo_manager.do(SetSpellSlotsCommand(manager=self.comb_manager,cid=combatant_id,new_caster_level=level))

            self.table_mapper.draw_combatant_spell_slots(clicked_row,combatant_id)


    def open_abilities_dialogue(self,clicked_row):
        dialog = AbilityDialog(self)

        if dialog.exec():
            # First we update the combat manager with the data
            ability_name, max_uses = dialog.get_data()
            combatant_id = self.table_mapper.fetch_combatant_id(clicked_row)

            self.undo_manager.do(SetAbilitiesCommand(self.comb_manager,combatant_id,ability_name,max_uses))

            self.table_mapper.draw_combatant_abilities(clicked_row,combatant_id)

    def open_conditions_dialog(self,combatant_id):
        combatant = self.comb_manager.get_combatant_by_id(combatant_id)
        conditions = copy.deepcopy(combatant.conditions)
        dialog = ConditionsDialog(conditions, self)
        if dialog.exec():
            new_conditions = dialog.get_data()

            self.undo_manager.do(SetConditionsCommand(
                manager=self.comb_manager,
                cid=combatant_id,
                new_conditions=new_conditions
            ))



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
        if column == self.table_mapper.col_index["Damage"]:  # Checking if the edited column was damage taken
                #This just returns, as the damage delegate takes care of these edits
                return


        # Get the id of the combatant in this row
        combatant_id = self.table_mapper.fetch_combatant_id(row)
        #We copy the combatant for back-up purposes in case a roll-back is needed
        combatant = copy.deepcopy(self.comb_manager.get_combatant_by_id(combatant_id))

        # Get the new value typed by the user
        edited_item = self.table.item(row, column)
        if not edited_item:
            return
        edited_text = edited_item.text()

        try:
            if column == self.table_mapper.col_index["Name"]:
                self.undo_manager.do(SetNameCommand(manager=self.comb_manager,cid=combatant_id,new_name=edited_text))
            elif column == self.table_mapper.col_index["Initiative"]: #Checking if the edited column was initiative
                initiative = float(edited_text)
                self.undo_manager.do(SetInitiativeCommand(manager=self.comb_manager,cid=combatant_id,new_initiative=initiative))
                if any(combatant.initiative >= com.initiative for com in self.comb_manager.combatants.values()):
                    self.sort_table_initiative()
                return
            elif column == self.table_mapper.col_index["AC"]: #Checking if the edited column was AC
                ac=int(edited_text)
                self.undo_manager.do(SetACCommand(manager=self.comb_manager,cid=combatant_id,new_ac=ac))
            elif column == self.table_mapper.col_index["HP"]:  # Checking if the edited column was Hp total
                hp_tot = int(edited_text)
                self.undo_manager.do(SetHPTotCommand(manager=self.comb_manager,cid=combatant_id,new_hp=hp_tot))
            elif column == self.table_mapper.col_index["Status"]:
                self.undo_manager.do(SetStatusCommand(manager=self.comb_manager,cid=combatant_id,new_status=edited_text))

        except Exception as e:
            #This is intended to handle invalid inputs, such as writing abc in the damage taken column.
            #In case of an error, just returns the original value in the UI and ensures the combat manage is reset
            print(f"Error: {e}. Rolling back UI and combat manager.")
            self.comb_manager.update_combatant_by_id(combatant_id, combatant)
            self.rebuilding = True
            try:
                self.table_mapper.update_combatant_row(row,combatant)
            finally:
                self.rebuilding = False
            return

        finally:
            # This part refreshes the ui with the information from the combat manager
            if column != self.table_mapper.col_index["Initiative"]:
                combatant = self.comb_manager.get_combatant_by_id(combatant_id)
                self.rebuilding = True
                try:
                    self.table_mapper.update_combatant_row(row, combatant)
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
                self.table_mapper.add_combatant_to_table(self.comb_manager.get_combatant_by_id(comb_id))

        finally:
            # At the end, we unblock the signals
            self.table.blockSignals(False)
            self.rebuilding = False

    def on_item_double_clicked(self, item):
        row = item.row()
        column = item.column()
        combatant_id = self.table_mapper.fetch_combatant_id(row)

        if column == self.table_mapper.col_index["Conditions"]:
            self.open_conditions_dialog(combatant_id)
            return

        # combatant = self.comb_manager.get_combatant_by_id(combatant_id)
        #
        # # prevent signal loop while we modify UI
        # self.rebuilding = True
        # try:
        #     item.setText(combatant.damage_expr)
        # finally:
        #     self.rebuilding = False

    # Settings Methods
    def apply_light_theme(self):
        apply_theme(LIGHT_THEME)

    def apply_dark_theme(self):
        apply_theme(DARK_THEME)

    #------------------------- HOLDING ----------------#
    def give_combatant_spell_slots(self, row: int, level: int):
        """This method exists to give a combatant in a certain row spell slots."""
        #Checking that the row does not have an empty name
        combatant_id = self.table_mapper.fetch_combatant_id(row)
        self.comb_manager.set_caster_level(combatant_id,caster_level = level)

    def give_combatant_ability(self, row: int, ability_name: str, maximum_uses: int):
        """This method exists to give a combatant in a certain row an ability."""
        #Checking that the row does not have an empty name
        combatant_id = self.table_mapper.fetch_combatant_id(row)
        self.comb_manager.add_ability(combatant_id,ability_name,maximum_uses)






def run_app():
    app = QApplication(sys.argv)

    window = MainWindow()
    window.show()
    sys.exit(app.exec())



