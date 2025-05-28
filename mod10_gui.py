#!/usr/bin/env python3
"""
mod10_gui.py - GUI interface for Luhn algorithm validation and generation

A PyQt6-based GUI for the mod10.py module that provides an intuitive interface
for validating and generating credit card numbers using the Luhn algorithm.
"""

import sys
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
                             QLabel, QLineEdit, QPushButton, QGroupBox, QSpinBox,
                             QTextEdit, QMessageBox, QTabWidget)
from PyQt6.QtCore import Qt, QSize
from PyQt6.QtGui import QIcon, QFont, QPalette, QColor

# Import our mod10 functions
from mod10 import mod10_check, generate_credit_card

class Mod10Validator(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Luhn Algorithm Tool")
        self.setMinimumSize(600, 500)
        
        # Set application style
        self.setStyleSheet("""
            QMainWindow {
                background-color: #f0f0f0;
            }
            QGroupBox {
                border: 1px solid #ccc;
                border-radius: 5px;
                margin-top: 10px;
                padding-top: 15px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 3px 0 3px;
            }
            QPushButton {
                background-color: #4a86e8;
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 4px;
                min-width: 100px;
            }
            QPushButton:hover {
                background-color: #3a76d8;
            }
            QPushButton:disabled {
                background-color: #cccccc;
            }
            QLineEdit, QSpinBox, QTextEdit {
                padding: 8px;
                border: 1px solid #ccc;
                border-radius: 4px;
                font-family: monospace;
            }
            QLineEdit:focus, QSpinBox:focus, QTextEdit:focus {
                border: 1px solid #4a86e8;
            }
            .valid {
                color: #2e8b57;
                font-weight: bold;
            }
            .invalid {
                color: #d32f2f;
                font-weight: bold;
            }
        """)
        
        self.init_ui()
    
    def init_ui(self):
        """Initialize the user interface"""
        # Create central widget and main layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        
        # Create tab widget
        tab_widget = QTabWidget()
        main_layout.addWidget(tab_widget)
        
        # Create tabs
        self.setup_validation_tab(tab_widget)
        self.setup_generation_tab(tab_widget)
        self.setup_about_tab(tab_widget)
        
        # Status bar
        self.statusBar().showMessage("Ready")
    
    def setup_validation_tab(self, tab_widget):
        """Set up the validation tab"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # Input group
        input_group = QGroupBox("Credit Card Number")
        input_layout = QVBoxLayout()
        
        self.card_input = QLineEdit()
        self.card_input.setPlaceholderText("Enter credit card number...")
        self.card_input.textChanged.connect(self.on_card_input_changed)
        input_layout.addWidget(self.card_input)
        
        # Format hint
        hint = QLabel("Enter a credit card number to validate it using the Luhn algorithm.")
        hint.setWordWrap(True)
        hint.setStyleSheet("color: #666; font-style: italic;")
        input_layout.addWidget(hint)
        
        input_group.setLayout(input_layout)
        layout.addWidget(input_group)
        
        # Result group
        result_group = QGroupBox("Validation Result")
        result_layout = QVBoxLayout()
        
        self.result_label = QLabel("Enter a credit card number to validate")
        self.result_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.result_label.setMinimumHeight(100)
        
        # Set a larger font for the result
        font = self.result_label.font()
        font.setPointSize(14)
        self.result_label.setFont(font)
        
        result_layout.addWidget(self.result_label)
        result_group.setLayout(result_layout)
        layout.addWidget(result_group)
        
        # Validate button
        self.validate_btn = QPushButton("Validate")
        self.validate_btn.clicked.connect(self.validate_card)
        self.validate_btn.setEnabled(False)
        layout.addWidget(self.validate_btn)
        
        tab_widget.addTab(tab, "Validation")
    
    def setup_generation_tab(self, tab_widget):
        """Set up the generation tab"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # Settings group
        settings_group = QGroupBox("Generation Settings")
        settings_layout = QVBoxLayout()
        
        # Length selection
        length_layout = QHBoxLayout()
        length_label = QLabel("Card Length:")
        self.length_spinbox = QSpinBox()
        self.length_spinbox.setRange(4, 32)
        self.length_spinbox.setValue(16)
        length_layout.addWidget(length_label)
        length_layout.addWidget(self.length_spinbox)
        length_layout.addStretch()
        settings_layout.addLayout(length_layout)
        
        # Prefix (optional)
        prefix_layout = QHBoxLayout()
        prefix_label = QLabel("Prefix (optional):")
        self.prefix_input = QLineEdit()
        self.prefix_input.setPlaceholderText("e.g., 4 for Visa, 5 for Mastercard")
        prefix_layout.addWidget(prefix_label)
        prefix_layout.addWidget(self.prefix_input)
        settings_layout.addLayout(prefix_layout)
        
        settings_group.setLayout(settings_layout)
        layout.addWidget(settings_group)
        
        # Generate button
        self.generate_btn = QPushButton("Generate Card Number")
        self.generate_btn.clicked.connect(self.generate_card)
        layout.addWidget(self.generate_btn)
        
        # Generated card
        self.generated_card_label = QLabel("Generated card will appear here...")
        self.generated_card_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.generated_card_label.setStyleSheet("""
            background-color: #f8f9fa;
            border: 1px solid #dee2e6;
            border-radius: 4px;
            padding: 20px;
            font-family: monospace;
            font-size: 16px;
            margin-top: 10px;
        """)
        layout.addWidget(self.generated_card_label)
        
        # Copy button
        self.copy_btn = QPushButton("Copy to Clipboard")
        self.copy_btn.clicked.connect(self.copy_to_clipboard)
        self.copy_btn.setEnabled(False)
        layout.addWidget(self.copy_btn)
        
        layout.addStretch()
        tab_widget.addTab(tab, "Generation")
    
    def setup_about_tab(self, tab_widget):
        """Set up the about tab"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        
        # App info
        app_info = QLabel("Luhn Algorithm Tool")
        app_info.setStyleSheet("font-size: 18px; font-weight: bold; margin-bottom: 10px;")
        app_info.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(app_info)
        
        # Description
        desc = QLabel(
            "This tool helps you validate and generate credit card numbers "
            "using the Luhn algorithm (mod 10).\n\n"
            "• Use the Validation tab to check if a credit card number is valid.\n"
            "• Use the Generation tab to create valid test credit card numbers.\n\n"
            "Note: This tool is for educational and testing purposes only."
        )
        desc.setWordWrap(True)
        desc.setStyleSheet("margin: 10px 0;")
        layout.addWidget(desc)
        
        # Author info
        author = QLabel("Created by: Acidus (acidus@msblabs.org)")
        author.setStyleSheet("color: #666; margin-top: 20px;")
        author.setAlignment(Qt.AlignmentFlag.AlignRight)
        layout.addWidget(author)
        
        tab_widget.addTab(tab, "About")
    
    def on_card_input_changed(self, text):
        """Handle changes to the card input field"""
        # Only enable validate button if there's text to validate
        self.validate_btn.setEnabled(len(text.strip()) > 0)
    
    def validate_card(self):
        """Validate the entered credit card number"""
        card_number = self.card_input.text().strip()
        
        # Remove any non-digit characters
        card_digits = ''.join(filter(str.isdigit, card_number))
        
        if not card_digits:
            self.show_result("Please enter a valid credit card number", False)
            return
        
        is_valid = mod10_check(card_digits)
        
        # Format the card number with spaces for better readability
        formatted_number = ' '.join([card_digits[i:i+4] for i in range(0, len(card_digits), 4)])
        
        if is_valid:
            self.show_result(f"✓ Valid Credit Card Number\n{formatted_number}", True)
        else:
            self.show_result(f"✗ Invalid Credit Card Number\n{formatted_number}", False)
    
    def show_result(self, message, is_valid):
        """Display the validation result"""
        self.result_label.setText(message)
        
        # Set style based on validity
        if is_valid:
            self.result_label.setStyleSheet("color: #2e8b57; font-weight: bold;")
        else:
            self.result_label.setStyleSheet("color: #d32f2f; font-weight: bold;")
    
    def generate_card(self):
        """Generate a valid credit card number"""
        try:
            length = self.length_spinbox.value()
            prefix = self.prefix_input.text().strip()
            
            # If prefix is provided, adjust the length
            if prefix:
                # Remove any non-digit characters from prefix
                prefix = ''.join(filter(str.isdigit, prefix))
                if not prefix:
                    QMessageBox.warning(self, "Invalid Prefix", "Please enter a valid numeric prefix.")
                    return
                    
                # Ensure the total length is at least 4 digits
                if len(prefix) >= length:
                    QMessageBox.warning(
                        self, 
                        "Invalid Length", 
                        f"Prefix is {len(prefix)} digits, but requested length is only {length}. "
                        f"Please increase the length to at least {len(prefix) + 1}."
                    )
                    return
                
                # Generate the rest of the number
                remaining_length = length - len(prefix) - 1  # -1 for check digit
                random_digits = ''.join(str(random.randint(0, 9)) for _ in range(remaining_length))
                partial_number = prefix + random_digits
                
                # Find the check digit that makes it valid
                for check_digit in range(10):
                    card_number = partial_number + str(check_digit)
                    if mod10_check(card_number):
                        break
            else:
                # No prefix, just generate a random valid number
                card_number = generate_credit_card(length)
            
            # Format with spaces for better readability
            formatted_number = ' '.join([card_number[i:i+4] for i in range(0, len(card_number), 4)])
            self.generated_card_label.setText(formatted_number)
            self.generated_card = card_number
            self.copy_btn.setEnabled(True)
            self.statusBar().showMessage("Card number generated successfully", 3000)
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to generate card number: {str(e)}")
    
    def copy_to_clipboard(self):
        """Copy the generated card number to the clipboard"""
        if hasattr(self, 'generated_card'):
            clipboard = QApplication.clipboard()
            clipboard.setText(self.generated_card)
            self.statusBar().showMessage("Copied to clipboard!", 2000)

def main():
    app = QApplication(sys.argv)
    
    # Set application style
    app.setStyle('Fusion')
    
    # Set application information
    app.setApplicationName("Luhn Algorithm Tool")
    app.setApplicationVersion("1.0")
    app.setOrganizationName("MSB Labs")
    
    window = Mod10Validator()
    window.show()
    
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
