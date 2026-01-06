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
import utils, launcher, ui

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

        self.info_label = QLabel()
        self.main_layout.addWidget(self.info_label)

        self.scrolla = ui.List()
        self.scrolla.on_selection.connect(self.handle_select)
        self.scrolla.on_reorder.connect(self.handle_reorder)
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
        self.scrolla.clear()

        if not self.instances:
            self.info_label.setText("No local versions found. Consider adding one.")
            return
        else: self.info_label.setText("")
        
        if not self.selected_inst_path: self.selected_inst_path = self.instances[0].path

        for inst in self.instances:
            is_selected = (inst.path == self.selected_inst_path)
            
            if is_selected:
                self.play_btn.setText(f"Play ({utils.format_vid(inst.name)})")

            self.scrolla.addCard(
                uid=inst.path,
                text=utils.format_vid(inst.name),
                is_selected=is_selected,
                show_delete=False 
            )

    def handle_play(self):
        version = [v for v in self.instances if v.path == self.selected_inst_path][0].name

        self.window().hide()
        
        print(f"PLAYING: {version}")

        worker = utils.Worker(launcher.launch_mc)(version)

        worker.signals.result.connect(self.launch_success)
        worker.signals.error.connect(self.onerror)

        utils.pool.start(worker)

    def handle_reorder(self, new_order_paths):
        map = {inst.path: inst for inst in self.instances}
        self.instances = [map[path] for path in new_order_paths if path in map]
        
        utils.save_instance_order([inst.name for inst in self.instances])

    def handle_select(self, path):
        self.selected_inst_path = path
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

