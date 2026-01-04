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