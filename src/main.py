from PySide6.QtWidgets import QApplication, QMainWindow, QWidget, QHBoxLayout
from PySide6.QtCore import QSize
import sys

import utils, instances, auth

class Cesena(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Cesena")
        self.resize(QSize(1366, 768))

        self.instance_manager = instances.InstanceManager()
        self.auth_manager = auth.AuthManager()

        self.main_widget = QWidget()
        self.main_layout = QHBoxLayout()
        self.main_widget.setLayout(self.main_layout)

        self.main_layout.addWidget(self.instance_manager)
        self.main_layout.addWidget(self.auth_manager)

        self.setCentralWidget(self.main_widget)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    # app.setDesktopFileName("com.uukelele.cesena")
    window = Cesena()
    window.show()
    sys.exit(app.exec())