from PySide6.QtWidgets import QApplication, QMainWindow, QTabWidget
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

        self.tab_manager = QTabWidget()

        self.tab_manager.addTab(self.instance_manager, 'Instances')
        self.tab_manager.addTab(self.auth_manager, 'Auth')

        self.setCentralWidget(self.tab_manager)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    # app.setDesktopFileName("com.uukelele.cesena")
    window = Cesena()
    window.show()
    sys.exit(app.exec())