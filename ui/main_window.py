import sys
import copy
from commands.commands import (SetNameCommand, SetACCommand, SetInitiativeCommand, SetHPTotCommand, \
    SetStatusCommand, SetSpellSlotsCommand,SetAbilitiesCommand, SetConditionsCommand, AdvanceRoundCommand, ResetRoundCommand,
                               ClearTrackerCommand, SetEncounterTitleCommand, SetPermanentCommand, ClearTrackerCompletelyCommand, AddCombatantCommand)
from models.combatant import Combatant

from services.combat_manager import CombatManager
from services.command_manager import CommandManager

from ui.delegates.damage_delegate import DamageDelegate
from ui.styling.themes import apply_theme,DARK_THEME,LIGHT_THEME

from ui.dialogs.ability_dialog import AbilityDialog
from ui.dialogs.spell_dialog import SpellDialog
from ui.dialogs.conditions_dialog import ConditionsDialog
from ui.dialogs.name_encounter_dialog import NameEncounterDialog
from ui.dialogs.confirmation_dialog import ConfirmationDialog
from ui.dialogs.duplicate_dialog import DuplicateDialog
from ui.table_mapper import CombatTableMapper

from PySide6.QtCore import Qt

from PySide6.QtWidgets import (QMainWindow, QApplication, QWidget, QTableWidget,
                               QVBoxLayout, QLineEdit, QPushButton, QHBoxLayout,
                               QSpinBox, QMenu, QLabel, QFileDialog, QMessageBox)

from PySide6.QtGui import QAction, QFont
from functools import partial


