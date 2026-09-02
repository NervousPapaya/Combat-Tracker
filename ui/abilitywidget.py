from math import ceil
from PySide6.QtCore import Qt
from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, QCheckBox, QSizePolicy)
from PySide6.QtGui import QColor


class AbilityTrackerWidget(QWidget):
    """This class handles adding checkmark.
    abilites_with_count expects a list of tuples [(ability_name,number_of,spell_level or None),... ].
    is_spells = True if handling spell slots.
    Each ability gets a label + horizontal checkboxes for uses.
    The intended use is primarily for spell slots, but it can be used for other stuff as well.
    """
    def __init__(self,manager,combatant_id,abilities_with_count, is_spells=False):
        super().__init__()

        self.manager = manager
        self.combatant_id = combatant_id
        self.is_spells = is_spells

        layout = QVBoxLayout(self)
        #We set margins between the cell widget and the outer edges of the cell at 2 pixes left, top, right, bottom
        layout.setContentsMargins(2, 2, 2, 2)
        #We set the spacing between the content of the cell
        layout.setSpacing(2)
        self.setStyleSheet("background: transparent;")


        #Initializing a list of hboxes which will act as our rows
        num_of_rows = ceil(len(abilities_with_count)/2)
        hboxes = []
        for _ in range(num_of_rows):
            h = QHBoxLayout()
            h.setSpacing(15)
            hboxes.append(h)

        column_counter = 0
        row_counter = 0

        for ability_name, total_count, spell_level in abilities_with_count:
            #We make a vertical box for storing the ability name and the checkboxes
            ability_widget = QWidget()
            ability_widget.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Fixed)
            vbox = QVBoxLayout(ability_widget)
            vbox.setContentsMargins(0, 0, 0, 0)
            vbox.setSpacing(1)

            #We set up the label with font, font size 10pt and left alignment
            label = QLabel(ability_name)
            font = label.font()
            font.setPointSize(10)
            label.setFont(font)
            #We add the label to the vbox
            vbox.addWidget(label, alignment=Qt.AlignmentFlag.AlignLeft)

            #Then we add the boxes horizontally
            box_row = QHBoxLayout()
            box_row.setSpacing(2) #spacing between boxes

            #Then we loop over the number of boxes needed
            for i in range(total_count):
                cb = QCheckBox()
                cb.setMaximumHeight(20)
                # Here we set the font size inside the box which manipulates its size, even though it will not hold text.
                cb_font = cb.font()
                cb_font.setPointSize(9)
                cb.setFont(cb_font)

                #Here we set up properties that allow us to uniquely determine the box.
                cb.setProperty("combatant_id",combatant_id)
                cb.setProperty("resource_name",ability_name)
                cb.setProperty("resource_level", spell_level)

                # Finally we set the resource type
                if spell_level is not None:
                    cb.setProperty("resource_type", "spell")
                else:
                    cb.setProperty("resource_type", "ability")

                #This next part is really only needed for when rebuilding the ui.
                #What it does, is check a box if the corresponding spell slot or ability has been used.
                #We need to handle spells and abilities differently, due to the way they are stored (to be codified later)

                self.initialize_checkbox(cb,ability_name,spell_level,total_count, i)

                #Then we define what the checkbox should do if toggled
                cb.toggled.connect(lambda checked, cb=cb: self.on_ability_box_toggled(cb, checked))

                box_row.addWidget(cb)



            #We add the checkboxes to the vbox
            vbox.addLayout(box_row)
            #Then we add the ability to the hbox corresponding to the row we are on
            hboxes[row_counter].addWidget(ability_widget)
            if column_counter == 1:
                row_counter +=1
            column_counter = (column_counter+1)%2

        for hbox in hboxes:
            row_widget = QWidget()
            row_widget.setLayout(hbox)
            row_widget.setSizePolicy(QSizePolicy.Maximum, QSizePolicy.Minimum)
            layout.addWidget(row_widget, alignment=Qt.AlignmentFlag.AlignHCenter)

        self.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Fixed)

    def initialize_checkbox(self,cb,ability_name,spell_level, total_count, index):
        combatant = self.manager.get_combatant_by_id(self.combatant_id)
        if spell_level is not None:
            # Spell slots used is count - remaining
            used = total_count - combatant.spell_slot_dict[spell_level]
            cb.setChecked(index < used)
        else:
            ability = combatant.ability_dict[ability_name]
            used = ability.max - ability.left
            cb.setChecked(index < used)

    def on_ability_box_toggled(self, cb, checked: bool):

        combatant_id = cb.property("combatant_id")
        resource_type = cb.property("resource_type")

        if resource_type == "spell":
            level = cb.property("resource_level")
            if checked:
                self.manager.use_spell_slot(combatant_id,level)
            else:
                self.manager.regain_spell_slot(combatant_id,level)
        elif resource_type == "ability":
            resource_name = cb.property("resource_name")
            if checked:
                self.manager.use_ability(combatant_id,resource_name)
            else:
                self.manager.regain_ability(combatant_id,resource_name)

    def set_background_color(self, color: QColor):
        """This method takes care of coloring.
        Essentially, it sets the background color of all the widgets contained in the ability widget."""
        self.setStyleSheet(f"QWidget {{ background-color: {color.name(QColor.HexArgb)}; }}")