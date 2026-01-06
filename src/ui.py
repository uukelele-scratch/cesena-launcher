from PySide6.QtWidgets import (
    QFrame,
    QSizePolicy,
    QListWidget,
    QAbstractItemView,
    QListWidgetItem,
    QHBoxLayout,
    QVBoxLayout,
    QLabel,
    QPushButton,
    QWidget,
)
from PySide6.QtCore import Qt, Signal, QRect
from PySide6.QtGui import QDrag, QPixmap, QImage, QPainter, QFontMetrics
import requests

class OverflowEllipsisLabel(QLabel):
    def __init__(self, text="", parent=None):
        super().__init__(text, parent)
        self.full_text = text
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
        self.setToolTip(text)

    def setText(self, text):
        self.full_text = text
        self.setToolTip(text)
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        metrics = QFontMetrics(self.font())
        elided = metrics.elidedText(self.full_text, Qt.ElideRight, self.width())
        painter.drawText(self.rect(), self.alignment(), elided)

class Card(QFrame):
    clicked = Signal()

    def __init__(self, uid, text, description=None, icon_url=None, icon_path=None, is_selected=False, show_delete=False, delete_cb=None):
        super().__init__()
        self.uid = uid
        self.setObjectName("CardFrame")

        self.setFrameShape(QFrame.NoFrame)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)

        self.setStyleSheet(selected_style if is_selected else default_style)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(10)

        self.icon_lbl = QLabel()
        self.icon_lbl.setFixedSize(42, 42)
        self.icon_lbl.setStyleSheet("background-color: transparent; border: none;")
        self.icon_lbl.setScaledContents(True)
        if icon_url or icon_path:
            layout.addWidget(self.icon_lbl)
            self.load_icon(icon_url, icon_path)
        else:
            self.icon_lbl.hide()

        text_layout = QVBoxLayout()
        text_layout.setSpacing(2)

        self.title_label = QLabel(text)
        self.title_label.setStyleSheet("font-weight: bold; font-size: 14px;")
        text_layout.addWidget(self.title_label)

        if description:
            self.desc_lbl = OverflowEllipsisLabel(description)
            self.desc_lbl.setObjectName("desc")
            self.desc_lbl.setStyleSheet("font-size: 12px;")
            text_layout.addWidget(self.desc_lbl)

        layout.addLayout(text_layout)

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

    def load_icon(self, url=None, path=None):
        if path:
            pixmap = QPixmap(str(path))
            if not pixmap.isNull():
                self.icon_lbl.setPixmap(pixmap)
                return

        if url:
            import utils 
            worker = utils.Worker(self._download_image, url)
            worker.signals.result.connect(self._set_icon_pixmap)
            utils.pool.start(worker)

    def _download_image(self, url):
        try:
            r = requests.get(url, timeout=3)
            r.raise_for_status()
            img = QImage()
            img.loadFromData(r.content)
            return QPixmap.fromImage(img)
        except:
            return None

    def _set_icon_pixmap(self, pixmap):
        if pixmap and not pixmap.isNull():
            self.icon_lbl.setPixmap(pixmap)
            self.icon_lbl.show()

default_style = """
    QFrame { background-color: #f0f0f0; border-radius: 5px; }
    QFrame:hover { background-color: #e0e0e0; }
    QLabel { background: transparent; }
    QLabel#desc { color: #555555; }
"""

selected_style = """
    QFrame { background-color: #0d6efd; border-radius: 5px; color: white; }
    QFrame:hover { background-color: #0b5ed7; }
    QLabel { background: transparent; color: white; }
    QLabel#desc { color: #e0e0e0; }
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

    def addCard(self, uid, text, description=None, icon_url=None, icon_path=None, is_selected=False, show_delete=False):
        card = Card(
            uid=uid, 
            text=text, 
            description=description,
            icon_url=icon_url,
            icon_path=icon_path,
            is_selected=is_selected, 
            show_delete=show_delete,
            delete_cb=self.on_delete.emit
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