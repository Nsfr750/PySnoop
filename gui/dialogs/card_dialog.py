"""
Card Dialog

This module provides a dialog for adding and editing card information.
"""

from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, 
    QComboBox, QDialogButtonBox, QFormLayout, QMessageBox
)
from PyQt6.QtCore import Qt, QDate
from PyQt6.QtGui import QIntValidator

class CardDialog(QDialog):
    """A dialog for adding or editing card information."""
    
    CARD_TYPES = [
        "Visa",
        "Mastercard",
        "American Express",
        "Discover",
        "Other"
    ]
    
    def __init__(self, parent=None, card_data=None):
        """
        Initialize the card dialog.
        
        Args:
            parent: The parent widget
            card_data: Optional dictionary containing card data to edit
        """
        super().__init__(parent)
        self.card_data = card_data or {}
        self.setup_ui()
    
    def setup_ui(self):
        """Initialize the user interface."""
        self.setWindowTitle("Edit Card" if self.card_data else "Add New Card")
        self.setMinimumWidth(400)
        
        layout = QVBoxLayout(self)
        form_layout = QFormLayout()
        
        # Cardholder Name
        self.name_edit = QLineEdit()
        self.name_edit.setPlaceholderText("John Doe")
        form_layout.addRow("Cardholder Name:", self.name_edit)
        
        # Card Number
        self.number_edit = QLineEdit()
        self.number_edit.setPlaceholderText("4111111111111111")
        # Only allow numbers and spaces
        self.number_edit.setInputMask("9999 9999 9999 9999;0")
        form_layout.addRow("Card Number:", self.number_edit)
        
        # Expiration Date
        exp_layout = QHBoxLayout()
        
        self.month_combo = QComboBox()
        self.month_combo.addItems([f"{i:02d}" for i in range(1, 13)])
        exp_layout.addWidget(self.month_combo)
        
        self.year_combo = QComboBox()
        current_year = QDate.currentDate().year()
        self.year_combo.addItems([str(i) for i in range(current_year, current_year + 10)])
        exp_layout.addWidget(self.year_combo)
        
        form_layout.addRow("Expiration (MM/YY):", exp_layout)
        
        # CVV
        self.cvv_edit = QLineEdit()
        self.cvv_edit.setPlaceholderText("123")
        self.cvv_edit.setValidator(QIntValidator(0, 9999))
        self.cvv_edit.setMaxLength(4)
        form_layout.addRow("CVV:", self.cvv_edit)
        
        # Card Type
        self.type_combo = QComboBox()
        self.type_combo.addItems(self.CARD_TYPES)
        form_layout.addRow("Card Type:", self.type_combo)
        
        # Notes
        self.notes_edit = QLineEdit()
        self.notes_edit.setPlaceholderText("Additional notes...")
        form_layout.addRow("Notes:", self.notes_edit)
        
        # Buttons
        button_box = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )
        button_box.accepted.connect(self.validate_and_accept)
        button_box.rejected.connect(self.reject)
        
        # Add layouts to main layout
        layout.addLayout(form_layout)
        layout.addWidget(button_box)
        
        # Populate fields if editing
        if self.card_data:
            self.populate_fields()
    
    def populate_fields(self):
        """Populate the form fields with existing card data."""
        self.name_edit.setText(self.card_data.get('cardholder_name', ''))
        self.number_edit.setText(self.card_data.get('number', ''))
        
        # Set expiration date
        exp_date = self.card_data.get('expiration_date', '')
        if exp_date and len(exp_date) >= 5:  # MM/YY format
            month, year = exp_date.split('/')
            self.month_combo.setCurrentText(month.zfill(2))
            # Find the year in the combo or add it if not present
            year_index = self.year_combo.findText(year)
            if year_index >= 0:
                self.year_combo.setCurrentIndex(year_index)
            else:
                self.year_combo.addItem(year)
                self.year_combo.setCurrentText(year)
        
        self.cvv_edit.setText(self.card_data.get('cvv', ''))
        
        # Set card type
        card_type = self.card_data.get('type', '')
        if card_type:
            type_index = self.type_combo.findText(card_type)
            if type_index >= 0:
                self.type_combo.setCurrentIndex(type_index)
        
        self.notes_edit.setText(self.card_data.get('notes', ''))
    
    def validate_and_accept(self):
        """Validate the form and accept if valid."""
        # Get values
        card_data = self.get_card_data()
        
        # Validate required fields
        if not card_data['cardholder_name'].strip():
            QMessageBox.warning(self, "Validation Error", "Cardholder name is required")
            self.name_edit.setFocus()
            return
            
        if not card_data['number'].replace(' ', '').isdigit() or len(card_data['number'].replace(' ', '')) < 13:
            QMessageBox.warning(self, "Validation Error", "Please enter a valid card number")
            self.number_edit.setFocus()
            return
            
        if not card_data['cvv'].isdigit() or len(card_data['cvv']) < 3:
            QMessageBox.warning(self, "Validation Error", "Please enter a valid CVV")
            self.cvv_edit.setFocus()
            return
        
        # If we get here, the data is valid
        self.card_data = card_data
        self.accept()
    
    def get_card_data(self):
        """
        Get the card data from the form.
        
        Returns:
            dict: A dictionary containing the card data
        """
        return {
            'cardholder_name': self.name_edit.text().strip(),
            'number': self.number_edit.text().strip(),
            'expiration_date': f"{self.month_combo.currentText()}/{self.year_combo.currentText()[-2:]}",
            'cvv': self.cvv_edit.text().strip(),
            'type': self.type_combo.currentText(),
            'notes': self.notes_edit.text().strip()
        }
