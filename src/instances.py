from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QScrollArea,
    QFrame,
    QPushButton,
    QMessageBox,
)
from PySide6.QtCore import Qt
from dataclasses import dataclass
import utils, launcher

@dataclass
class Instance:
    name: str
    path: str

class InstanceManager(QWidget):
    def __init__(self):
        super().__init__()
        self.instances: list[Instance] = []
        self.proc: launcher.sp.Popen = None

        self.main_layout = QVBoxLayout(self)

        self.info_label = QLabel()
        self.main_layout.addWidget(self.info_label)

        self.scrolla = QScrollArea()
        self.scrolla.setWidgetResizable(True)
        self.scrolla.setFrameShape(QFrame.NoFrame)

        self.scroll_content = QWidget()
        self.instance_layout = QVBoxLayout(self.scroll_content)
        self.instance_layout.setAlignment(Qt.AlignTop)

        self.scrolla.setWidget(self.scroll_content)
        
        self.main_layout.addWidget(self.scrolla)

        self.load_instances()

    
    def load_instances(self):
        self.instances = [
            Instance(
                name = v.name,
                path = str(v),
            )
            for v in utils.get_local_versions()
        ]
        self.update_instances()
        self.info_label.setText(f'Selected Account: {utils.get_selected_username()}')

    def update_instances(self):
        while self.instance_layout.count():
            item = self.instance_layout.takeAt(0)
            widget = item.widget()
            if widget: widget.deleteLater()

        if not self.instances:
            self.instance_layout.addWidget(QLabel("No local versions found. Consider adding one."))

        for inst in self.instances:
            card = QWidget()
            card.setStyleSheet("background-color: #f0f0f0; border-radius: 5px;")

            box = QHBoxLayout(card)

            label = QLabel(inst.name)
            label.setStyleSheet("font-weight: bold; font-size: 14px;")

            play_btn = QPushButton("Play")
            play_btn.setCursor(Qt.PointingHandCursor)
            play_btn.setStyleSheet("background-color: #4CAF50; color: white; padding: 5px 15px; border: none;")
            play_btn.clicked.connect(lambda checked, v=inst.name: self.handle_play(v))

            box.addWidget(label)
            box.addStretch()
            box.addWidget(play_btn)

            card.setLayout(box)
            self.instance_layout.addWidget(card)

    def handle_play(self, version):
        print(f"PLAYING: {version}")

        worker = utils.Worker(launcher.launch_mc)(version)

        worker.signals.result.connect(self.launch_success)
        worker.signals.error.connect(self.onerror)

        utils.pool.start(worker)

    def launch_success(self, proc):
        self.proc = proc
        
        self.window().hide()
        self.setEnabled(True)

        worker = utils.Worker(self.proc.communicate)
        worker.signals.result.connect(self.mc_closed)

        utils.pool.start(worker)

    def mc_closed(self, output):
        stdout, stderr = output
        self.window().show()
        if self.proc.returncode and self.proc.returncode != 0:
            QMessageBox.critical(self, "Minecraft Crashed", (stdout+stderr)[-1000:])

    def onerror(self, *args):
        self.setEnabled(True)
        print("Error:", *args)
        if len(args) >= 1 and isinstance(args[0], tuple) and len(args[0]) >= 3:
            QMessageBox.critical(self, "Error", f"Error:\n{args[0][1]}")

