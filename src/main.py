from PySide6.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel
from PySide6.QtCore import QSize
from PySide6.QtGui import QPixmap
import sys

import utils, instances, auth, mods

class Cesena(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Cesena")
        self.resize(QSize(1366, 768))

        self.setWindowIcon(QPixmap('assets/logo.png'))

        self.main_widget = QWidget()
        self.main_layout = QVBoxLayout()
        self.main_widget.setLayout(self.main_layout)

        self.info_layout = QHBoxLayout()
        self.item_layout = QHBoxLayout()

        self.main_layout.addLayout(self.info_layout)
        self.main_layout.addLayout(self.item_layout)

        self.ITEMS = [
            { "name": "Instances", "item": instances.InstanceManager },
            { "name": "Accounts", "item": auth.AuthManager },
            { "name": "Mods", "item": mods.ModManager },
        ]

        for item in self.ITEMS:
            label = QLabel(item['name'])
            label.setStyleSheet('font-size: 14pt;')
            inst = item['item']()
            item['inst'] = inst

            self.info_layout.addWidget(label)
            self.item_layout.addWidget(inst)

        self.setCentralWidget(self.main_widget)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    # app.setDesktopFileName("com.uukelele.cesena")
    window = Cesena()
    window.show()
    sys.exit(app.exec())