#!/usr/bin/env python3
"""
Card Database GUI

A modern PyQt6-based GUI for the card database manager.
"""
import sys
import os
from pathlib import Path

from PyQt6.QtWidgets import QApplication

from gui.main_window import MainWindow

def main():
    """Main entry point for the application."""
    app = QApplication(sys.argv)
    
    # Set application style
    app.setStyle('Fusion')
    
    # Create and show the main window
    window = MainWindow()
    window.show()
    
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
