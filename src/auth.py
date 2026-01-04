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

import utils
from card import Card

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

        self.scrolla = QScrollArea()
        self.scrolla.setWidgetResizable(True)
        self.scrolla.setFrameShape(QFrame.NoFrame)

        self.scroll_content = QWidget()
        self.accounts_layout = QVBoxLayout(self.scroll_content)
        self.accounts_layout.setAlignment(Qt.AlignTop)

        self.scrolla.setWidget(self.scroll_content)
        
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
        while self.accounts_layout.count():
            item = self.accounts_layout.takeAt(0)
            widget = item.widget()
            if widget: widget.deleteLater()

        if not self.accounts:
            self.accounts_layout.addWidget(QLabel("No accounts found. Consider adding one."))

        for inst in self.accounts:
            is_selected = (inst.username == self.current_account)

            card = Card()

            card.setStyleSheet("background-color: #f0f0f0; border-radius: 5px;")
            if is_selected: card.setStyleSheet("background-color: #0d6efd; border-radius: 5px; color: white;")
            card.clicked.connect(lambda a=inst.username: self.handle_select(a))
            card.setCursor(Qt.PointingHandCursor)

            box = QHBoxLayout(card)

            label = QLabel(inst.username)
            label.setStyleSheet("font-weight: bold; font-size: 14px;")

            delete_btn = QPushButton("Delete")
            delete_btn.setCursor(Qt.PointingHandCursor)
            delete_btn.setStyleSheet("background-color: #ee1313; color: white; padding: 5px 15px; border: none;")
            delete_btn.clicked.connect(lambda checked, a=inst.username: self.handle_delete(a))

            box.addWidget(label)
            box.addStretch()
            box.addWidget(delete_btn)

            card.setLayout(box)
            self.accounts_layout.addWidget(card)

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

    def handle_select(self, username):
        self.current_account = username
        self.save()
        self.update_accounts()

    def handle_delete(self, username):
        self.accounts = [acc for acc in self.accounts if acc.username != username]
    
        if self.current_account == username:
            if len(self.accounts) == 0:
                self.current_account = None
            else:
                self.current_account = self.accounts[0].username
     
        self.save()
        self.update_accounts()