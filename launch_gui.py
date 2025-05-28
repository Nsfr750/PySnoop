#!/usr/bin/env python3
"""
Stripe Snoop Launcher

A simple launcher for the Stripe Snoop application and its utilities.
"""

import sys
import os
import subprocess
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QPushButton, 
    QLabel, QMessageBox, QHBoxLayout
)
from PyQt6.QtCore import Qt, QSize
from PyQt6.QtGui import QIcon, QFont

class LauncherWindow(QMainWindow):
    """Main launcher window for Stripe Snoop applications."""
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Stripe Snoop Launcher")
        self.setMinimumSize(400, 300)
        self.setup_ui()
    
    def setup_ui(self):
        """Set up the user interface."""
        # Create central widget and layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        layout = QVBoxLayout(central_widget)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)
        
        # Title
        title_label = QLabel("Stripe Snoop")
        title_font = QFont()
        title_font.setPointSize(18)
        title_font.setBold(True)
        title_label.setFont(title_font)
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        version_label = QLabel("Version 2.0")
        version_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        # Buttons
        self.main_app_btn = QPushButton("Launch Main Application")
        self.main_app_btn.setMinimumHeight(50)
        self.main_app_btn.clicked.connect(self.launch_main_app)
        
        self.msr605_test_btn = QPushButton("MSR605 Test Utility")
        self.msr605_test_btn.setMinimumHeight(50)
        self.msr605_test_btn.clicked.connect(self.launch_msr605_test)
        
        self.quit_btn = QPushButton("Exit")
        self.quit_btn.setMinimumHeight(40)
        self.quit_btn.clicked.connect(self.close)
        
        # Add widgets to layout
        layout.addStretch(1)
        layout.addWidget(title_label)
        layout.addWidget(version_label)
        layout.addSpacing(20)
        layout.addWidget(self.main_app_btn)
        layout.addWidget(self.msr605_test_btn)
        layout.addStretch(1)
        layout.addWidget(self.quit_btn)
    
    def launch_main_app(self):
        """Launch the main Stripe Snoop application."""
        try:
            if not os.path.exists("gui_main.py"):
                QMessageBox.critical(
                    self, 
                    "File Not Found", 
                    "Could not find gui_main.py. Please make sure you're running from the correct directory."
                )
                return
                
            if sys.platform == 'win32':
                subprocess.Popen([sys.executable, "gui_main.py"], creationflags=subprocess.CREATE_NO_WINDOW)
            else:
                subprocess.Popen([sys.executable, "gui_main.py"])
                
        except Exception as e:
            QMessageBox.critical(
                self, 
                "Error", 
                f"Failed to launch main application: {e}"
            )
    
    def launch_msr605_test(self):
        """Launch the MSR605 test utility."""
        try:
            if not os.path.exists("test_msr605.py"):
                QMessageBox.critical(
                    self, 
                    "File Not Found", 
                    "Could not find test_msr605.py. Please make sure you're running from the correct directory."
                )
                return
                
            if sys.platform == 'win32':
                subprocess.Popen([sys.executable, "test_msr605.py"], creationflags=subprocess.CREATE_NO_WINDOW)
            else:
                subprocess.Popen([sys.executable, "test_msr605.py"])
                
        except Exception as e:
            QMessageBox.critical(
                self, 
                "Error", 
                f"Failed to launch MSR605 test utility: {e}"
            )

def main():
    """Main entry point for the launcher application."""
    app = QApplication(sys.argv)
    
    # Set application style
    app.setStyle('Fusion')
    
    # Create and show the launcher window
    launcher = LauncherWindow()
    launcher.show()
    
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
