
from PySide6.QtCore import Qt

from PySide6.QtWidgets import QTableWidgetItem
from PySide6.QtGui import QColor, QFont

from models.combatant import Combatant
from services.formating import abilities_to_list, spell_slots_to_list, format_initiative, format_conditions
from ui.abilitywidget import AbilityTrackerWidget
from ui.styling.color_themes import column_coloring_dark,column_coloring_light
from commands.commands import DuplicateCombatantNTimesCommand,DuplicateCombatantCommand,DeleteCombatantCommand,DeleteMultipleCombatantsCommand


#This class should handle the table in the main UI
class CombatTableMapper:
    def __init__(self, table, combat_manager,undo_manager):
        self.table=table
        self.comb_manager = combat_manager
        self.undo_manager = undo_manager

        #This dictionary keeps a master list of all possible columns and their relative positions
        self.column_priority = {
            "Name": 0,
            "Initiative": 1,
            "AC": 2,
            "Damage": 3,
            "HP": 4,
            "Conditions": 5,
            "Status": 6,
            "Spell Slots": 7,
            "Abilities": 10,
        }

        # These Column groups can be used for coloring purposes
        self.column_groups = {
            "combat": ["Name", "Initiative", "AC"],
            "damage": ["Damage", "HP"],
            "state": ["Conditions", "Status"],
            "other":["Spell Slots","Abilities"]
        }

        #This list is the master of which columns are currently displayed
        self.active_columns = ["Name", "Initiative", "AC", "Damage", "HP", "Conditions", "Status"]
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

        #Setting up a dark mode flag
        self.dark_mode = False

    def add_combatant_to_table(self, combatant: Combatant):
        row_index = self.table.rowCount()
        self.table.insertRow(row_index)

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

        conditions_string = format_conditions(combatant)
        conditions_item = QTableWidgetItem(conditions_string)
        conditions_item.setFlags(Qt.ItemIsSelectable | Qt.ItemIsEnabled)
        #conditions_item.setFlags(Qt.ItemIsSelectable)

        self.table.setItem(row_index, self.col_index["Name"] , name_item)
        self.table.setItem(row_index, self.col_index["Initiative"] , initiative_item)
        self.table.setItem(row_index, self.col_index["AC"] , ac_item)
        self.table.setItem(row_index, self.col_index["Damage"] , damage_item)
        self.table.setItem(row_index, self.col_index["HP"] , hp_item)
        self.table.setItem(row_index, self.col_index["Conditions"] , conditions_item)
        self.table.setItem(row_index, self.col_index["Status"] , status_item)



        caster_level = combatant.caster_level
        if caster_level >= 1:
            self.ensure_spell_slots_column()
            spell_slots = spell_slots_to_list(self.comb_manager.full_caster_progression[caster_level])
            col = self.col_index["Spell Slots"]
            self.set_ability_widget(row_index,col, combatant.id, spell_slots,True)

        if combatant.ability_dict:
            self.ensure_abilities_column()
            abilities = sorted(abilities_to_list(combatant.ability_dict))
            col = self.col_index["Abilities"]
            self.set_ability_widget(row_index, col,combatant.id, abilities)

        self.update_row_color(row_index)

    def duplicate_combatant_in_table(self,row):
        combatant_id = self.fetch_combatant_id(row)
        self.comb_manager.duplicate_combatant(combatant_id)

    def duplicate_combatant_in_table_n_times(self,row,num_copies):
        combatant_id = self.fetch_combatant_id(row)
        self.undo_manager.do(DuplicateCombatantNTimesCommand(self.comb_manager,combatant_id,num_copies))
        #self.comb_manager.duplicate_combatant_n_times(combatant_id,num_copies)

    def remove_combatant_from_table(self,row,selected_indices):
        # We check if the user has selected multiple rows, and if so we remove those
        if selected_indices:
            cid_list = []
            for index in selected_indices:
                row = index.row()
                cid_list.append(self.fetch_combatant_id(row))
            self.undo_manager.do(DeleteMultipleCombatantsCommand(self.comb_manager,cid_list))
        else:
            combatant_id = self.fetch_combatant_id(row)
            self.undo_manager.do(DeleteCombatantCommand(self.comb_manager,combatant_id))
        #self.comb_manager.remove_combatant_by_id(combatant_id)
        #self.table.removeRow(row)

    #def remove_combatant_from_table(self,row):
        #combatant_id = self.fetch_combatant_id(row)
        #self.comb_manager.remove_combatant_by_id(combatant_id)
        #self.table.removeRow(row)


    def update_combatant_row(self, row: int, combatant: Combatant):
        """
        Update all cells in table for a specific row from the combatant object.
        This avoids searching by name and prevents NoneType errors
        """
        # if not self.table.item(row, self.col_index["Name"]):
        #     self.table.setItem(row,self.col_index["Name"],QTableWidgetItem())
        # if not self.table.item(row,self.col_index["Initiative"]):
        #     self.table.setItem(row, self.col_index["Initiative"], QTableWidgetItem())
        # if not self.table.item(row, self.col_index["AC"]):
        #     self.table.setItem(row,self.col_index["AC"],QTableWidgetItem())
        # if not self.table.item(row, self.col_index["Damage"]):
        #     self.table.setItem(row, self.col_index["Damage"], QTableWidgetItem())
        # if not self.table.item(row, self.col_index["HP"]):
        #     self.table.setItem(row, self.col_index["HP"], QTableWidgetItem())
        # if not self.table.item(row, self.col_index["Status"]):
        #     self.table.setItem(row, self.col_index["Status"], QTableWidgetItem())
        # if not self.table.item(row, self.col_index["Conditions"]):
        #     self.table.setItem(row, self.col_index["Conditions"], QTableWidgetItem())

        name_item = self.get_item(row, self.col_index["Name"])
        initiative_item = self.get_item(row,self.col_index["Initiative"])
        ac_item = self.get_item(row,self.col_index["AC"])
        damage_item = self.get_item(row,self.col_index["Damage"])
        hp_item = self.get_item(row,self.col_index["HP"])
        conditions_item = self.get_item(row,self.col_index["Conditions"])
        status_item = self.get_item(row,self.col_index["Status"])

        name_item.setText(combatant.name)
        name_item.setData(Qt.UserRole, combatant.id)

        initiative = format_initiative(combatant.initiative)
        initiative_item.setText(initiative)
        ac_item.setText(str(combatant.ac))
        damage_item.setText(str(combatant.damage_taken))
        hp_item.setText(str(combatant.hp_total))
        status_item.setText(str(combatant.status))

        conditions_item.setFlags(Qt.ItemIsSelectable | Qt.ItemIsEnabled)
        conditions_string = format_conditions(combatant)
        conditions_item.setText(str(conditions_string))

        # self.table.item(row,self.col_index["Name"]).setText(combatant.name)
        # self.table.item(row, self.col_index["Name"]).setData(Qt.UserRole, combatant.id)
        # initiative = format_initiative(combatant.initiative)
        # self.table.item(row,self.col_index["Initiative"]).setText(initiative)
        # self.table.item(row,self.col_index["AC"]).setText(str(combatant.ac))
        # self.table.item(row,self.col_index["Damage"]).setText(str(combatant.damage_taken))
        # self.table.item(row,self.col_index["HP"]).setText(str(combatant.hp_total))
        # self.table.item(row,self.col_index["Status"]).setText(str(combatant.status))
        # conditions_string = format_conditions(combatant)
        # item = self.table.item(row,self.col_index["Conditions"]).setText(str(conditions_string))
        # item.setFlags(Qt.ItemIsSelectable | Qt.ItemIsEnabled)

        self.update_row_color(row)

    #This method is set up to ensure a cell is there to be edited
    def get_item(self, row, col):
        item = self.table.item(row, col)
        if item is None:
            item = QTableWidgetItem()
            self.table.setItem(row, col, item)
        return item

    def refresh_table(self):
        """This method is an alternative to the sort method of the main window.
        While that one rebuilds the entire table, this refreshes each row (excluding checkbox columns)"""
        row_count = self.table.rowCount()
        for row in range(row_count):
            combatant_id = self.fetch_combatant_id(row)
            combatant = self.comb_manager.get_combatant_by_id(combatant_id)
            self.update_combatant_row(row,combatant)

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

    def style_headers(self):
        if self.dark_mode:
            group_colors = column_coloring_dark
        else:
            group_colors = column_coloring_light

        for group, columns in self.column_groups.items():
            color = group_colors[group]
            for col_name in columns:
                if col_name not in self.col_index:
                    continue
                col = self.col_index[col_name]
                item = self.table.horizontalHeaderItem(col)
                if item:
                    item.setBackground(QColor(color))

                item.setForeground(QColor("#ffffff" if self.dark_mode else "#000000"))

                item.setFont(QFont())

    def rebuild_columns_index(self):
        ordered_columns = self.ordered_columns()
        self.col_index = {name: i for i, name in enumerate(ordered_columns)}

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

    def fetch_combatant_id(self,row):
        name_item = self.table.item(row,0)
        if not name_item:
            return
        #Fetching the combatant id from the table
        combatant_id = name_item.data(Qt.UserRole)
        return combatant_id



    def update_row_color(self, row):
        combatant_id = self.fetch_combatant_id(row)
        combatant = self.comb_manager.get_combatant_by_id(combatant_id)
        hp_left = combatant.hp_remaining

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

    def ordered_columns(self):
        return sorted(
            self.active_columns,
            key=lambda name: self.column_priority[name]
        )



    def draw_combatant_spell_slots(self,clicked_row,combatant_id):
        #First, we ensure there is actually a spell slot column
        self.ensure_spell_slots_column()

        # Then we render the spell slots based on the combat manager
        combatant = self.comb_manager.get_combatant_by_id(combatant_id)
        spell_slots = spell_slots_to_list(combatant.spell_slot_dict)
        col = self.col_index["Spell Slots"]
        self.set_ability_widget(clicked_row, col, combatant_id, spell_slots, True)

    def draw_combatant_abilities(self,clicked_row,combatant_id):
        # Then we ensure there is actually a spell slot column
        self.ensure_abilities_column()

        # Now we render the abilities based on the data in the combat manager
        combatant = self.comb_manager.get_combatant_by_id(combatant_id)
        abilities = sorted(abilities_to_list(combatant.ability_dict))
        col = self.col_index["Abilities"]
        self.set_ability_widget(clicked_row, col, combatant_id, abilities)



    #    ---------------------------------------------------
    def get_insert_position(self, column_name):
        priority = self.column_priority[column_name]

        for i, name in enumerate(self.ordered_columns()):
            if self.column_priority[name] > priority:
                return i

        return len(self.active_columns)