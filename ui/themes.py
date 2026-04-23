from PySide6.QtWidgets import QApplication

DARK_THEME = """
QWidget {
    background-color: #2b2b2b;
    color: #f0f0f0;
}

QLineEdit, QSpinBox, QTableWidget {
    background-color: #3c3c3c;
    color: #f0f0f0;
    selection-background-color: #555555;
}

QHeaderView::section {
    background-color: #444444;
    color: #f0f0f0;
}

QMenu {
    background-color: #2b2b2b;
    color: #f0f0f0;
}
"""

LIGHT_THEME = ""

def apply_theme(theme: str):
    app = QApplication.instance()
    app.setStyleSheet(theme)