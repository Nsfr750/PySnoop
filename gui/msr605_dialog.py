"""
MSR605 Reader/Writer Dialog

This module provides a dialog for interacting with the MSR605 magnetic stripe card reader/writer.
"""

from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, 
    QTextEdit, QComboBox, QCheckBox, QMessageBox, QFileDialog
)
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QTextCursor

import sys
import os
import time
from typing import Optional, List, Dict, Any

# Add the project root to the Python path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from msr605_reader import MSR605Reader, list_msr605_devices

class MSR605Dialog(QDialog):
    """Dialog for interacting with the MSR605 reader/writer"""
    
    def __init__(self, parent=None):
        """Initialize the MSR605 dialog"""
        super().__init__(parent)
        self.reader = None
        self.timer = QTimer()
        self.timer.timeout.connect(self.check_for_card)
        self.init_ui()
    
    def init_ui(self):
        """Initialize the user interface"""
        self.setWindowTitle("MSR605 Card Reader/Writer")
        self.setMinimumSize(500, 600)
        
        # Main layout
        layout = QVBoxLayout()
        
        # Device selection
        device_layout = QHBoxLayout()
        device_layout.addWidget(QLabel("Device:"))
        self.device_combo = QComboBox()
        self.refresh_devices()
        device_layout.addWidget(self.device_combo, 1)
        
        refresh_btn = QPushButton("Refresh")
        refresh_btn.clicked.connect(self.refresh_devices)
        device_layout.addWidget(refresh_btn)
        
        connect_btn = QPushButton("Connect")
        connect_btn.clicked.connect(self.connect_reader)
        device_layout.addWidget(connect_btn)
        
        layout.addLayout(device_layout)
        
        # Status
        self.status_label = QLabel("Status: Not connected")
        layout.addWidget(self.status_label)
        
        # Tabs or sections for different functions
        self.tabs = QVBoxLayout()
        
        # Read section
        read_group = QVBoxLayout()
        read_group.addWidget(QLabel("<b>Read Card</b>"))
        
        self.track1_check = QCheckBox("Track 1")
        self.track1_check.setChecked(True)
        self.track2_check = QCheckBox("Track 2")
        self.track2_check.setChecked(True)
        self.track3_check = QCheckBox("Track 3")
        
        tracks_layout = QHBoxLayout()
        tracks_layout.addWidget(self.track1_check)
        tracks_layout.addWidget(self.track2_check)
        tracks_layout.addWidget(self.track3_check)
        
        read_group.addLayout(tracks_layout)
        
        read_btn = QPushButton("Read Card")
        read_btn.clicked.connect(self.read_card)
        read_group.addWidget(read_btn)
        
        self.tabs.addLayout(read_group)
        
        # Write section
        write_group = QVBoxLayout()
        write_group.addWidget(QLabel("<b>Write Card</b>"))
        
        self.track1_edit = QTextEdit()
        self.track1_edit.setPlaceholderText("Track 1 data (starts with %)")
        self.track1_edit.setMaximumHeight(60)
        
        self.track2_edit = QTextEdit()
        self.track2_edit.setPlaceholderText("Track 2 data (starts with ;)")
        self.track2_edit.setMaximumHeight(60)
        
        self.track3_edit = QTextEdit()
        self.track3_edit.setPlaceholderText("Track 3 data (starts with ;)")
        self.track3_edit.setMaximumHeight(60)
        
        write_group.addWidget(QLabel("Track 1:"))
        write_group.addWidget(self.track1_edit)
        write_group.addWidget(QLabel("Track 2:"))
        write_group.addWidget(self.track2_edit)
        write_group.addWidget(QLabel("Track 3 (optional):"))
        write_group.addWidget(self.track3_edit)
        
        write_btn = QPushButton("Write Card")
        write_btn.clicked.connect(self.write_card)
        write_group.addWidget(write_btn)
        
        self.tabs.addLayout(write_group)
        
        # Log section
        log_group = QVBoxLayout()
        log_group.addWidget(QLabel("<b>Log</b>"))
        
        self.log_text = QTextEdit()
        self.log_text.setReadOnly(True)
        log_group.addWidget(self.log_text)
        
        clear_log_btn = QPushButton("Clear Log")
        clear_log_btn.clicked.connect(self.clear_log)
        log_group.addWidget(clear_log_btn)
        
        self.tabs.addLayout(log_group)
        
        layout.addLayout(self.tabs)
        
        # Buttons
        button_layout = QHBoxLayout()
        
        close_btn = QPushButton("Close")
        close_btn.clicked.connect(self.close)
        button_layout.addWidget(close_btn)
        
        layout.addLayout(button_layout)
        
        self.setLayout(layout)
        
        # Disable controls until connected
        self.set_controls_enabled(False)
    
    def log_message(self, message: str):
        """Add a message to the log"""
        timestamp = time.strftime("%H:%M:%S", time.localtime())
        self.log_text.append(f"[{timestamp}] {message}")
        self.log_text.moveCursor(QTextCursor.MoveOperation.End)
    
    def clear_log(self):
        """Clear the log"""
        self.log_text.clear()
    
    def refresh_devices(self):
        """Refresh the list of available MSR605 devices"""
        self.device_combo.clear()
        
        try:
            devices = list_msr605_devices()
            if not devices:
                self.device_combo.addItem("No MSR605 devices found")
                self.log_message("No MSR605 devices found")
                return
                
            for i, device in enumerate(devices):
                path = device.get('path', '').decode('utf-8')
                self.device_combo.addItem(f"MSR605 ({path})", path)
                
            self.log_message(f"Found {len(devices)} MSR605 device(s)")
            
        except Exception as e:
            self.log_message(f"Error listing devices: {e}")
    
    def connect_reader(self):
        """Connect to the selected MSR605 device"""
        if self.reader and self.reader.initialized:
            # Disconnect
            self.timer.stop()
            self.reader = None
            self.status_label.setText("Status: Disconnected")
            self.set_controls_enabled(False)
            self.log_message("Disconnected from MSR605")
            return
            
        # Connect
        try:
            device_path = self.device_combo.currentData()
            if not device_path:
                QMessageBox.warning(self, "Error", "No device selected")
                return
                
            self.log_message(f"Connecting to {device_path}...")
            
            self.reader = MSR605Reader(device_path)
            if not self.reader.init_reader():
                raise Exception("Failed to initialize reader")
                
            self.status_label.setText("Status: Connected")
            self.set_controls_enabled(True)
            self.log_message("Connected to MSR605")
            
            # Start polling for card
            self.timer.start(500)  # Check every 500ms
            
        except Exception as e:
            self.log_message(f"Error connecting to MSR605: {e}")
            QMessageBox.critical(self, "Error", f"Failed to connect to MSR605: {e}")
    
    def set_controls_enabled(self, enabled: bool):
        """Enable or disable controls"""
        for i in range(self.tabs.count()):
            widget = self.tabs.itemAt(i).widget()
            if widget:
                widget.setEnabled(enabled)
    
    def check_for_card(self):
        """Check if a card is present and read it if auto-read is enabled"""
        if not self.reader or not self.reader.initialized:
            return
            
        try:
            # Try to read a small amount of data to check for card presence
            # This is a simple check - you might need to adjust based on your reader
            data = self.reader.device.read(64, 100)  # 100ms timeout
            if data:
                # If we got data, try to parse it as a card
                self.process_card_data(data)
                
        except Exception as e:
            self.log_message(f"Error checking for card: {e}")
    
    def read_card(self):
        """Read data from the card"""
        if not self.reader or not self.reader.initialized:
            QMessageBox.warning(self, "Error", "Not connected to MSR605")
            return
            
        try:
            self.log_message("Reading card...")
            
            # Read the card
            card = self.reader.read()
            if not card:
                self.log_message("No card data read")
                return
                
            # Process the tracks
            for track_num in [1, 2, 3]:
                track = card.get_track(track_num)
                if track:
                    data = track.get_chars()
                    self.log_message(f"Track {track_num}: {data}")
                    
                    # Update the corresponding track edit
                    if track_num == 1:
                        self.track1_edit.setPlainText(data)
                    elif track_num == 2:
                        self.track2_edit.setPlainText(data)
                    elif track_num == 3:
                        self.track3_edit.setPlainText(data)
            
            self.log_message("Card read successfully")
            
        except Exception as e:
            self.log_message(f"Error reading card: {e}")
            QMessageBox.critical(self, "Error", f"Failed to read card: {e}")
    
    def write_card(self):
        """Write data to the card"""
        if not self.reader or not self.reader.initialized:
            QMessageBox.warning(self, "Error", "Not connected to MSR605")
            return
            
        try:
            # Get track data from the UI
            track1_data = self.track1_edit.toPlainText().strip()
            track2_data = self.track2_edit.toPlainText().strip()
            track3_data = self.track3_edit.toPlainText().strip()
            
            if not track1_data and not track2_data and not track3_data:
                QMessageBox.warning(self, "Error", "No track data to write")
                return
                
            self.log_message("Preparing to write card...")
            
            # Create a card with the track data
            from card import Card
            from track import Track
            
            card = Card()
            
            if track1_data:
                track = Track(track1_data.encode('ascii'), len(track1_data), 1)
                card.add_track(track)
                self.log_message(f"Will write Track 1: {track1_data}")
                
            if track2_data:
                track = Track(track2_data.encode('ascii'), len(track2_data), 2)
                card.add_track(track)
                self.log_message(f"Will write Track 2: {track2_data}")
                
            if track3_data:
                track = Track(track3_data.encode('ascii'), len(track3_data), 3)
                card.add_track(track)
                self.log_message(f"Will write Track 3: {track3_data}")
            
            # Write the card
            tracks_to_write = []
            if track1_data:
                tracks_to_write.append(1)
            if track2_data:
                tracks_to_write.append(2)
            if track3_data:
                tracks_to_write.append(3)
                
            if not self.reader.write(card, tracks_to_write):
                raise Exception("Write operation failed")
                
            self.log_message("Card written successfully")
            QMessageBox.information(self, "Success", "Card written successfully")
            
        except Exception as e:
            self.log_message(f"Error writing card: {e}")
            QMessageBox.critical(self, "Error", f"Failed to write card: {e}")
    
    def closeEvent(self, event):
        """Handle dialog close event"""
        self.timer.stop()
        if self.reader:
            self.reader = None
        event.accept()
