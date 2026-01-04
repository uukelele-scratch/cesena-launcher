from PySide6.QtWidgets import (
    QFrame,
    QSizePolicy,
)
from PySide6.QtCore import Qt, Signal

class Card(QFrame):
    clicked = Signal()

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.setFrameShape(QFrame.NoFrame)

        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.clicked.emit()

default_style = """
    QFrame { background-color: #f0f0f0; border-radius: 5px; }
    QFrame:hover { background-color: #e0e0e0; }
    QLabel { background: transparent; }
"""

selected_style = """
    QFrame { background-color: #0d6efd; border-radius: 5px; color: white; }
    QFrame:hover { background-color: #0b5ed7; }
    QLabel { background: transparent; color: white; }
"""