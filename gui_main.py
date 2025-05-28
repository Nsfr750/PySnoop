#!/usr/bin/env python3
"""
Card Database Manager - GUI Application

This is the main entry point for the Card Database Manager GUI application.
It provides a user-friendly interface for managing payment card information
with strong encryption for sensitive data.
"""
import sys
import os
import traceback
import json
import base64
from pathlib import Path

# Add the project root to the Python path
project_root = os.path.dirname(os.path.abspath(__file__))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

print("Python Path:", sys.path)  # Debug: Show Python path

# Import Qt after setting up the path
from PyQt6.QtWidgets import (
    QApplication, QMessageBox, QDialog, QVBoxLayout, QLabel, 
    QLineEdit, QPushButton, QHBoxLayout
)
from PyQt6.QtGui import QIcon
from PyQt6.QtCore import Qt

# Import local modules
from gui.dialogs import PasswordDialog
from database.enhanced_database import EnhancedCardDatabase

def handle_exception(exc_type, exc_value, exc_traceback):
    """Handle uncaught exceptions with a user-friendly message."""
    error_msg = """
    An unexpected error occurred:
    
    Type: {}
    Error: {}
    
    Traceback:
    {}
    
    Python Path: {}
    """.format(
        exc_type.__name__,
        str(exc_value),
        "".join(traceback.format_tb(exc_traceback)),
        sys.path
    )
    
    print(error_msg)  # Print to console
    
    # Show error dialog if possible
    app = QApplication.instance()
    if app is not None:
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Icon.Critical)
        msg.setWindowTitle("Unexpected Error")
        msg.setText("An unexpected error occurred")
        msg.setDetailedText(error_msg)
        msg.setStandardButtons(QMessageBox.StandardButton.Ok)
        msg.exec()
    
    sys.exit(1)

# Set the exception hook
sys.excepthook = handle_exception

def main():
    """Main entry point for the GUI application."""
    try:
        print("Starting Card Database Manager...")  # Debug: App start
        
        # Set up the application
        app = QApplication(sys.argv)
        app.setApplicationName("Card Database Manager")
        app.setApplicationVersion("1.0.0")
        app.setOrganizationName("CardDB")
        
        # Set the application style to a modern look
        app.setStyle('Fusion')
        
        print("Creating main window...")  # Debug: Before creating main window
        
        # Import here to catch import errors properly
        from gui.main_window import MainWindow
        
        # Create and show the main window
        main_window = MainWindow()
        main_window.show()
        
        print("Application started successfully")  # Debug: App started
        
        # Start the application event loop
        sys.exit(app.exec())
        
    except Exception as e:
        print(f"Error in main: {str(e)}")
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()
