from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel, 
    QPushButton,
    QLineEdit,
    QSplitter,
    QMessageBox,
)
from PySide6.QtCore import Qt

import utils, modrinth, ui

class ModManager(QWidget):
    def __init__(self):
        super().__init__()

        self.results = []
        
        self.main_layout = QVBoxLayout(self)

        self.search_layout = QHBoxLayout()
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Search Modrinth...")
        self.search_input.returnPressed.connect(self.search)
        
        self.search_btn = QPushButton("Search")
        self.search_btn.clicked.connect(self.search)
        
        self.search_layout.addWidget(self.search_input)
        self.search_layout.addWidget(self.search_btn)
        self.main_layout.addLayout(self.search_layout)

        splitter = QSplitter(Qt.Vertical)

        self.results_widget = QWidget()
        l_layout = QVBoxLayout(self.results_widget)
        l_layout.addWidget(QLabel("Search Results"))
        self.search_info_label = QLabel("")
        l_layout.addWidget(self.search_info_label)
        self.results_list = ui.List()
        self.results_list.on_selection.connect(self.add_mod_from_search)
        l_layout.addWidget(self.results_list)

        self.installed_widget = QWidget()
        r_layout = QVBoxLayout(self.installed_widget)
        r_layout.addWidget(QLabel("Enabled Mods"))
        self.installed_list = ui.List()
        self.installed_list.on_delete.connect(self.remove_mod)
        r_layout.addWidget(self.installed_list)

        splitter.addWidget(self.results_widget)
        splitter.addWidget(self.installed_widget)
        splitter.setStretchFactor(0, 1)
        splitter.setStretchFactor(1, 1)

        self.main_layout.addWidget(splitter)
        
        self.refresh_installed_list()

    def search(self):
        query = self.search_input.text().strip()
        if not query: return
        
        self.results_list.clear()
        self.search_btn.setText("Searching...")
        self.search_btn.setEnabled(False)
        
        worker = utils.Worker(modrinth.search_mods)(query)
        worker.signals.result.connect(self.on_search_results)
        utils.pool.start(worker)

    def on_search_results(self, results):
        self.search_btn.setText("Search")
        self.search_btn.setEnabled(True)
        self.results_list.clear()

        self.results = results
        
        if not results:
            self.search_info_label.setText("No results.")
            return
        else: self.search_info_label.setText("")

        for mod in results:
            self.results_list.addCard(
                uid=mod["project_id"], 
                text=mod["title"],
                description=f'{utils.short_num(mod.get("downloads", 0))} downloads • ' + mod.get('description', 'No description provided.'),
                icon_url=mod.get('icon_url'),
                is_selected=False,
                show_delete=False,
            )

    def add_mod_from_search(self, id):
        mod = [m for m in self.results if m['project_id'] == id][0]
        utils.add_mod(mod)
        self.refresh_installed_list()
        QMessageBox.information(self, "Installed Mod", f"Installed mod ({mod['title']})")

    def remove_mod(self, id):
        mod = [m for m in utils.get_mods_config().get("enabled_mods", []) if m['project_id'] == id][0]
        utils.rm_mod(mod)
        self.refresh_installed_list()

    def refresh_installed_list(self):
        self.installed_list.clear()
        mods = utils.get_mods_config().get("enabled_mods", [])
        for mod in mods:
            self.installed_list.addCard(
                uid=mod['project_id'],
                text=mod['title'],
                description=mod.get('description', 'No description provided.'),
                icon_url=mod.get('icon_url'),
                is_selected=False,
                show_delete=True,
            )