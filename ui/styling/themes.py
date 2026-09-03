from PySide6.QtWidgets import QApplication

DARK_THEME = """
QWidget {
    background-color: #2b2b2b;
    color: #f0f0f0;
}

/* default button */
QPushButton {
    background-color: #3c3c3c;
    color: #f0f0f0;
    border: 1px solid #777;
}

/* hover */
QPushButton:hover {
    background-color: #4a4a4a;
}

/* pressed */
QPushButton:pressed {
    background-color: #2f2f2f;
}

QLineEdit, QSpinBox, QTableWidget, QListWidget {
    background-color: #3c3c3c;
    color: #f0f0f0;
    selection-background-color: #555555;
}

QTableWidget::item:focus {
    outline: none;
}

QHeaderView {
    background-color: #3c3c3c;
}

QHeaderView::section {
    background-color: #3a3f4b; /* dark slate */
    color:white;
    font-weight: 600;
    padding: 4px;
    border: none;
}

QMenu {
    background-color: #2b2b2b;
    color: #f0f0f0;
}

QMenu::item:disabled {
    color: #6f6f6f;
}

QCheckBox[checkbox_type="dialogue"]::indicator {
    width: 14px;
    height: 14px;
    border: 1px solid #aaa;
    background-color: #2b2b2b;
}

QCheckBox[checkbox_type="dialogue"]::indicator:checked {
    background-color: #2b2b2b;
    border: 1px solid #aaa;
    image: url(assets/icons/check-mark-dark.svg);
}

QCheckBox[resource_type="ability"]::indicator {
    width: 14px;
    height: 14px;
    border: 1px solid #aaa;
    background-color: #2b2b2b;
}

QCheckBox[resource_type="ability"]::indicator:checked {
    background-color: #B82A27;  
    border: 1px solid #B82A27;
}


QCheckBox[resource_type="spell"]::indicator {
    width: 14px;
    height: 14px;
    border: 1px solid #aaa;
    background-color: #2b2b2b;
}

QCheckBox[resource_type="spell"]::indicator:checked {
    background-color: #6ea8fe;  
    border: 1px solid #6ea8fe;
}
"""

LIGHT_THEME = """
QWidget {
    background-color: #D9D9D9;
    color: #000000;
}

QPushButton {
        background-color: #ffffff;
        font-weight: 600;
        border-radius: 6px;
        border: 1px solid #777;
}

QPushButton:hover {
    background-color: rgba(0, 0, 0, 0.08);
}

QPushButton:pressed {
    background-color: rgba(0, 0, 0, 0.15);
}

QLineEdit, QSpinBox, QTableWidget, QListWidget {
    background-color: #ffffff;
    color: #000000;
}


QHeaderView {
    background-color: #ffffff;
}

QHeaderView::section   {
    background-color:  #FFF2C7;  /*light yellow*/
    color:black;
    font-weight: 600;
    padding: 4 px;
    }

QTableWidget::item:focus {
    outline: none;
}

QMenu {
    background-color: #ffffff;
    color: #000000;
}

QMenu::item:disabled {
    color: #a0a0a0;
}

QCheckBox[checkbox_type="dialogue"]::indicator {
    width: 14px;
    height: 14px;
    border: 1px solid #555;
    background-color: #ffffff;
}

QCheckBox[checkbox_type="dialogue"]::indicator:checked {
    background-color: #ffffff;
    border: 1px solid #555;
    image: url(assets/icons/check-mark-light.svg);
}

QCheckBox[resource_type="ability"]::indicator {
    width: 14px;
    height: 14px;
    border: 1px solid #555;
    background-color: #ffffff;
}

QCheckBox[resource_type="ability"]::indicator:checked {
    background-color: #B82A27;  /* Testing out, original was 4a90e2 */
    border: 1px solid #B82A27;
}

QCheckBox[resource_type="spell"]::indicator {
    width: 14px;
    height: 14px;
    border: 1px solid #555;
    background-color: #ffffff;
}

QCheckBox[resource_type="spell"]::indicator:checked {
    background-color: #4a90e2;  
    border: 1px solid #4a90e2;
}

"""

def apply_theme(theme: str):
    app = QApplication.instance()
    app.setStyleSheet(theme)

    # QHeaderView::section
    # {
    #     background - color:  # a84a58;  /* maroon */
    #         color: white;
    # font - weight: 600;
    # padding: 4
    # px;
    #
    # border: none;
    # background - image: linear - gradient(to
    # right,
    # rgba(0, 0, 0, 0.15),
    # rgba(0, 0, 0, 0.15)
    # );
    # background - position: right;
    # background - repeat: no - repeat;
    # background - size: 1
    # px
    # 100 %;
    # }

    # QHeaderView::section
    # {
    #     background - color:  # 3a3f4b;  /* dark slate */
    #         color:  # f0f0f0;
    # font - weight: 600;
    # padding: 4
    # px;
    # border: none;
    # }