# Helper function to create labeled input
def labeled_input(label_text, widget):
    layout = QVBoxLayout()
    layout.setAlignment(Qt.AlignTop)  # Align label + input to the top

    label = QLabel(label_text)
    label.setStyleSheet("font-weight: 600")

    # Match the visual left edge of the input text
    left_margin = 5
    label.setContentsMargins(left_margin, 0, 0, 0)

    layout.addWidget(label)
    layout.addWidget(widget)
    return layout

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("D&D Combat Tracker")
        self.setGeometry(100,100,900,600)

        self.comb_manager = CombatManager()
        self.command_manager = CommandManager()



        self.rebuilding = False
        # Menu Bar
        self.menu_bar = self.menuBar()  # QMainWindow already provides menuBar()
        self.file_menu = self.menu_bar.addMenu("File")  # Creates 'File' dropdown

        #Name Encounter
        entitle_encounter_action = QAction("Name Encounter",self)
        entitle_encounter_action.triggered.connect(self.open_encounter_title_dialog)
        self.file_menu.addAction(entitle_encounter_action)

        #Clear Encounter Completely
        clear_encounter_completely_action = QAction("Clear Tracker Completely",self)
        clear_encounter_completely_action.triggered.connect(self.clear_tracker_completely)
        self.file_menu.addAction(clear_encounter_completely_action)

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

        #Make header semi-bold
        # self.table.horizontalHeader().setStyleSheet("""
        # QHeaderView::section {
        #     font-weight: 600;
        # }
        # """)
        # font = self.table.horizontalHeader().font()
        # font.setWeight(QFont.DemiBold)
        # font.setItalic(True)
        # font.setPointSize(10)
        # self.table.horizontalHeader().setFont(font)

        self.table_mapper = CombatTableMapper(self.table,self.comb_manager,self.command_manager)


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
        self.name_input.setMinimumWidth(150)

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
        # self.add_button.setMinimumHeight(32) #This and the next is one style
        # self.add_button.setStyleSheet("font-weight: bold;")
        # self.add_button.setIcon(QIcon.fromTheme("list-add")) #This is another style
        add_button_layout = QVBoxLayout()
        add_button_layout.addWidget(QLabel(""))  # empty space above the button
        add_button_layout.setAlignment(Qt.AlignTop)
        add_button_layout.addWidget(self.add_button)
        self.add_button.setStyleSheet("""
            QPushButton {
                font-weight: 600;
                padding: 6px 12px;
                border-radius: 6px;
                border: 1px solid #777;
            }

            QPushButton:hover {
                background-color: rgba(0, 0, 0, 0.08);
                }

            QPushButton:pressed {
                background-color: rgba(0, 0, 0, 0.15);
            }
        """)
        #background - color:  # 3A7CA5;

        #Create a field for setting encounter title
        self.encounter_title = QLabel("Untitled Encounter")
        self.encounter_title.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        self.encounter_title.setMinimumWidth(200)
        encounter_font = QFont("Palatino Linotype")
        encounter_font.setPointSize(20)
        encounter_font.setWeight(QFont.DemiBold)
        self.encounter_title.setFont(encounter_font)
        self.style_encounter()

        #Input Layout
        input_layout = QHBoxLayout()
        input_layout.addLayout(name_layout)
        input_layout.addLayout(initiative_layout)
        input_layout.addLayout(ac_layout)
        input_layout.addLayout(hp_layout)
        input_layout.addSpacing(10)
        input_layout.addLayout(add_button_layout)
        input_layout.addStretch()

        input_layout.addWidget(self.encounter_title)

        #Set custom context menu
        self.table.setContextMenuPolicy(Qt.CustomContextMenu)
        self.table.customContextMenuRequested.connect(self.show_context_menu)

        # Allow selecting whole rows
        self.table.setSelectionBehavior(QTableWidget.SelectRows)

        # Allow multiple rows to be selected
        self.table.setSelectionMode(QTableWidget.ExtendedSelection)



        # Building a bottom status bar:

        self.round_label = QLabel()
        self.update_round_display()
        self.next_round_button = QPushButton("Next Round")
        self.next_round_button.setStyleSheet("""
            QPushButton {
                padding: 6px 6px;
                border-radius: 6px;
                border: 1px solid #777;
            }
            """
            )
        self.next_round_button.clicked.connect(self.on_next_round_clicked)
        self.next_round_button.setShortcut("Space")

        self.statusBar().addPermanentWidget(self.round_label)
        self.statusBar().addPermanentWidget(self.next_round_button)

        #Main Layout
        main_layout = QVBoxLayout() #Tells the Qwidget to use a vertical box layout
        main_layout.addLayout(input_layout) #Adds the input layout on top
        main_layout.addSpacing(10)
        main_layout.addWidget(self.table) #Adds the table to the layout


        #The central widget
        central = QWidget()  # Telling the window that the central part is
        central.setLayout(main_layout)  # Tells the window to use the named layout
        self.setCentralWidget(central)

        self.apply_light_theme()

        #This removes the "focus square" when selecting row
        self.table.setFocusPolicy(Qt.NoFocus)

    def open_encounter_title_dialog(self):
        dialog = NameEncounterDialog(self)
        if dialog.exec():
            new_name = dialog.get_data()
            self.command_manager.do(SetEncounterTitleCommand(self.comb_manager, new_name))
            self.update_encounter_title()

    def clear_tracker_completely(self):
        dialog = ConfirmationDialog(self, warning_text="Deleting all combatants (including permanent)")
        if dialog.exec():
            self.command_manager.do(ClearTrackerCompletelyCommand(self.comb_manager))
            self.sort_table_initiative()
            self.update_round_display()
            self.update_encounter_title()

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
                self.update_round_display()
                self.update_encounter_title()

                self.command_manager.clear_queue()

            except Exception as e:
                # If there’s an error (e.g., invalid file), show a message box
                QMessageBox.critical(
                    self,
                    "Error Loading Encounter",
                    f"Could not load encounter from file:\n{str(e)}"
                )

    def update_round_display(self):
        self.round_label.setText(f"Round: {self.comb_manager.round}")

    def update_encounter_title(self):
        self.encounter_title.setText(self.comb_manager.encounter_title)

    def style_encounter(self):
        if self.table_mapper.dark_mode:
            self.encounter_title.setStyleSheet("""
            color: #f0f0f0;
            padding: 2px 6px;
        """)
        else:
            self.encounter_title.setStyleSheet("""
            color: #B82A27;
            padding: 2px 6px;
            """)

    #This method handles the right click context menu !!!
    def show_context_menu(self, pos):
        clicked_row = self.table.rowAt(pos.y())
        #First we set a flag based on whether the user actually clicked a row
        has_row = clicked_row != -1 and self.table.item(clicked_row,0) is not None

        menu = QMenu(self.table) #Note to self: Ensure stuff like QMenu has a parent i.e. includes self.table. Otherwise, we risk weird floating box errors or rendering behind table.

        undo_action = menu.addAction("Undo")
        undo_action.triggered.connect(self.handle_undo)
        if not self.command_manager.undo_stack:
            undo_action.setEnabled(False)

        redo_action = menu.addAction("Redo")
        redo_action.triggered.connect(self.handle_redo)
        if not self.command_manager.redo_stack:
            redo_action.setEnabled(False)

        reset_round_action = menu.addAction("Reset Round")
        reset_round_action.triggered.connect(self.handle_round_reset)

        reset_encounter_action = menu.addAction("Clear Tracker")
        reset_encounter_action.triggered.connect(self.handle_clear_tracker)

        sort_action = menu.addAction("Sort By Initiative")
        sort_action.triggered.connect(self.sort_table_initiative)

        #Position sensitive part of menu.
        #Only rendered if a row is clicked.
        if has_row:
            menu.addSeparator()
            remove_action = menu.addAction("Remove Combatant")
            remove_action.triggered.connect(partial(self.handle_remove_combatant,clicked_row))

            duplicate_action = menu.addAction("Duplicate Combatant")
            duplicate_action.triggered.connect(partial(self.handle_duplicate,clicked_row))

            duplicate_mult_action = menu.addAction("Duplicate multiple")
            duplicate_mult_action.triggered.connect(partial(self.handle_duplicate_mult,clicked_row))

            permanent_action = menu.addAction("Toggle Permanent Combatant")
            permanent_action.triggered.connect(partial(self.handle_permanent,clicked_row))

            spells_action = menu.addAction("Add/Remove Spell Slots")
            spells_action.triggered.connect(partial(self.open_spell_slots_dialogue,clicked_row))

            abilities_action = menu.addAction("Add Ability")
            abilities_action.triggered.connect(partial(self.open_abilities_dialogue,clicked_row))

            conditions_action = menu.addAction("Add/Remove Conditions")
            conditions_action.triggered.connect(partial(self.open_conditions_dialog, clicked_row))

        menu.exec(self.table.viewport().mapToGlobal(pos))

    #These handler methods handle parts of the context menu
    def handle_undo(self):
        self.command_manager.undo()
        self.sort_table_initiative()
        self.update_round_display()
        self.update_encounter_title()

    def handle_redo(self):
        self.command_manager.redo()
        self.sort_table_initiative()
        self.update_round_display()
        self.update_encounter_title()

    def handle_round_reset(self):
        self.command_manager.do(ResetRoundCommand(self.comb_manager))
        self.update_round_display()

    def handle_clear_tracker(self):
        self.command_manager.do(ClearTrackerCommand(self.comb_manager))
        self.sort_table_initiative()
        self.update_round_display()
        self.update_encounter_title()

    def handle_remove_combatant(self,clicked_row):
        selected_rows = self.table.selectionModel().selectedRows()  # Setting up a collection of selected rows to possibly delete multiple combatants
        self.table_mapper.remove_combatant_from_table(clicked_row,selected_rows)
        self.sort_table_initiative()
        #if selected_rows:
        #    for index in sorted(selected_rows, key=lambda x: x.row(), reverse=True):
        #        self.table_mapper.remove_combatant_from_table(index.row())
        #else:  # Else we simply delete the clicked row
        #    self.table_mapper.remove_combatant_from_table(clicked_row)

    def handle_duplicate(self,row):
        self.table_mapper.duplicate_combatant_in_table(row)
        self.sort_table_initiative()

    def handle_duplicate_mult(self,row):
        dialog = DuplicateDialog(self)
        if dialog.exec():
            num_copies = dialog.get_data()
            self.table_mapper.duplicate_combatant_in_table_n_times(row,num_copies)
            self.sort_table_initiative()

    def handle_permanent(self,clicked_row):
        combatant_id = self.table_mapper.fetch_combatant_id(clicked_row)
        self.command_manager.do(SetPermanentCommand(self.comb_manager,combatant_id))

    def open_spell_slots_dialogue(self,clicked_row):
        dialog = SpellDialog(self)

        if dialog.exec():
            #First we update the combatant based on the input
            level = dialog.get_data()
            combatant_id = self.table_mapper.fetch_combatant_id(clicked_row)

            self.command_manager.do(SetSpellSlotsCommand(manager=self.comb_manager,cid=combatant_id,new_caster_level=level))

            self.table_mapper.draw_combatant_spell_slots(clicked_row,combatant_id)


    def open_abilities_dialogue(self,clicked_row):
        dialog = AbilityDialog(self)

        if dialog.exec():
            # First we update the combat manager with the data
            ability_name, max_uses = dialog.get_data()
            combatant_id = self.table_mapper.fetch_combatant_id(clicked_row)

            self.command_manager.do(SetAbilitiesCommand(self.comb_manager,combatant_id,ability_name,max_uses))

            self.table_mapper.draw_combatant_abilities(clicked_row,combatant_id)

    def open_conditions_dialog(self,row):
        combatant_id = self.table_mapper.fetch_combatant_id(row)
        combatant = self.comb_manager.get_combatant_by_id(combatant_id)
        conditions = copy.deepcopy(combatant.conditions)
        dialog = ConditionsDialog(conditions, self)
        if dialog.exec():
            new_conditions = dialog.get_data()

            self.command_manager.do(SetConditionsCommand(
                manager=self.comb_manager,
                cid=combatant_id,
                new_conditions=new_conditions
            ))

            self.table_mapper.update_combatant_row(row,combatant)


    #This method handles what happens when the add combatant button is clicked
    def on_add_combatant_clicked(self):
        name = self.name_input.text()
        initiative = self.initiative_input.value()
        ac = self.ac_input.value()
        hp = self.hp_total_input.value()
        if name:
            self.command_manager.do(AddCombatantCommand(self.comb_manager,name,initiative,ac,hp))
            # combatant = Combatant(name,initiative,ac,hp)
            # self.comb_manager.add_combatant(combatant)

            #After adding, clears input
            self.name_input.clear()
            self.initiative_input.setValue(0)
            self.ac_input.setValue(0)
            self.hp_total_input.setValue(0)
            self.sort_table_initiative()
            return


    #This handler method handles when the next round button is clicked
    def on_next_round_clicked(self):
        self.command_manager.do(AdvanceRoundCommand(self.comb_manager))
        self.update_round_display()
        self.table_mapper.refresh_table()

    #This is the "handler method" which handles cells being changed
    def on_cell_changed(self,row,column):
        print(self.command_manager.undo_stack)
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
                self.command_manager.do(SetNameCommand(manager=self.comb_manager,cid=combatant_id,new_name=edited_text))
            elif column == self.table_mapper.col_index["Initiative"]: #Checking if the edited column was initiative
                initiative = float(edited_text)
                self.command_manager.do(SetInitiativeCommand(manager=self.comb_manager,cid=combatant_id,new_initiative=initiative))
                init_comb = self.comb_manager.get_combatant_by_id(combatant_id)
                if any(init_comb.initiative >= com.initiative for com in self.comb_manager.combatants.values()):
                    self.sort_table_initiative()
                return
            elif column == self.table_mapper.col_index["AC"]: #Checking if the edited column was AC
                ac=int(edited_text)
                self.command_manager.do(SetACCommand(manager=self.comb_manager,cid=combatant_id,new_ac=ac))
            elif column == self.table_mapper.col_index["HP"]:  # Checking if the edited column was Hp total
                hp_tot = int(edited_text)
                self.command_manager.do(SetHPTotCommand(manager=self.comb_manager,cid=combatant_id,new_hp=hp_tot))
            elif column == self.table_mapper.col_index["Status"]:
                self.command_manager.do(SetStatusCommand(manager=self.comb_manager,cid=combatant_id,new_status=edited_text))

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
            self.open_conditions_dialog(row)
            return

    # Settings Methods
    def apply_light_theme(self):
        apply_theme(LIGHT_THEME)
        self.table_mapper.dark_mode=False
        #self.table_mapper.style_headers()

    def apply_dark_theme(self):
        apply_theme(DARK_THEME)
        self.table_mapper.dark_mode=True
        #self.table_mapper.style_headers()

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



