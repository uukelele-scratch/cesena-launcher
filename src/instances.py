from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QScrollArea,
    QFrame,
    QPushButton,
    QMessageBox,
    QSizePolicy,
)
from PySide6.QtCore import Qt
from dataclasses import dataclass
import utils, launcher
from card import Card, default_style, selected_style

@dataclass
class Instance:
    name: str
    path: str

class InstanceManager(QWidget):
    def __init__(self):
        super().__init__()
        
        self.instances: list[Instance] = []
        self.selected_inst_path: str = None

        self.proc: launcher.sp.Popen = None

        self.main_layout = QVBoxLayout(self)

        self.scrolla = QScrollArea()
        self.scrolla.setWidgetResizable(True)
        self.scrolla.setFrameShape(QFrame.NoFrame)

        self.scroll_content = QWidget()
        self.instance_layout = QVBoxLayout(self.scroll_content)
        self.instance_layout.setAlignment(Qt.AlignTop)

        self.scrolla.setWidget(self.scroll_content)
        
        self.main_layout.addWidget(self.scrolla)

        self.play_btn = QPushButton("Play")
        self.play_btn.setCursor(Qt.PointingHandCursor)
        self.play_btn.setStyleSheet("background-color: #4CAF50; color: white; padding: 5px 15px; border: none; border-radius: 5px;")
        self.play_btn.clicked.connect(self.handle_play)
        self.main_layout.addWidget(self.play_btn)

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

    def update_instances(self):
        while self.instance_layout.count():
            item = self.instance_layout.takeAt(0)
            widget = item.widget()
            if widget: widget.deleteLater()

        if not self.instances:
            self.instance_layout.addWidget(QLabel("No local versions found. Consider adding one."))
            return
        
        if not self.selected_inst_path: self.selected_inst_path = self.instances[0].path

        for inst in self.instances:
            is_selected = self.selected_inst_path == inst.path

            if is_selected: self.play_btn.setText(f"Play ({inst.name})")

            card = Card()
            card.setStyleSheet(default_style)
            if is_selected: card.setStyleSheet(selected_style)
            card.clicked.connect(lambda v=inst.path: self.handle_select(v))
            card.setCursor(Qt.PointingHandCursor)

            box = QHBoxLayout(card)

            label = QLabel(inst.name)
            label.setStyleSheet("font-weight: bold; font-size: 14px;")

            box.addWidget(label)
            box.addStretch()

            card.setLayout(box)
            self.instance_layout.addWidget(card)

    def handle_play(self):
        version = [v for v in self.instances if v.path == self.selected_inst_path][0].name
        print(f"PLAYING: {version}")

        worker = utils.Worker(launcher.launch_mc)(version)

        worker.signals.result.connect(self.launch_success)
        worker.signals.error.connect(self.onerror)

        utils.pool.start(worker)

    def handle_select(self, v):
        self.selected_inst_path = v
        self.update_instances()

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

