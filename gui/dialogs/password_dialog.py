"""
Password Dialog

This module provides a password input dialog for the Card Database Manager.
"""

from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QLabel, QLineEdit, QPushButton, 
    QHBoxLayout, QMessageBox
)
from PyQt6.QtCore import Qt

class PasswordDialog(QDialog):
    """A dialog for entering a password."""
    
    def __init__(self, parent=None, new_db=False):
        """
        Initialize the password dialog.
        
        Args:
            parent: The parent widget
            new_db: Whether this is for a new database (shows confirm field)
        """
        super().__init__(parent)
        self.password = None
        self.new_db = new_db
        self.init_ui()
    
    def init_ui(self):
        """Initialize the user interface."""
        self.setWindowTitle("Enter Password")
        self.setMinimumWidth(350)
        
        layout = QVBoxLayout(self)
        
        # Password field
        self.password_label = QLabel("Password:")
        self.password_input = QLineEdit()
        self.password_input.setEchoMode(QLineEdit.EchoMode.Password)
        
        # Confirm password field (only for new databases)
        self.confirm_label = QLabel("Confirm Password:")
        self.confirm_input = QLineEdit()
        self.confirm_input.setEchoMode(QLineEdit.EchoMode.Password)
        
        # Buttons
        button_box = QHBoxLayout()
        self.ok_button = QPushButton("OK")
        self.cancel_button = QPushButton("Cancel")
        
        button_box.addWidget(self.ok_button)
        button_box.addWidget(self.cancel_button)
        
        # Add widgets to layout
        layout.addWidget(self.password_label)
        layout.addWidget(self.password_input)
        
        if self.new_db:
            layout.addWidget(self.confirm_label)
            layout.addWidget(self.confirm_input)
        
        layout.addLayout(button_box)
        
        # Connect signals
        self.ok_button.clicked.connect(self.accept)
        self.cancel_button.clicked.connect(self.reject)
        
        # Set focus to password field
        self.password_input.setFocus()
    
    def get_password(self):
        """
        Get the entered password.
        
        Returns:
            str: The entered password, or None if cancelled
        """
        if self.exec() == QDialog.DialogCode.Accepted:
            password = self.password_input.text()
            
            # Validate password for new databases
            if self.new_db:
                confirm = self.confirm_input.text()
                if password != confirm:
                    QMessageBox.warning(self, "Error", "Passwords do not match")
                    return None
                if not password:
                    QMessageBox.warning(self, "Error", "Password cannot be empty")
                    return None
            
            return password
        return None
