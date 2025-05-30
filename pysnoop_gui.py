"""
PySnoop - GUI Implementation

A modern Tkinter-based GUI for the PySnoop magstripe card reader application.
"""

import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox, filedialog
from typing import Dict, List, Optional, Any, Union
import os
import sys
import queue
import threading
import json
from pathlib import Path
from datetime import datetime
import appdirs
import serial.tools.list_ports

# Import local modules
from about import create_about_tab

# Import core functionality
from card import Card
from reader import load_config, Reader
from database import CardStorage
from ssflags import SSFlags

# Try to import ttkthemes for better looking UI
try:
    from ttkthemes import ThemedStyle
    THEMED_UI = True
except ImportError:
    THEMED_UI = False
    print("Note: ttkthemes not found, using default theme")

class PySnoopGUI(tk.Tk):
    """Main application window for PySnoop GUI."""
    
    def __init__(self):
        """Initialize the application."""
        super().__init__()
        
        self.title("PySnoop")
        self.geometry("1000x700")
        self.minsize(800, 600)
        
        # Initialize flags and state
        self.flags = SSFlags()
        self.reader = None
        self.db = CardStorage()  # Initialize card storage
        self.current_card = None
        self.reader_thread = None
        self.stop_event = threading.Event()
        self.message_queue = queue.Queue()
        
        # Default settings
        self.settings = {
            'window_geometry': '1000x700',
            'theme': 'default',
            'recent_files': [],
            'last_directory': str(Path.home()),
            'msr605_port': None,
            'msr605_baud': 9600,
            'auto_save': True,
            'auto_load': True,
            'check_updates': True,
            'max_recent_files': 10
        }
        
        # Load settings
        self.settings_file = Path(appdirs.user_config_dir('stripe_snoop')) / 'settings.json'
        self._load_settings()
        
        # Apply loaded geometry if available
        if 'window_geometry' in self.settings:
            self.geometry(self.settings['window_geometry'])
        
        # Print HID devices for debugging
        self.print_hid_devices()
        
        # Configure styles
        self._setup_styles()
        
        # Build the UI
        self._create_widgets()
        
        # Start the message pump
        self.after(100, self.process_messages)
        
        # Save settings on window close
        self.protocol("WM_DELETE_WINDOW", self.on_closing)
    
    def print_hid_devices(self):
        """Print all connected HID devices for debugging."""
        try:
            import hid
            print("\n=== Connected HID Devices ===")
            devices = hid.enumerate()
            if not devices:
                print("No HID devices found")
            else:
                for i, device in enumerate(devices, 1):
                    print(f"\nDevice {i}:")
                    for key, value in device.items():
                        if isinstance(value, (str, int, float, bool)) or value is None:
                            print(f"  {key}: {value}")
                        elif isinstance(value, bytes):
                            try:
                                print(f"  {key}: {value.decode('utf-8', errors='replace')}")
                            except:
                                print(f"  {key}: <binary data>")
            print("\n" + "="*50 + "\n")
        except Exception as e:
            print(f"Error listing HID devices: {e}")
    
    def _setup_styles(self):
        """Configure application styles."""
        if THEMED_UI:
            self.style = ThemedStyle(self)
            self.style.set_theme("arc")  # Use a nice theme if available
        else:
            self.style = ttk.Style()
        
        # Configure custom styles
        self.style.configure("Card.TFrame", background="#f5f5f5")
        self.style.configure("Status.TLabel", padding=5, relief=tk.SUNKEN, anchor=tk.W)
        self.style.configure("Title.TLabel", font=('Helvetica', 12, 'bold'))
        self.style.configure("Subtitle.TLabel", font=('Helvetica', 10, 'bold'))
        self.style.map("Accent.TButton",
                      foreground=[('active', 'white'), ('!disabled', 'white')],
                      background=[('active', '#0052cc'), ('!disabled', '#0066ff')])
    
    def _create_widgets(self):
        """Create and arrange all UI widgets."""
        # Main container
        main_container = ttk.Frame(self)
        main_container.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Create notebook for tabs
        self.notebook = ttk.Notebook(main_container)
        self.notebook.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        
        # Create tabs
        self._create_reader_tab()
        self._create_database_tab()
        self._create_settings_tab()
        self._create_about_tab()
        
        # Status bar
        self.status_var = tk.StringVar(value="Ready")
        status_bar = ttk.Label(
            main_container,
            textvariable=self.status_var,
            style="Status.TLabel"
        )
        status_bar.pack(fill=tk.X, pady=(5, 0))
    
    def init_reader(self):
        """Initialize the selected card reader."""
        reader_type = self.reader_var.get()
        com_port = self.com_port_var.get()
        
        if not com_port:
            messagebox.showerror("Error", "Please select a COM port")
            return
            
        try:
            if reader_type == "MSR605":
                from msr605_serial import MSR605Reader
                self.reader = MSR605Reader(com_port=com_port)
                if self.reader.init_reader():
                    messagebox.showinfo("Success", f"Successfully initialized {reader_type} on {com_port}")
                    self.read_btn.config(state=tk.NORMAL)
                    self.stop_btn.config(state=tk.DISABLED)
                else:
                    messagebox.showerror("Error", f"Failed to initialize {reader_type} on {com_port}")
                    self.read_btn.config(state=tk.DISABLED)
                    self.stop_btn.config(state=tk.DISABLED)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to initialize reader: {str(e)}")
            self.read_btn.config(state=tk.DISABLED)
            self.stop_btn.config(state=tk.DISABLED)
    
    def read_card(self):
        """Read data from the card using the initialized reader."""
        if not self.reader or not hasattr(self.reader, 'read'):
            messagebox.showerror("Error", "Reader not properly initialized")
            return
            
        try:
            self.track_text.delete(1.0, tk.END)  # Clear previous data
            self.track_text.insert(tk.END, "Swipe card now...\n")
            self.read_btn.config(state=tk.DISABLED)
            self.stop_btn.config(state=tk.NORMAL)
            
            # Read card data in a separate thread to avoid freezing the UI
            def read_thread():
                try:
                    card_data = self.reader.read()
                    if card_data:
                        self.message_queue.put(('data', card_data))
                    else:
                        self.message_queue.put(('error', "No data read from card"))
                except Exception as e:
                    self.message_queue.put(('error', f"Error reading card: {str(e)}"))
                finally:
                    self.message_queue.put(('done', None))
            
            threading.Thread(target=read_thread, daemon=True).start()
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to read card: {str(e)}")
            self.read_btn.config(state=tk.NORMAL)
            self.stop_btn.config(state=tk.DISABLED)
    
    def stop_reading(self):
        """Stop the current card reading operation."""
        if hasattr(self.reader, 'cancel_read'):
            self.reader.cancel_read()
        self.read_btn.config(state=tk.NORMAL)
        self.stop_btn.config(state=tk.DISABLED)
    
    def _create_reader_tab(self):
        """Create the card reader tab."""
        tab = ttk.Frame(self.notebook)
        self.notebook.add(tab, text="Card Reader")
        
        # Main container with padding
        container = ttk.Frame(tab, padding=10)
        container.pack(fill=tk.BOTH, expand=True)
        
        # Reader controls frame
        ctrl_frame = ttk.LabelFrame(container, text="Reader Controls", padding=10)
        ctrl_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Configure grid weights
        ctrl_frame.columnconfigure(1, weight=1)
        
        # Row 0: Reader selection
        ttk.Label(ctrl_frame, text="Reader:").grid(row=0, column=0, sticky=tk.W, padx=5, pady=5)
        self.reader_var = tk.StringVar()
        self.reader_combo = ttk.Combobox(
            ctrl_frame,
            textvariable=self.reader_var,
            values=["MSR605"],  # Only MSR605 is supported for now
            state="readonly",
            width=15
        )
        self.reader_combo.set("MSR605")  # Default to MSR605
        self.reader_combo.grid(row=0, column=1, sticky=tk.W, padx=5, pady=5)
        
        # Initialize button
        self.init_btn = ttk.Button(
            ctrl_frame,
            text="Initialize Reader",
            command=self.init_reader,
            style="Accent.TButton"
        )
        self.init_btn.grid(row=0, column=2, padx=5, pady=5, sticky=tk.W)
        
        # Row 1: COM port selection
        ttk.Label(ctrl_frame, text="COM Port:").grid(row=1, column=0, sticky=tk.W, padx=5, pady=5)
        
        # COM port selection frame
        com_frame = ttk.Frame(ctrl_frame)
        com_frame.grid(row=1, column=1, columnspan=2, sticky=tk.W+tk.E, pady=5)
        
        # COM port variable and combobox
        self.com_port_var = tk.StringVar()
        
        def get_available_ports():
            """Get a list of available COM ports."""
            ports = []
            try:
                # Try to get detailed port information
                ports = [port.device for port in serial.tools.list_ports.comports()]
                if not ports:  # If no ports found, try alternative method
                    import winreg
                    with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, 'HARDWARE\\DEVICEMAP\\SERIALCOMM') as key:
                        for i in range(1024):
                            try:
                                port = winreg.EnumValue(key, i)[1]
                                if port not in ports:
                                    ports.append(port)
                            except WindowsError:
                                break
            except Exception as e:
                print(f"Error detecting COM ports: {e}")
            return sorted(ports, key=lambda x: int(x[3:]) if x[3:].isdigit() else float('inf'))
        
        # Create COM port dropdown
        self.com_port_combo = ttk.Combobox(
            com_frame,
            textvariable=self.com_port_var,
            values=get_available_ports(),
            state="readonly",
            width=15
        )
        self.com_port_combo.pack(side=tk.LEFT, padx=(0, 5))
        
        # Add refresh button
        def refresh_ports():
            ports = get_available_ports()
            self.com_port_combo['values'] = ports
            if ports and not self.com_port_var.get():
                self.com_port_var.set(ports[0])
        
        refresh_btn = ttk.Button(
            com_frame,
            text="🔄",
            width=3,
            command=refresh_ports
        )
        refresh_btn.pack(side=tk.LEFT)
        
        # Auto-refresh ports on tab open
        refresh_ports()
        
        # Initialize button
        self.init_btn = ttk.Button(
            ctrl_frame,
            text="Initialize Reader",
            command=self.init_reader,
            style="Accent.TButton"
        )
        self.init_btn.grid(row=0, column=3, padx=5, pady=5)
        
        # Read button
        self.read_btn = ttk.Button(
            ctrl_frame,
            text="Read Card",
            command=self.read_card,
            state=tk.DISABLED
        )
        self.read_btn.grid(row=0, column=4, padx=5, pady=5)
        
        # Stop button
        self.stop_btn = ttk.Button(
            ctrl_frame,
            text="Stop",
            command=self.stop_reading,
            state=tk.DISABLED
        )
        self.stop_btn.grid(row=0, column=5, padx=5, pady=5)
        
        # Card display area
        card_frame = ttk.LabelFrame(container, text="Card Data", padding=10)
        card_frame.pack(fill=tk.BOTH, expand=True)
        
        # Track data display
        self.track_text = scrolledtext.ScrolledText(
            card_frame,
            wrap=tk.WORD,
            width=80,
            height=20,
            font=('Consolas', 10)
        )
        self.track_text.pack(fill=tk.BOTH, expand=True)
        
        # Card info frame
        info_frame = ttk.Frame(card_frame)
        info_frame.pack(fill=tk.X, pady=(10, 0))
        
        # Card type
        ttk.Label(info_frame, text="Card Type:").pack(side=tk.LEFT, padx=(0, 10))
        self.card_type_var = tk.StringVar(value="Unknown")
        ttk.Label(info_frame, textvariable=self.card_type_var, font=('Arial', 10, 'bold')).pack(side=tk.LEFT)
        
        # Card number
        ttk.Label(info_frame, text="Number:", padding=(20, 0, 0, 0)).pack(side=tk.LEFT)
        self.card_number_var = tk.StringVar()
        ttk.Label(info_frame, textvariable=self.card_number_var, font=('Arial', 10, 'bold')).pack(side=tk.LEFT)
        
        # Card holder
        ttk.Label(info_frame, text="Holder:", padding=(20, 0, 0, 0)).pack(side=tk.LEFT)
        self.card_holder_var = tk.StringVar()
        ttk.Label(info_frame, textvariable=self.card_holder_var, font=('Arial', 10, 'bold')).pack(side=tk.LEFT)
        
        # Expiry date
        ttk.Label(info_frame, text="Expires:", padding=(20, 0, 0, 0)).pack(side=tk.LEFT)
        self.expiry_var = tk.StringVar()
        ttk.Label(info_frame, textvariable=self.expiry_var, font=('Arial', 10, 'bold')).pack(side=tk.LEFT)
        
        # Save button frame
        button_frame = ttk.Frame(card_frame)
        button_frame.pack(fill=tk.X, pady=(10, 0))
        
        # Save button
        self.save_btn = ttk.Button(
            button_frame,
            text="Save to Database",
            command=self._save_card_data,
            state=tk.DISABLED
        )
        self.save_btn.pack(side=tk.RIGHT)
    
    def browse_database(self):
        """Open a file dialog to select a database file."""
        initial_dir = self.settings.get('last_directory', str(Path.home()))
        file_path = filedialog.askopenfilename(
            title="Select Database File",
            filetypes=[("SQLite Database", "*.db"), ("JSON Database", "*.json"), ("All Files", "*.*")],
            initialdir=initial_dir
        )
        if file_path:
            self.db_path_var.set(file_path)
            self.settings['last_directory'] = str(Path(file_path).parent)
            self.save_settings()
    
    def _populate_card_list(self):
        """Populate the card list with data from the database."""
        if not hasattr(self, 'card_list'):
            return False  # Card list widget not initialized yet
            
        try:
            # Clear existing items
            self.card_list.delete(*self.card_list.get_children())
            
            # Add cards to the list
            for idx, card in enumerate(self.db.get_all_cards()):
                card_number = card.get('card_number', '')
                card_holder = card.get('card_holder', 'Unknown')
                timestamp = card.get('timestamp', 'Unknown')
                
                # Format the display text
                display_text = f"Card ending in {card_number[-4:] if card_number else '****'}"
                if card_holder and card_holder != 'Unknown':
                    display_text += f" - {card_holder}"
                display_text += f" ({timestamp.split('T')[0] if 'T' in timestamp else timestamp})"
                
                # Add to the treeview
                self.card_list.insert('', 'end', values=(str(idx), display_text, timestamp))
            return True
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to populate card list: {str(e)}")
            return False
    
    def load_database(self):
        """Load the selected database file."""
        db_path = self.db_path_var.get().strip()
        if not db_path:
            messagebox.showerror("Error", "Please select a database file")
            return
            
        try:
            if db_path.endswith('.json'):
                # Load JSON database
                with open(db_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                # Clear existing data and load new data
                self.db.clear()
                for card in data:
                    self.db.add_card(card)
                
                messagebox.showinfo("Success", f"Successfully loaded {len(data)} cards from {db_path}")
                
                # Refresh the card list
                self._populate_card_list()
                
            else:
                messagebox.showwarning("Not Supported", "Only JSON database files are currently supported")
                
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load database: {str(e)}")
            print(f"Error loading database: {e}")
    
    def _export_cards(self):
        """Export all cards to a file."""
        try:
            # Ask for save location
            file_path = filedialog.asksaveasfilename(
                defaultextension=".json",
                filetypes=[("JSON files", "*.json"), ("All files", "*.*")],
                title="Export Cards"
            )
            
            if not file_path:
                return  # User cancelled
                
            # Get all cards
            cards = self.db.get_all_cards()
            
            # Save to file
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(cards, f, indent=2)
                
            messagebox.showinfo("Success", f"Successfully exported {len(cards)} cards to {file_path}")
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to export cards: {str(e)}")
    
    def _clear_cards(self):
        """Clear all cards from the database."""
        if messagebox.askyesno(
            "Confirm Clear",
            "Are you sure you want to delete all cards? This action cannot be undone."
        ):
            try:
                self.db.clear()
                self._populate_card_list()
                messagebox.showinfo("Success", "All cards have been deleted.")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to clear cards: {str(e)}")
        
    def _create_database_tab(self):
        """Create the database management tab."""
        tab = ttk.Frame(self.notebook)
        self.notebook.add(tab, text="Database")
        
        # Main container
        container = ttk.Frame(tab, padding=10)
        container.pack(fill=tk.BOTH, expand=True)
        
        # Database controls frame
        ctrl_frame = ttk.LabelFrame(container, text="Database Controls", padding=10)
        ctrl_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Buttons frame
        btn_frame = ttk.Frame(ctrl_frame)
        btn_frame.pack(fill=tk.X, pady=5)
        
        # Load button
        load_btn = ttk.Button(
            btn_frame,
            text="Load Cards...",
            command=self.load_database
        )
        load_btn.pack(side=tk.LEFT, padx=5)
        
        # Export button
        export_btn = ttk.Button(
            btn_frame,
            text="Export Cards...",
            command=self._export_cards
        )
        export_btn.pack(side=tk.LEFT, padx=5)
        
        # Clear button
        clear_btn = ttk.Button(
            btn_frame,
            text="Clear All",
            command=self._clear_cards,
            style="Danger.TButton"
        )
        clear_btn.pack(side=tk.RIGHT, padx=5)
        
        # Card list frame
        list_frame = ttk.LabelFrame(container, text="Stored Cards", padding=10)
        list_frame.pack(fill=tk.BOTH, expand=True)
        
        # Create treeview with scrollbars
        tree_scroll = ttk.Scrollbar(list_frame)
        tree_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Create the card list treeview
        columns = ('id', 'card_info', 'timestamp')
        self.card_list = ttk.Treeview(
            list_frame,
            columns=columns,
            show='headings',
            yscrollcommand=tree_scroll.set,
            selectmode='browse'
        )
        
        # Configure the scrollbar
        tree_scroll.config(command=self.card_list.yview)
        
        # Define columns
        self.card_list.heading('id', text='ID')
        self.card_list.heading('card_info', text='Card Information')
        self.card_list.heading('timestamp', text='Date Added')
        
        # Set column widths
        self.card_list.column('id', width=50, anchor=tk.CENTER, stretch=tk.NO)
        self.card_list.column('card_info', width=300, anchor=tk.W)
        self.card_list.column('timestamp', width=150, anchor=tk.W, stretch=tk.NO)
        
        # Pack the treeview
        self.card_list.pack(fill=tk.BOTH, expand=True)
        
        # Bind selection event
        self.card_list.bind('<<TreeviewSelect>>', self.on_card_select)
        
        # Card details frame
        details_frame = ttk.LabelFrame(container, text="Card Details", padding=10)
        details_frame.pack(fill=tk.BOTH, expand=True, pady=(10, 0))
        
        # Card details text area
        self.card_details = scrolledtext.ScrolledText(
            details_frame,
            wrap=tk.WORD,
            width=80,
            height=10,
            font=('Consolas', 9)
        )
        self.card_details.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Bind selection event is already set above with self.card_list
        # Remove duplicate binding
    
    def on_card_select(self, event):
        """Handle card selection in the database view."""
        if not hasattr(self, 'card_list') or not hasattr(self, 'card_details'):
            return
            
        selected = self.card_list.selection()
        if not selected:
            return
            
        try:
            # Get the selected item
            item = self.card_list.item(selected[0])
            item_values = item['values']
            if not item_values or len(item_values) < 3:
                return
                
            # Get the card index
            card_index = int(item_values[0])
            
            # Get all cards and find the selected one
            cards = self.db.get_all_cards()
            if card_index < 0 or card_index >= len(cards):
                return
                
            card = cards[card_index]
            
            # Display card details
            self.card_details.delete(1.0, tk.END)
            
            # Basic card info
            self.card_details.insert(tk.END, "=== Card Details ===\n\n")
            
            # Card number
            card_number = card.get('card_number', '')
            if card_number:
                self.card_details.insert(tk.END, f"Number: {card_number}\n")
            
            # Card holder
            card_holder = card.get('card_holder', '')
            if card_holder:
                self.card_details.insert(tk.END, f"Holder: {card_holder}\n")
            
            # Expiration
            expiry = card.get('expiry', '')
            if expiry:
                self.card_details.insert(tk.END, f"Expires: {expiry}\n")
            
            # Timestamp
            timestamp = card.get('timestamp', '')
            if timestamp:
                self.card_details.insert(tk.END, f"Added: {timestamp}\n")
            
            # Track data
            self.card_details.insert(tk.END, "\n=== Track Data ===\n\n")
            
            # Track 1
            track1 = card.get('track1', '')
            if track1:
                self.card_details.insert(tk.END, f"Track 1: {track1}\n\n")
            
            # Track 2
            track2 = card.get('track2', '')
            if track2:
                self.card_details.insert(tk.END, f"Track 2: {track2}\n\n")
            
            # Track 3
            track3 = card.get('track3', '')
            if track3:
                self.card_details.insert(tk.END, f"Track 3: {track3}\n\n")
            
        except Exception as e:
            print(f"Error displaying card details: {e}")
            self.card_details.delete(1.0, tk.END)
            self.card_details.insert(tk.END, f"Error loading card details: {str(e)}")
    
    def _create_about_tab(self):
        """Create the about tab with application information."""
        tab = create_about_tab(self.notebook)
        self.notebook.add(tab, text="About")
    
    def _create_settings_tab(self):
        """Create the settings tab."""
        tab = ttk.Frame(self.notebook)
        self.notebook.add(tab, text="Settings")
        
        # Main container with padding and scrolling
        container = ttk.Frame(tab)
        container.pack(fill=tk.BOTH, expand=True)
        
        # Canvas and scrollbar for scrolling content
        canvas = tk.Canvas(container)
        scrollbar = ttk.Scrollbar(container, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        # Pack the canvas and scrollbar
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Settings content
        content = ttk.Frame(scrollable_frame, padding=20)
        content.pack(fill=tk.BOTH, expand=True)
        
        # Appearance section
        ttk.Label(
            content,
            text="Appearance",
            font=('Helvetica', 12, 'bold')
        ).pack(anchor=tk.W, pady=(0, 10))
        
        # Theme selection
        theme_frame = ttk.Frame(content)
        theme_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(theme_frame, text="Theme:").pack(side=tk.LEFT, padx=(0, 10))
        
        self.theme_var = tk.StringVar(value=self.settings.get('theme', 'default'))
        theme_combo = ttk.Combobox(
            theme_frame,
            textvariable=self.theme_var,
            values=["default", "light", "dark", "classic"],
            state="readonly",
            width=15
        )
        theme_combo.pack(side=tk.LEFT)
        
        # Application section
        ttk.Label(
            content,
            text="Application",
            font=('Helvetica', 12, 'bold')
        ).pack(anchor=tk.W, pady=(20, 10))
        
        # Auto-save settings
        auto_save_frame = ttk.Frame(content)
        auto_save_frame.pack(fill=tk.X, pady=5)
        
        self.auto_save_var = tk.BooleanVar(value=self.settings.get('auto_save', True))
        auto_save_cb = ttk.Checkbutton(
            auto_save_frame,
            text="Auto-save settings on exit",
            variable=self.auto_save_var
        )
        auto_save_cb.pack(anchor=tk.W)
        
        # Auto-load last file
        auto_load_frame = ttk.Frame(content)
        auto_load_frame.pack(fill=tk.X, pady=5)
        
        self.auto_load_var = tk.BooleanVar(value=self.settings.get('auto_load', True))
        auto_load_cb = ttk.Checkbutton(
            auto_load_frame,
            text="Auto-load last opened file",
            variable=self.auto_load_var
        )
        auto_load_cb.pack(anchor=tk.W)
        
        # Check for updates
        update_frame = ttk.Frame(content)
        update_frame.pack(fill=tk.X, pady=5)
        
        self.check_updates_var = tk.BooleanVar(value=self.settings.get('check_updates', True))
        update_cb = ttk.Checkbutton(
            update_frame,
            text="Check for updates on startup",
            variable=self.check_updates_var
        )
        update_cb.pack(anchor=tk.W)
        
        # MSR605 Settings
        ttk.Label(
            content,
            text="MSR605 Reader",
            font=('Helvetica', 12, 'bold')
        ).pack(anchor=tk.W, pady=(20, 10))
        
        # COM Port
        port_frame = ttk.Frame(content)
        port_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(port_frame, text="Default COM Port:").pack(side=tk.LEFT, padx=(0, 10))
        
        self.port_var = tk.StringVar(value=self.settings.get('msr605_port', ''))
        port_entry = ttk.Entry(port_frame, textvariable=self.port_var, width=15)
        port_entry.pack(side=tk.LEFT)
        
        # Baud Rate
        baud_frame = ttk.Frame(content)
        baud_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(baud_frame, text="Baud Rate:").pack(side=tk.LEFT, padx=(0, 10))
        
        self.baud_var = tk.StringVar(value=str(self.settings.get('msr605_baud', 9600)))
        baud_combo = ttk.Combobox(
            baud_frame,
            textvariable=self.baud_var,
            values=["9600", "19200", "38400", "57600", "115200"],
            state="readonly",
            width=10
        )
        baud_combo.pack(side=tk.LEFT)
        
        # Save settings button
        btn_frame = ttk.Frame(content)
        btn_frame.pack(fill=tk.X, pady=(20, 0))
        
        # Reset to defaults button
        reset_btn = ttk.Button(
            btn_frame,
            text="Reset to Defaults",
            command=self._reset_settings
        )
        reset_btn.pack(side=tk.LEFT)
        
        # Save button
        save_btn = ttk.Button(
            btn_frame,
            text="Save Settings",
            command=self.save_settings,
            style="Accent.TButton"
        )
        save_btn.pack(side=tk.RIGHT, padx=(10, 0))
        
    def _load_settings(self):
        """Load settings from file."""
        try:
            if self.settings_file.exists():
                with open(self.settings_file, 'r') as f:
                    loaded_settings = json.load(f)
                    self.settings.update(loaded_settings)
                    
                    # Update window geometry if it was saved
                    if 'window_geometry' in self.settings:
                        self.geometry(self.settings['window_geometry'])
                        
        except Exception as e:
            print(f"Error loading settings: {e}")
            # If there's an error, continue with default settings
    
    def save_settings(self):
        """Save current settings to file."""
        try:
            # Update settings dictionary with current values
            self.settings.update({
                'window_geometry': self.geometry(),
                'theme': self.theme_var.get(),
                'msr605_port': self.port_var.get(),
                'msr605_baud': int(self.baud_var.get()),
                'auto_save': self.auto_save_var.get(),
                'auto_load': self.auto_load_var.get(),
                'check_updates': self.check_updates_var.get(),
                'last_directory': self.settings.get('last_directory', str(Path.home()))
            })
            
            # Ensure the settings directory exists
            self.settings_file.parent.mkdir(parents=True, exist_ok=True)
            
            # Save to file
            with open(self.settings_file, 'w') as f:
                json.dump(self.settings, f, indent=4)
                
            messagebox.showinfo("Settings", "Settings saved successfully!")
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save settings: {e}")
    
    def _reset_settings(self):
        """Reset settings to default values."""
        if messagebox.askyesno(
            "Reset Settings",
            "Are you sure you want to reset all settings to default values?"
        ):
            # Reset to default values
            self.theme_var.set('default')
            self.port_var.set('')
            self.baud_var.set('9600')
            self.auto_save_var.set(True)
            self.auto_load_var.set(True)
            self.check_updates_var.set(True)
            
            # Save the reset settings
            self.save_settings()
    
    def update_recent_files(self, file_path: Union[str, Path]):
        """Update the list of recently opened files."""
        if isinstance(file_path, Path):
            file_path = str(file_path)
            
        if 'recent_files' not in self.settings:
            self.settings['recent_files'] = []
            
        # Remove if already in the list
        if file_path in self.settings['recent_files']:
            self.settings['recent_files'].remove(file_path)
            
        # Add to the beginning of the list
        self.settings['recent_files'].insert(0, file_path)
        
        # Keep only the most recent files
        max_files = self.settings.get('max_recent_files', 10)
        self.settings['recent_files'] = self.settings['recent_files'][:max_files]
        
        # Save the updated settings
        self.save_settings()
    
    def process_messages(self):
        """Process messages from the message queue."""
        try:
            while True:
                try:
                    # Get message from queue (non-blocking)
                    msg_type, data = self.message_queue.get_nowait()
                    
                    if msg_type == 'data':
                        # Handle card data
                        self._handle_card_data(data)
                    elif msg_type == 'error':
                        # Handle error message
                        messagebox.showerror("Error", data)
                    elif msg_type == 'done':
                        # Reading operation completed
                        self.read_btn.config(state=tk.NORMAL)
                        self.stop_btn.config(state=tk.DISABLED)
                        
                except queue.Empty:
                    break
                    
        except Exception as e:
            messagebox.showerror("Error", f"Error processing messages: {str(e)}")
            
        # Schedule the next check
        self.after(100, self.process_messages)
    
    def _save_card_data(self):
        """Save the current card data to the database."""
        if not hasattr(self, 'current_card') or not self.current_card:
            messagebox.showerror("Error", "No card data to save")
            return
            
        try:
            # Create a new card object with all available data
            card_data = {
                'track1': self.current_card.get('track1', ''),
                'track2': self.current_card.get('track2', ''),
                'track3': self.current_card.get('track3', ''),
                'card_number': self.current_card.get('card_number', ''),
                'card_holder': self.current_card.get('card_holder', ''),
                'expiry': self.current_card.get('expiry', ''),
                'timestamp': datetime.now().isoformat()
            }
            
            # Add the card to the database
            self.db.add_card(card_data)
            
            # Update the card list
            if hasattr(self, '_populate_card_list'):
                self._populate_card_list()
            
            # Disable the save button if it exists
            if hasattr(self, 'save_btn'):
                self.save_btn.config(state=tk.DISABLED)
            
            messagebox.showinfo("Success", "Card data saved to database")
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save card data: {str(e)}")
            print(f"Error saving card data: {e}")
    
    def _handle_card_data(self, card_data):
        """Handle card data received from the reader."""
        try:
            # Store the raw card data
            self.current_card = card_data
            
            # Update the UI with the card data
            if hasattr(self, 'track_text'):
                self.track_text.delete(1.0, tk.END)
                
                # Display track data
                if 'track1' in card_data and card_data['track1']:
                    self.track_text.insert(tk.END, "Track 1: " + card_data['track1'] + "\n\n")
                if 'track2' in card_data and card_data['track2']:
                    self.track_text.insert(tk.END, "Track 2: " + card_data['track2'] + "\n\n")
                if 'track3' in card_data and card_data['track3']:
                    self.track_text.insert(tk.END, "Track 3: " + card_data['track3'] + "\n\n")
            
            # Enable the save button if it exists
            if hasattr(self, 'save_btn'):
                self.save_btn.config(state=tk.NORMAL)
                
            # Parse and display card information
            if 'track1' in card_data and card_data['track1']:
                # Try to parse track 1 data
                try:
                    # Format: %B1234567890123456^CARDHOLDER/NAME^YYMM...
                    track1 = card_data['track1']
                    if track1.startswith('%B'):
                        parts = track1.split('^')
                        if len(parts) >= 3:
                            card_number = parts[0][2:].strip()  # Remove %B
                            name_parts = parts[1].split('/')
                            last_name = name_parts[0].strip()
                            first_name = name_parts[1].strip() if len(name_parts) > 1 else ''
                            exp_date = parts[2][:4]  # YYMM format
                            
                            # Format the expiration date as MM/YY
                            exp_formatted = f"{exp_date[2:4]}/{exp_date[0:2]}"
                            
                            # Update the UI
                            if hasattr(self, 'card_number_var'):
                                self.card_number_var.set(f"**** **** **** {card_number[-4:]}" if len(card_number) > 4 else card_number)
                            if hasattr(self, 'card_holder_var'):
                                self.card_holder_var.set(f"{first_name} {last_name}".strip())
                            if hasattr(self, 'expiry_var'):
                                self.expiry_var.set(exp_formatted)
                except Exception as e:
                    print(f"Error parsing track 1 data: {e}")
            
            # Enable save button if it exists
            if hasattr(self, 'save_btn'):
                self.save_btn.config(state=tk.NORMAL)
            
        except Exception as e:
            messagebox.showerror("Error", f"Error processing card data: {str(e)}")
    
    def on_closing(self):
        """Handle application closing."""
        # Stop any ongoing operations
        self.stop_reading()
        
        # Save settings if auto-save is enabled
        if self.auto_save_var.get():
            try:
                self.save_settings()
            except Exception as e:
                print(f"Error saving settings on exit: {e}")
        
        # Close any open files or connections
        if hasattr(self, 'reader') and self.reader:
            try:
                self.reader.close()
            except Exception as e:
                print(f"Error closing reader: {e}")
        
        # Close the application
        self.destroy()

def main():
    """Main entry point for the application."""
    try:
        app = PySnoopGUI()
        app.title("PySnoop")
        app.protocol("WM_DELETE_WINDOW", app.on_closing)
        app.mainloop()
    except Exception as e:
        messagebox.showerror("Fatal Error", f"An unexpected error occurred: {str(e)}")
        print(f"Fatal error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
