from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QScrollArea,
    QFrame,
    QPushButton,
    QLineEdit,
    QMessageBox,
)
from PySide6.QtCore import Qt
from dataclasses import dataclass

import utils, ui

@dataclass
class Account:
    username: str

class AuthManager(QWidget):
    def __init__(self):
        super().__init__()

        self.accounts: list[Account] = []
        self.current_account: str = None

        self.main_layout = QVBoxLayout(self)
        self.add_layout = QHBoxLayout()
        
        self.username_label = QLabel("Username: ")
        self.username_input = QLineEdit()
        
        self.add_btn = QPushButton("Add Account")
        self.add_btn.clicked.connect(self.add_account)

        self.add_layout.addWidget(self.username_label)
        self.add_layout.addWidget(self.username_input)
        self.add_layout.addWidget(self.add_btn)
        
        self.main_layout.addLayout(self.add_layout)

        self.info_label = QLabel()
        self.main_layout.addWidget(self.info_label)

        self.scrolla = ui.List()
        self.scrolla.on_selection.connect(self.handle_select)
        self.scrolla.on_delete.connect(self.handle_delete)
        self.scrolla.on_reorder.connect(self.handle_reorder)
        self.main_layout.addWidget(self.scrolla)

        self.load_accounts()

    def load_accounts(self):
        auth = utils.get_accounts()
        self.current_account = auth.get("selected")
        self.accounts = [
            Account(
                username = acc["username"],
            )
            for acc in auth.get("accounts", [])
        ]
        self.update_accounts()

    def update_accounts(self):
        self.scrolla.clear()

        if not self.accounts:
            self.info_label.setText("No accounts found. Consider adding one.")
            return
        else: self.info_label.setText("")

        for inst in self.accounts:
            self.scrolla.addCard(
                uid=inst.username,
                text=inst.username,
                is_selected=(inst.username == self.current_account),
                show_delete=True,
            )

    def save_accounts(self):
        self.accounts = []
        
        for i in range(self.scrolla.count()):
            item = self.scrolla.item(i)
            widget = self.scrolla.itemWidget(item)
            
            name = widget.username
            self.accounts.append(Account(name))
            
        self.save()

    def save(self):
        data = {
            "selected": self.current_account,
            "accounts": [{"username": acc.username} for acc in self.accounts]
        }
        utils.save_accounts(data)

    def add_account(self):
        name = self.username_input.text().strip()
        if not name: return

        if any(acc.username == name for acc in self.accounts):
            QMessageBox.warning(self, "Error", "Account already exists!")
            return
        
        new_acc = Account(username=name)
        self.accounts.append(new_acc)

        if len(self.accounts) == 1:
            self.current_account = name

        self.username_input.clear()
        self.save()
        self.update_accounts()

    def handle_reorder(self, new_order_ids):
        self.accounts = [Account(uid) for uid in new_order_ids]
        self.save()

    def handle_select(self, username):
        self.current_account = username
        self.save()
        self.update_accounts()

    def handle_delete(self, username):
        self.accounts = [a for a in self.accounts if a.username != username]
        
        if self.current_account == username:
            self.current_account = self.accounts[0].username if self.accounts else None
            
        self.save()
        self.update_accounts()