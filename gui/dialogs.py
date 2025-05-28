"""
Dialog Windows

This module contains various dialog windows used in the application.
"""
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QLabel, QLineEdit, QDialogButtonBox,
    QFormLayout, QMessageBox, QComboBox, QTextEdit, QCompleter
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QIcon

class PasswordDialog(QDialog):
    """Dialog for entering password for encrypted databases."""
    
    def __init__(self, parent=None, new_db=False):
        super().__init__(parent)
        self.setWindowTitle("Enter Password")
        self.setModal(True)
        self.setMinimumWidth(300)
        self.new_db = new_db
        self.setup_ui()
    
    def setup_ui(self):
        """Set up the user interface."""
        layout = QVBoxLayout(self)
        
        # Add message
        message = "Enter password to unlock database"
        if self.new_db:
            message = "Set a password for the new database"
        layout.addWidget(QLabel(f"<h3>{message}</h3>"))
        
        # Form layout
        form = QFormLayout()
        
        # Password field
        self.password_edit = QLineEdit()
        self.password_edit.setEchoMode(QLineEdit.EchoMode.Password)
        self.password_edit.setPlaceholderText("Enter password")
        form.addRow("Password:", self.password_edit)
        
        # Confirm password field for new databases
        if self.new_db:
            self.confirm_edit = QLineEdit()
            self.confirm_edit.setEchoMode(QLineEdit.EchoMode.Password)
            self.confirm_edit.setPlaceholderText("Confirm password")
            form.addRow("Confirm:", self.confirm_edit)
        
        layout.addLayout(form)
        
        # Buttons
        button_box = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | 
            QDialogButtonBox.StandardButton.Cancel
        )
        button_box.accepted.connect(self.validate)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)
        
        # Set focus to password field
        self.password_edit.setFocus()
    
    def validate(self):
        """Validate the input before accepting."""
        password = self.password_edit.text().strip()
        
        if not password:
            QMessageBox.warning(self, "Error", "Password cannot be empty.")
            return
            
        if self.new_db and password != self.confirm_edit.text():
            QMessageBox.warning(self, "Error", "Passwords do not match.")
            return
            
        self.accept()
    
    def get_password(self) -> str:
        """Get the entered password."""
        return self.password_edit.text()

