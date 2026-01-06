from PySide6.QtWidgets import (
    QFrame,
    QSizePolicy,
    QListWidget,
    QAbstractItemView,
    QListWidgetItem,
    QHBoxLayout,
    QLabel,
    QPushButton,
)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QDrag

class Card(QFrame):
    clicked = Signal()

    def __init__(self, uid, text, is_selected=False, show_delete=False, delete_cb=None):
        super().__init__()
        self.uid = uid

        self.setFrameShape(QFrame.NoFrame)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)

        self.setStyleSheet(selected_style if is_selected else default_style)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)

        self.label = QLabel(text)
        self.label.setStyleSheet("font-weight: bold; font-size: 14px;")
        layout.addWidget(self.label)

        layout.addStretch()

        if show_delete:
            btn = QPushButton("Delete")
            btn.setCursor(Qt.PointingHandCursor)
            btn.setStyleSheet("""
                QPushButton { background-color: #ee1313; color: white; border: none; border-radius: 3px; padding: 5px 10px; }
                QPushButton:hover { background-color: #c00; }
            """)

            if delete_cb:
                btn.clicked.connect(lambda: delete_cb(self.uid))
            layout.addWidget(btn)


    def mousePressEvent(self, event):
        event.ignore()

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

class List(QListWidget):
    on_reorder = Signal(list)
    on_selection = Signal(str)
    on_delete = Signal(str)

    def __init__(self):
        super().__init__()
        
        self.setDragEnabled(True)
        self.setAcceptDrops(True)
        self.setDragDropMode(QAbstractItemView.InternalMove)
        
        self.setStyleSheet("""
            QListWidget { background: transparent; border: none; outline: none; }
            QListWidget::item { background: transparent; border: none; }
            QListWidget::item:selected { background: transparent; border: none; }
            QListWidget::item:hover { background: transparent; border: none; }
        """)
        
        self.setVerticalScrollMode(QAbstractItemView.ScrollPerPixel)
        self.setSpacing(5)

        self.itemClicked.connect(self._handle_click)

    def addCard(self, uid, text, is_selected=False, show_delete=False):
        card = Card(
            uid=uid,
            text=text,
            is_selected=is_selected,
            show_delete=show_delete,
            delete_cb=self.on_delete.emit,
        )

        item = QListWidgetItem(self)        
        item.setSizeHint(card.sizeHint())

        item.setData(Qt.UserRole, uid)        

        self.addItem(item)
        self.setItemWidget(item, card)

    def get_order(self):
        order = []
        for i in range(self.count()):
            item = self.item(i)
            order.append(item.data(Qt.UserRole))
        return order
    
    def _handle_click(self, item):
        uid = item.data(Qt.UserRole)
        self.on_selection.emit(uid)

    def dropEvent(self, event):
        super().dropEvent(event)
        self.on_reorder.emit(self.get_order())

    def startDrag(self, supportedActions):
        item = self.currentItem()
        widget = self.itemWidget(item)
        if not widget: return super().startDrag(supportedActions)

        pixmap = widget.grab()
        drag = QDrag(self)
        drag.setMimeData(self.model().mimeData(self.selectedIndexes()))
        drag.setPixmap(pixmap)
        drag.setHotSpot(pixmap.rect().center())
        drag.exec(supportedActions)