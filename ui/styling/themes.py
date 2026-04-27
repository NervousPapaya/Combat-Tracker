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

QLineEdit, QSpinBox, QTableWidget {
    background-color: #3c3c3c;
    color: #f0f0f0;
    selection-background-color: #555555;
}

QTableWidget::item {
    border: none;
}

QTableWidget::item:selected {
    background-color: rgba(120, 140, 170, 0.35);
    color: #f0f0f0;
}

QTableWidget::item:focus {
    outline: none;
}

QHeaderView {
    background-color: #3c3c3c;
}

QHeaderView::section {
    background-color: #3a3f4b; /*dark slate*/
    color:white;
    font-weight: 600;
    padding: 4px;
    border: none;
}

QMenu {
    background-color: #2b2b2b;
    color: #f0f0f0;
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

QLineEdit, QSpinBox, QTableWidget {
    background-color: #ffffff;
    color: #000000;
}


QHeaderView {
    background-color: #ffffff;
}

QHeaderView::section   {
    background-color:  #FFF2C7;  /*maroon*/
    color:black;
    font-weight: 600;
    padding: 4 px;
    }


QTableWidget::item:selected {
    background-color: rgba(90, 106, 138, 0.6);
    color: white;
    border: none;
}

QTableWidget::item:focus {
    outline: none;
}

QMenu {
    background-color: #ffffff;
    color: #000000;
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