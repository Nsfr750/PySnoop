"""
Main Window

This module contains the main application window for the Card Database Manager.
"""
import os
import json
import base64
import traceback
from typing import Dict, Any, Optional

from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QPushButton, 
    QListWidget, QListWidgetItem, QLabel, QLineEdit, QTextEdit, 
    QMessageBox, QFileDialog, QDialog, QMenuBar, QMenu, QSplitter,
    QApplication, QSizePolicy, QStatusBar, QInputDialog, QTextBrowser
)
from PyQt6.QtCore import Qt, QSettings
from PyQt6.QtGui import QAction, QKeySequence, QIcon

# Add the project root to the Python path if not already there
import sys
import os
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from database.enhanced_database import EnhancedCardDatabase
from security.secure_storage import get_secure_storage
from gui.dialogs import PasswordDialog, CardDialog

class MainWindow(QMainWindow):
    """Main application window for the Card Database Manager."""
    
    def __init__(self):
        super().__init__()
        self.db = None
        self.current_file = None
        self.settings = QSettings("CardDB", "CardDatabaseManager")
        self.setup_ui()
    
    def setup_ui(self):
        """Set up the user interface."""
        self.setWindowTitle("Card Database Manager")
        self.setMinimumSize(800, 600)
        
        # Create central widget and layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Main layout with splitter
        splitter = QSplitter(Qt.Orientation.Horizontal)
        
        # Left panel - Card list
        left_panel = QWidget()
        left_layout = QVBoxLayout(left_panel)
        left_layout.setContentsMargins(0, 0, 0, 0)
        
        # Search bar
        search_layout = QHBoxLayout()
        self.search_edit = QLineEdit()
        self.search_edit.setPlaceholderText("Search cards...")
        self.search_edit.textChanged.connect(self.filter_cards)
        search_layout.addWidget(self.search_edit)
        left_layout.addLayout(search_layout)
        
        # Card list
        self.card_list = QListWidget()
        self.card_list.setMinimumWidth(250)
        self.card_list.itemSelectionChanged.connect(self.on_card_selected)
        self.card_list.setSelectionMode(QListWidget.SelectionMode.SingleSelection)
        left_layout.addWidget(self.card_list)
        
        # Add card button
        add_btn = QPushButton("Add Card")
        add_btn.clicked.connect(self.add_card)
        left_layout.addWidget(add_btn)
        
        # Right panel - Card details
        right_panel = QWidget()
        right_layout = QVBoxLayout(right_panel)
        
        # Card details - Using QTextBrowser for better HTML support
        self.details_text = QTextBrowser()
        self.details_text.setReadOnly(True)
        self.details_text.setOpenExternalLinks(True)  # Enable external links
        self.details_text.setStyleSheet("""
            QTextBrowser {
                background-color: white;
                border: 1px solid #d0d0d0;
                border-radius: 4px;
                padding: 10px;
                font-family: Arial, sans-serif;
                font-size: 14px;
            }
            QTextBrowser a {
                color: #0066cc;
                text-decoration: none;
            }
            QTextBrowser a:hover {
                text-decoration: underline;
            }
        """)
        right_layout.addWidget(self.details_text, 1)  # Add stretch to take available space
        
        # Buttons
        btn_layout = QHBoxLayout()
        
        edit_btn = QPushButton("Edit")
        edit_btn.clicked.connect(self.edit_selected_card)
        btn_layout.addWidget(edit_btn)
        
        delete_btn = QPushButton("Delete")
        delete_btn.clicked.connect(self.delete_card)
        btn_layout.addWidget(delete_btn)
        
        right_layout.addLayout(btn_layout)
        
        # Add panels to splitter
        splitter.addWidget(left_panel)
        splitter.addWidget(right_panel)
        # Set initial sizes (width in pixels)
        splitter.setSizes([200, 400])
        
        # Set main layout
        main_layout = QVBoxLayout(central_widget)
        main_layout.addWidget(splitter)
        
        # Create menu bar
        self.create_menus()
        
        # Status bar
        self.statusBar().showMessage("Ready")
        
        # Update UI state
        self.update_ui_state()
    
    def create_menus(self):
        """Create the menu bar."""
        menubar = self.menuBar()
        
        # File menu
        file_menu = menubar.addMenu("&File")
        
        new_action = QAction("&New Database...", self)
        new_action.triggered.connect(self.new_database)
        new_action.setShortcut(QKeySequence.StandardKey.New)
        file_menu.addAction(new_action)
        
        open_action = QAction("&Open...", self)
        open_action.triggered.connect(self.open_database)
        open_action.setShortcut(QKeySequence.StandardKey.Open)
        file_menu.addAction(open_action)
        
        self.save_action = QAction("&Save", self)
        self.save_action.triggered.connect(self.save_database)
        self.save_action.setShortcut(QKeySequence.StandardKey.Save)
        self.save_action.setEnabled(False)
        file_menu.addAction(self.save_action)
        
        save_as_action = QAction("Save &As...", self)
        save_as_action.triggered.connect(self.save_database_as)
        save_as_action.setShortcut(QKeySequence.StandardKey.SaveAs)
        file_menu.addAction(save_as_action)
        
        file_menu.addSeparator()
        
        exit_action = QAction("E&xit", self)
        exit_action.triggered.connect(self.close)
        exit_action.setShortcut(QKeySequence.StandardKey.Quit)
        file_menu.addAction(exit_action)
        
        # Edit menu
        self.edit_menu = menubar.addMenu("&Edit")
        
        add_card_action = QAction("&Add Card", self)
        add_card_action.triggered.connect(self.add_card)
        add_card_action.setShortcut(QKeySequence("Ctrl+N"))
        self.edit_menu.addAction(add_card_action)
        
        edit_card_action = QAction("&Edit Card", self)
        edit_card_action.triggered.connect(self.edit_selected_card)
        edit_card_action.setShortcut(QKeySequence("Ctrl+E"))
        self.edit_menu.addAction(edit_card_action)
        
        delete_card_action = QAction("&Delete Card", self)
        delete_card_action.triggered.connect(self.delete_card)
        delete_card_action.setShortcut(QKeySequence("Del"))
        self.edit_menu.addAction(delete_card_action)
        
        # Disable edit menu initially
        self.edit_menu.setEnabled(False)
        
        # Tools menu
        tools_menu = menubar.addMenu("&Tools")
        
        # MSR605 Reader action
        msr605_action = QAction("MSR605 Reader/Writer", self)
        msr605_action.triggered.connect(self.show_msr605_dialog)
        tools_menu.addAction(msr605_action)
        
        tools_menu.addSeparator()
        
        # Settings action
        settings_action = QAction("&Settings", self)
        settings_action.triggered.connect(self.show_settings)
        tools_menu.addAction(settings_action)
        
        # Help menu
        help_menu = menubar.addMenu("&Help")
        
        about_action = QAction("&About", self)
        about_action.triggered.connect(self.show_about)
        help_menu.addAction(about_action)
    
    def show_msr605_dialog(self):
        """Show the MSR605 reader/writer dialog."""
        try:
            from gui.msr605_dialog import MSR605Dialog
            dialog = MSR605Dialog(self)
            dialog.exec()
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to initialize MSR605 dialog: {e}")
    
    def update_ui_state(self, has_db: bool = None):
        """Update the UI state based on whether a database is loaded."""
        if has_db is None:
            has_db = self.db is not None
        
        # Enable/disable menu actions
        for action in self.menuBar().actions():
            if action.text() not in ["&File", "&Help"]:
                action.setEnabled(has_db)
        
        # Enable/disable buttons and search
        self.search_edit.setEnabled(has_db)
        self.card_list.setEnabled(has_db)
        
        # Update window title
        if has_db and self.current_file:
            self.setWindowTitle(f"Card Database Manager - {os.path.basename(self.current_file)}")
        else:
            self.setWindowTitle("Card Database Manager")
    
    def filter_cards(self, select_index: int = -1):
        """
        Filter the card list based on search text.
        
        Args:
            select_index: Optional index to select after refreshing the list
        """
        if not self.db:
            print("No database loaded, cannot filter cards")
            return
        
        print(f"\n--- DEBUG: Filtering cards (select_index={select_index}) ---")
        
        # Store the current search text and selection
        search_text = self.search_edit.text().lower()
        current_selection = self.card_list.currentRow()
        
        print(f"Current search text: '{search_text}'")
        print(f"Current selection: {current_selection}")
        
        # Block signals to prevent multiple selection events
        self.card_list.blockSignals(True)
        
        try:
            # Clear the list and repopulate
            self.card_list.clear()
            
            if not hasattr(self.db, 'cards') or not self.db.cards:
                print("No cards in database")
                return
            
            print(f"Found {len(self.db.cards)} cards in database")
            
            visible_indices = []
            
            for i, card in enumerate(self.db.cards):
                try:
                    # Get decrypted card for searching
                    search_card = card
                    if hasattr(self.db, 'secure_storage') and self.db.secure_storage:
                        search_card = self.db.secure_storage.decrypt_card(card)
                    
                    # Ensure all required fields exist with at least empty strings
                    search_card = {
                        'number': '', 
                        'type': '', 
                        'issuer': '', 
                        'holder_name': '', 
                        'expiration': '', 
                        'notes': '',
                        **search_card  # Override with actual values
                    }
                    
                    # Clean the card number for display (show last 4 digits only)
                    display_number = search_card.get('number', '')
                    if len(display_number) > 4:
                        display_number = '•••• ' + display_number[-4:]
                    
                    # Create display text
                    holder_name = search_card.get('holder_name', '').strip()
                    if not holder_name:
                        holder_name = search_card.get('type', 'Card')
                    
                    display_text = f"{display_number}"
                    if holder_name:
                        display_text += f" - {holder_name}"
                    
                    # Check if card matches search
                    matches_search = (not search_text or
                        search_text in search_card.get('number', '').lower() or
                        search_text in search_card.get('holder_name', '').lower() or
                        search_text in search_card.get('type', '').lower() or
                        search_text in search_card.get('issuer', '').lower() or
                        search_text in search_card.get('notes', '').lower())
                    
                    if matches_search:
                        item = QListWidgetItem(display_text)
                        item.setData(Qt.ItemDataRole.UserRole, i)
                        self.card_list.addItem(item)
                        visible_indices.append(i)
                        
                except Exception as e:
                    print(f"Error processing card {i}: {str(e)}")
                    import traceback
                    traceback.print_exc()
            
            # Select the appropriate item
            if select_index >= 0 and select_index < len(self.db.cards):
                # Find the item with the matching index
                for row in range(self.card_list.count()):
                    item = self.card_list.item(row)
                    if item.data(Qt.ItemDataRole.UserRole) == select_index:
                        self.card_list.setCurrentRow(row)
                        print(f"Selected item at row {row} (index {select_index})")
                        break
            elif self.card_list.count() > 0:
                # Select the first item by default if nothing is selected
                if current_selection < 0 or current_selection >= self.card_list.count():
                    self.card_list.setCurrentRow(0)
                    print("Selected first item by default")
            
            print(f"Visible cards: {len(visible_indices)}/{len(self.db.cards)}")
            
        finally:
            # Always unblock signals
            self.card_list.blockSignals(False)
            
        # Force update the details if we have a selection
        current_row = self.card_list.currentRow()
        if current_row >= 0:
            self.on_card_selected()
    
    def on_card_selected(self):
        """Handle card selection change."""
        print("\n--- DEBUG: on_card_selected called ---")
        current_item = self.card_list.currentItem()
        if current_item:
            index = current_item.data(Qt.ItemDataRole.UserRole)
            print(f"Selected card index: {index}")
            if index is not None and 0 <= index < len(self.db.cards):
                self.show_card_details(index)
            else:
                print(f"Invalid card index: {index}")
                self.details_text.clear()
        else:
            print("No item selected")
            self.details_text.clear()
    
    def show_card_details(self, index: int):
        """Show details for the selected card."""
        if not self.db or index < 0 or index >= len(self.db.cards):
            self.details_text.clear()
            print("Error: Invalid index or no database")
            return
        
        try:
            print(f"\n--- DEBUG: Showing card at index {index} ---")
            
            # Get the card data
            card = self.db.cards[index]
            print(f"Raw card data from DB: {card}")
            
            # Decrypt if needed
            if hasattr(self.db, 'secure_storage') and self.db.secure_storage:
                print("Decrypting card data...")
                card = self.db.secure_storage.decrypt_card(card)
                print(f"Decrypted card data: {card}")
            
            # Debug output all card keys and values
            print("\nCard data keys and values:")
            for key, value in card.items():
                print(f"  {key}: {value} (type: {type(value).__name__})")
            
            # Ensure all fields exist with default values
            default_card = {
                'number': '', 
                'type': 'Unknown', 
                'issuer': 'Unknown', 
                'holder_name': '', 
                'expiration': '',
                'expiration_date': '',
                'cvv': '',
                'notes': ''
            }
            
            # Create a new card with default values and update with actual values
            card = {**default_card, **card}
            
            print("\nMerged card data:")
            for key, value in card.items():
                print(f"  {key}: {value} (type: {type(value).__name__})")
            
            # Format the card number for display (show last 4 digits only)
            display_number = card.get('number', '')
            if display_number and len(display_number) > 4:
                masked = '•' * (len(display_number) - 4)
                display_number = masked + display_number[-4:]
            
            # Use expiration_date if expiration is not available
            expiration = card.get('expiration') or card.get('expiration_date', '')
                
            # Format the card details with better styling using format_map to avoid CSS conflicts
            template = """
            <html>
            <head>
            <style>
                body {{
                    font-family: Arial, sans-serif;
                    font-size: 14px;
                    margin: 0;
                    padding: 10px;
                    color: #333;
                }}
                .card-details {{ 
                    max-width: 600px;
                    margin: 0 auto;
                }}
                .card-details h2 {{
                    color: #2c3e50;
                    border-bottom: 1px solid #eee;
                    padding-bottom: 8px;
                    margin: 0 0 15px 0;
                    font-size: 18px;
                }}
                .card-details p {{
                    margin: 12px 0;
                    line-height: 1.6;
                    padding: 0;
                }}
                .card-details b {{
                    color: #2c3e50;
                    min-width: 140px;
                    display: inline-block;
                    font-weight: 600;
                }}
                .card-details .notes {{
                    background-color: #f8f9fa;
                    padding: 12px;
                    border-radius: 4px;
                    margin-top: 20px;
                    border-left: 3px solid #3498db;
                }}
                .card-details .notes h3 {{
                    margin: 0 0 10px 0;
                    color: #2c3e50;
                    font-size: 16px;
                }}
                .card-details .value {{
                    color: #34495e;
                }}
                .na {{
                    color: #999;
                    font-style: italic;
                }}
            </style>
            </head>
            <body>
            <div class="card-details">
                <h2>Card Details</h2>
                <p><b>Card Number:</b> <span class="value">{number}</span></p>
                <p><b>Card Type:</b> <span class="value">{card_type}</span></p>
                <p><b>Issuer:</b> <span class="value">{issuer}</span></p>
                <p><b>Expiration Date:</b> <span class="value">{expiration}</span></p>
                <p><b>Cardholder Name:</b> <span class="value">{holder_name}</span></p>
                <p><b>CVV:</b> <span class="value">{cvv}</span></p>
                <div class="notes">
                    <h3>Notes</h3>
                    <p>{notes}</p>
                </div>
            </div>
            </body>
            </html>
            """
            
            # Create a dictionary with all the values
            values = {
                'number': display_number or '<span class="na">N/A</span>',
                'card_type': card.get('type', '<span class="na">N/A</span>'),
                'issuer': card.get('issuer', card.get('type', '<span class="na">N/A</span>')),
                'expiration': expiration or '<span class="na">N/A</span>',
                'holder_name': card.get('holder_name', '<span class="na">N/A</span>'),
                'cvv': ('•' * len(str(card.get('cvv', '')))) if card.get('cvv') else '<span class="na">N/A</span>',
                'notes': card.get('notes', '<span class="na">No notes available</span>').replace('\n', '<br>')
            }
            
            # Format the template with the values
            details = template.format_map(values)
            
            # Set the HTML content
            self.details_text.clear()
            self.details_text.setHtml(details)
            
            # Debug: Print the HTML content to console
            print("\n--- DEBUG: HTML Content ---")
            print(details[:500] + "..." if len(details) > 500 else details)
            
            # Force update the UI
            QApplication.processEvents()
            
        except Exception as e:
            error_msg = f"Error displaying card details: {str(e)}"
            print(error_msg)
            import traceback
            traceback.print_exc()
            self.details_text.setPlainText(error_msg)
    
    def add_card(self):
        """Add a new card to the database."""
        if not self.db:
            self.statusBar().showMessage("No database is open")
            return
        
        print("\n--- DEBUG: Starting to add a new card ---")
        dialog = CardDialog(self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            try:
                print("Dialog accepted, getting card data...")
                card_data = dialog.get_card_data()
                print(f"Raw card data from dialog: {card_data}")
                
                # Map the card data to the expected format
                mapped_data = {
                    'number': card_data.get('number', '').replace(' ', ''),  # Remove spaces from card number
                    'type': card_data.get('type', 'Unknown'),
                    'issuer': card_data.get('type', 'Unknown'),  # Use card type as issuer if not specified
                    'holder_name': card_data.get('cardholder_name', ''),
                    'expiration': card_data.get('expiration_date', ''),
                    'cvv': card_data.get('cvv', ''),
                    'notes': card_data.get('notes', '')
                }
                
                print("\nMapped card data for database:")
                for key, value in mapped_data.items():
                    print(f"  {key}: {value} (type: {type(value).__name__})")
                
                print("\nAttempting to add card to database...")
                if self.db.add_card(mapped_data):
                    print("Card added to database successfully")
                    self.statusBar().showMessage("Card added successfully")
                    
                    # Get the index of the newly added card (last in the list)
                    new_card_index = len(self.db.cards) - 1
                    print(f"New card index: {new_card_index}")
                    
                    # Force refresh the card list and select the new card
                    print("Refreshing card list...")
                    self.filter_cards(select_index=new_card_index)
                    
                    # Ensure the card list has focus and the item is selected
                    self.card_list.setFocus()
                    if self.card_list.count() > 0:
                        self.card_list.setCurrentRow(self.card_list.count() - 1)
                        self.on_card_selected()
                    
                    # Auto-save the database if we have a file path
                    if self.current_file:
                        try:
                            print(f"Saving database to {self.current_file}")
                            self.db.save_to_file(self.current_file)
                            self.statusBar().showMessage(f"Database saved to {os.path.basename(self.current_file)}")
                            print("Database saved successfully")
                        except Exception as e:
                            error_msg = f"Failed to save database: {str(e)}"
                            print(error_msg)
                            QMessageBox.warning(self, "Warning", error_msg)
                else:
                    error_msg = "Failed to add card to database (check console for details)"
                    print(error_msg)
                    QMessageBox.warning(self, "Error", error_msg)
                    
            except Exception as e:
                error_msg = f"Unexpected error adding card: {str(e)}"
                print(error_msg)
                import traceback
                traceback.print_exc()
                QMessageBox.critical(self, "Error", error_msg)
        else:
            print("Dialog was cancelled")
    
    def edit_selected_card(self):
        """Edit the currently selected card."""
        selected = self.card_list.currentRow()
        if selected >= 0:
            self.edit_card(self.card_list.currentItem())
    
    def edit_card(self, item):
        """Edit a card."""
        if not self.db or not item:
            return
        
        index = item.data(Qt.ItemDataRole.UserRole)
        if index < 0 or index >= len(self.db.cards):
            return
        
        try:
            # Get the card data
            card = self.db.cards[index]
            
            # Decrypt if needed
            if hasattr(self.db, 'secure_storage') and self.db.secure_storage:
                card = self.db.secure_storage.decrypt_card(card)
            
            # Map the card data to the format expected by the dialog
            dialog_card_data = {
                'cardholder_name': card.get('holder_name', ''),
                'number': card.get('number', ''),
                'expiration_date': card.get('expiration', ''),
                'cvv': card.get('cvv', ''),
                'type': card.get('type', 'Unknown'),
                'issuer': card.get('issuer', card.get('type', 'Unknown')),  # Fallback to type if issuer not set
                'notes': card.get('notes', '')
            }
            
            dialog = CardDialog(self, dialog_card_data)
            if dialog.exec() == QDialog.DialogCode.Accepted:
                new_data = dialog.get_card_data()
                
                # Map the dialog data back to the database format
                mapped_data = {
                    'number': new_data.get('number', '').replace(' ', ''),  # Remove spaces from card number
                    'type': new_data.get('type', 'Unknown'),
                    'issuer': new_data.get('type', 'Unknown'),  # Use card type as issuer if not specified
                    'holder_name': new_data.get('cardholder_name', ''),
                    'expiration': new_data.get('expiration_date', ''),
                    'cvv': new_data.get('cvv', ''),
                    'notes': new_data.get('notes', '')
                }
                
                print(f"Updating card with data: {mapped_data}")  # Debug output
                
                # First try to update the card directly
                if hasattr(self.db, 'update_card'):
                    success = self.db.update_card(index, mapped_data)
                else:
                    # If update_card doesn't exist, remove and re-add the card
                    self.db.cards[index].update(mapped_data)
                    success = True
                
                if success:
                    self.statusBar().showMessage("Card updated successfully")
                    self.filter_cards()  # Refresh the list
                    
                    # Auto-save the database if we have a file path
                    if self.current_file:
                        try:
                            self.db.save_to_file(self.current_file)
                            self.statusBar().showMessage(f"Database saved to {os.path.basename(self.current_file)}")
                        except Exception as e:
                            QMessageBox.warning(self, "Warning", f"Card updated but failed to save database: {str(e)}")
                    
                    # Reselect the item
                    for i in range(self.card_list.count()):
                        if self.card_list.item(i).data(Qt.ItemDataRole.UserRole) == index:
                            self.card_list.setCurrentRow(i)
                            break
                else:
                    QMessageBox.warning(self, "Error", "Failed to update card. Please check the console for more details.")
        except Exception as e:
            error_msg = f"Error editing card: {str(e)}"
            print(error_msg)
            import traceback
            traceback.print_exc()
            QMessageBox.critical(self, "Error", error_msg)
    
    def delete_card(self):
        """Delete the selected card."""
        if not self.db:
            return
            
        selected = self.card_list.currentRow()
        if selected < 0:
            return
            
        index = self.card_list.currentItem().data(Qt.ItemDataRole.UserRole)
        
        # Confirm deletion
        reply = QMessageBox.question(
            self, 'Confirm Deletion',
            'Are you sure you want to delete this card?',
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            if self.db.remove_card(index):
                self.statusBar().showMessage("Card deleted successfully")
                self.filter_cards()  # Refresh the list
                
                # Auto-save the database if we have a file path
                if self.current_file:
                    try:
                        with open(self.current_file, 'wb') as f:
                            f.write(self.db.export_to_bytes())
                        self.statusBar().showMessage(f"Database saved to {os.path.basename(self.current_file)}")
                    except Exception as e:
                        QMessageBox.warning(self, "Warning", f"Card deleted but failed to save database: {str(e)}")
        # Create new database
        try:
            # Initialize the database with the password
            self.db = EnhancedCardDatabase(file_path=file_path, password=password)
            
            # Save the empty database to create the file
            if self.db.save_to_file():
                self.current_file = file_path
                self.statusBar().showMessage("New database created")
                self.update_ui_state(True)
                
                # Clear any existing cards from the UI
                self.card_list.clear()
                self.details_text.clear()
            else:
                QMessageBox.critical(self, "Error", "Failed to create database file")
                
        except Exception as e:
            error_msg = str(e) or "Unknown error occurred"
            QMessageBox.critical(self, "Error", f"Failed to create database: {error_msg}")
            print(f"Error creating database: {error_msg}")
            print("Full traceback:", traceback.format_exc())
    
    def open_database(self):
        """Open an existing database."""
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Open Database",
            "",
            "Card Database (*.cdb);;All Files (*)")
        
        if not file_path:
            return
        
        # Ask for password using the new PasswordDialog
        dialog = PasswordDialog(self)
        password = dialog.get_password()
        
        if not password:  # User cancelled or entered no password
            return
        
        try:
            # Try to load the database with the provided password
            self.db = EnhancedCardDatabase.load_from_file(file_path, password)
            
            if self.db is None:
                QMessageBox.critical(self, "Error", "Failed to open database: Invalid password or corrupted file")
                return
                
            self.current_file = file_path
            self.statusBar().showMessage(f"Database loaded: {os.path.basename(file_path)}")
            self.update_ui_state(True)
            self.filter_cards()  # Load cards into the list
            
        except json.JSONDecodeError as e:
            QMessageBox.critical(self, "Error", f"Invalid database format: {str(e)}")
            self.db = None
        except ValueError as e:
            QMessageBox.critical(self, "Error", f"Failed to open database: {str(e)}")
            self.db = None
        except Exception as e:
            QMessageBox.critical(self, "Error", f"An unexpected error occurred: {str(e)}")
            print(f"Error loading database: {str(e)}")
            import traceback
            traceback.print_exc()
            self.db = None
    
    def new_database(self):
        """Create a new database."""
        # Ask for password using the PasswordDialog with new_db=True
        dialog = PasswordDialog(self, new_db=True)
        password = dialog.get_password()
        
        if not password:  # User cancelled or entered no password
            return False
            
        try:
            # Initialize a new database with the provided password
            self.db = EnhancedCardDatabase()
            self.db.secure_storage = get_secure_storage(password)
            
            # Clear the current file path
            self.current_file = None
            
            # Update UI
            self.statusBar().showMessage("New database created")
            self.update_ui_state(True)
            self.filter_cards()  # Clear the card list
            
            # Prompt to save the new database
            return self.save_database_as()
            
        except Exception as e:
            error_msg = f"Failed to create new database: {str(e)}"
            QMessageBox.critical(self, "Error", error_msg)
            print(f"Error creating new database: {error_msg}")
            import traceback
            traceback.print_exc()
            self.db = None
            return False
    
    def save_database(self):
        """Save the current database.
        
        Returns:
            bool: True if save was successful, False otherwise
        """
        if not self.db:
            QMessageBox.warning(self, "No Database", "No database is currently open.")
            return False
            
        if not self.current_file:
            return self.save_database_as()
            
        try:
            # Show a status message
            self.statusBar().showMessage("Saving database...")
            
            # Save the database to the current file
            success = self.db.save_to_file(self.current_file)
            
            if success:
                msg = f"Database saved to {os.path.basename(self.current_file)}"
                self.statusBar().showMessage(msg)
                print(msg)
                return True
            else:
                error_msg = "Failed to save database. Check console for details."
                self.statusBar().showMessage(error_msg)
                QMessageBox.critical(self, "Error", error_msg)
                return False
                
        except Exception as e:
            error_msg = f"Failed to save database: {str(e)}"
            self.statusBar().showMessage(error_msg)
            QMessageBox.critical(self, "Error", error_msg)
            print(f"Error saving database: {error_msg}")
            import traceback
            traceback.print_exc()
            return False
    
    def save_database_as(self):
        """Save the current database to a new file.
        
        Returns:
            bool: True if save was successful, False otherwise
        """
        if not self.db:
            QMessageBox.warning(self, "No Database", "No database is currently open.")
            return False
            
        # Suggest a default filename if we have a current file
        default_dir = ""
        default_name = ""
        
        if self.current_file:
            default_dir = os.path.dirname(self.current_file)
            default_name = os.path.basename(self.current_file)
        
        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "Save Database As",
            os.path.join(default_dir, default_name) if default_name else "",
            "Card Database (*.cdb);;All Files (*)"
        )
        
        if not file_path:
            return False
            
        # Ensure the file has the .cdb extension
        if not file_path.lower().endswith('.cdb'):
            file_path += '.cdb'
            
        # Check if file exists and ask for confirmation
        if os.path.exists(file_path):
            reply = QMessageBox.question(
                self,
                "Confirm Overwrite",
                f"The file '{os.path.basename(file_path)}' already exists. Overwrite?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                QMessageBox.StandardButton.No
            )
            
            if reply != QMessageBox.StandardButton.Yes:
                return False
            
        try:
            # Show a status message
            self.statusBar().showMessage(f"Saving database to {os.path.basename(file_path)}...")
            
            # Save the database to the new file
            success = self.db.save_to_file(file_path)
            
            if success:
                self.current_file = file_path
                msg = f"Database saved to {os.path.basename(file_path)}"
                self.statusBar().showMessage(msg)
                print(msg)
                return True
            else:
                error_msg = "Failed to save database. Check console for details."
                self.statusBar().showMessage(error_msg)
                QMessageBox.critical(self, "Error", error_msg)
                return False
                
        except Exception as e:
            error_msg = f"Failed to save database: {str(e)}"
            self.statusBar().showMessage(error_msg)
            QMessageBox.critical(self, "Error", error_msg)
            print(f"Error saving database: {error_msg}")
            import traceback
            traceback.print_exc()
            return False
    
    def show_about(self):
        """Show the about dialog."""
        QMessageBox.about(
            self,
            "About Card Database Manager",
            "<h2>Card Database Manager</h2>"
            "<p>Version 1.0.0</p>"
            "<p>A secure application for managing payment card information.</p>"
            "<p>&copy; 2025 Card Database Manager</p>"
        )
    
    def closeEvent(self, event):
        """Handle window close event."""
        # Save window geometry
        self.settings.setValue("geometry", self.saveGeometry())
        
        # Check for unsaved changes
        if self.db and self.db.modified:
            reply = QMessageBox.question(
                self,
                'Save Changes',
                'Do you want to save your changes before exiting?',
                QMessageBox.StandardButton.Save | QMessageBox.StandardButton.Discard | QMessageBox.StandardButton.Cancel,
                QMessageBox.StandardButton.Save
            )
            
            if reply == QMessageBox.StandardButton.Save:
                if not self.save_database():
                    event.ignore()
                    return
            elif reply == QMessageBox.StandardButton.Cancel:
                event.ignore()
                return
        
        event.accept()