class CardDialog(QDialog):
    """Dialog for adding/editing card information."""
    
    def __init__(self, parent=None, card_data: dict = None):
        super().__init__(parent)
        self.setWindowTitle("Edit Card" if card_data else "Add New Card")
        self.setModal(True)
        self.setMinimumSize(500, 400)
        self.card_data = card_data or {}
        self.setup_ui()
    
    def setup_ui(self):
        """Set up the user interface."""
        layout = QVBoxLayout(self)
        
        # Form layout for card details
        form = QFormLayout()
        
        # Card number with auto-detect
        self.number_edit = QLineEdit()
        self.number_edit.setPlaceholderText("Card number (auto-detects type)")
        self.number_edit.textChanged.connect(self._on_card_number_changed)
        form.addRow("Card Number:", self.number_edit)
        
        # Card type with auto-complete
        self.type_combo = QComboBox()
        self.type_combo.setEditable(True)
        self.type_combo.setInsertPolicy(QComboBox.InsertPolicy.NoInsert)
        
        # Set up auto-completion
        completer = QCompleter()
        completer.setCaseSensitivity(Qt.CaseSensitivity.CaseInsensitive)
        self.type_combo.setCompleter(completer)
        
        # Add card types
        card_types = ["Visa", "Mastercard", "American Express", 
                     "Discover", "JCB", "Diners Club", "Other"]
        self.type_combo.addItems(card_types)
        form.addRow("Card Type:", self.type_combo)
        
        # Issuer (read-only)
        self.issuer_edit = QLineEdit()
        self.issuer_edit.setReadOnly(True)
        self.issuer_edit.setPlaceholderText("Auto-detected from card number")
        form.addRow("Issuer:", self.issuer_edit)
        
        # Expiration
        self.expiry_edit = QLineEdit()
        self.expiry_edit.setPlaceholderText("MM/YY")
        form.addRow("Expiration:", self.expiry_edit)
        
        # Cardholder name
        self.name_edit = QLineEdit()
        self.name_edit.setPlaceholderText("Cardholder Name")
        form.addRow("Cardholder Name:", self.name_edit)
        
        # Notes
        self.notes_edit = QTextEdit()
        self.notes_edit.setPlaceholderText("Additional notes...")
        form.addRow("Notes:", self.notes_edit)
        
        # Load existing data if editing
        if self.card_data:
            self.load_card_data()
        
        # Buttons
        button_box = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | 
            QDialogButtonBox.StandardButton.Cancel
        )
        button_box.accepted.connect(self.validate_and_accept)
        button_box.rejected.connect(self.reject)
        
        # Add widgets to main layout
        layout.addLayout(form)
        layout.addWidget(button_box)
    
    def _on_card_number_changed(self, text):
        """Handle card number changes to auto-detect card type and issuer."""
        try:
            from database.card_utils import card_detector
            
            # Clean the card number (remove non-digits)
            clean_number = ''.join(c for c in text if c.isdigit())
            
            # Only try to detect if we have at least 4 digits
            if len(clean_number) >= 4:
                card_info = card_detector.get_card_type(clean_number)
                
                # Debug output
                print(f"Card number: {clean_number}")
                print(f"Detected card info: {card_info}")
                
                # Update card type if not manually changed
                if not self.type_combo.lineEdit().isModified():
                    # Try to find an exact match first
                    index = self.type_combo.findText(card_info['type'], Qt.MatchFlag.MatchFixedString)
                    if index >= 0:
                        self.type_combo.setCurrentIndex(index)
                    else:
                        # If no exact match, try to find a partial match
                        for i in range(self.type_combo.count()):
                            if card_info['type'].lower() in self.type_combo.itemText(i).lower():
                                self.type_combo.setCurrentIndex(i)
                                break
                
                # Update issuer if we have one
                issuer = card_info.get('issuer', '')
                if issuer and issuer.lower() != 'unknown':
                    self.issuer_edit.setText(issuer)
                else:
                    self.issuer_edit.clear()
            else:
                self.issuer_edit.clear()
                
        except Exception as e:
            print(f"Error detecting card type: {str(e)}")
            import traceback
            traceback.print_exc()
    
    def load_card_data(self):
        """Load card data into the form."""
        self.number_edit.setText(self.card_data.get('number', ''))
        
        # Set card type
        card_type = self.card_data.get('card_type', '')
        if card_type:
            index = self.type_combo.findText(card_type)
            if index >= 0:
                self.type_combo.setCurrentIndex(index)
        
        # Set issuer if available
        if 'issuer' in self.card_data:
            self.issuer_edit.setText(self.card_data['issuer'])
        
        self.expiry_edit.setText(self.card_data.get('expiration', ''))
        self.name_edit.setText(self.card_data.get('holder_name', ''))
        self.notes_edit.setPlainText(self.card_data.get('notes', ''))
    
    def validate_and_accept(self):
        """Validate input before accepting."""
        if not self.number_edit.text().strip():
            QMessageBox.warning(self, "Error", "Card number is required.")
            return
            
        if not self.name_edit.text().strip():
            QMessageBox.warning(self, "Error", "Cardholder name is required.")
            return
            
        self.accept()
    
    def get_card_data(self) -> dict:
        """
        Get the card data from the form.
        
        Returns:
            Dict containing the card data
        """
        # Get the card type from the combo box
        card_type = self.type_combo.currentText().strip()
        
        # If card type is empty but we have an issuer, use that
        if not card_type and self.issuer_edit.text().strip():
            card_type = self.issuer_edit.text().strip()
            
        # If we still don't have a card type, try to detect it from the number
        if not card_type and self.number_edit.text().strip():
            from database.card_utils import card_detector
            clean_number = ''.join(c for c in self.number_edit.text() if c.isdigit())
            if len(clean_number) >= 4:
                card_info = card_detector.get_card_type(clean_number)
                card_type = card_info.get('type', 'Unknown')
        
        # Create the card data dictionary
        card_data = {
            'number': self.number_edit.text().strip(),
            'card_type': card_type,
            'issuer': self.issuer_edit.text().strip(),
            'expiration': self.expiry_edit.text().strip(),
            'holder_name': self.name_edit.text().strip(),
            'notes': self.notes_edit.toPlainText().strip()
        }
        
        # Ensure issuer is set if we have card type but no issuer
        if card_data['card_type'] and not card_data['issuer']:
            card_data['issuer'] = card_data['card_type']
            
        return card_data
